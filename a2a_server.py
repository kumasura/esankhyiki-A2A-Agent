"""A2A-compliant server powered by Google ADK for the MoSPI MCP workflow.

Implements the Agent-to-Agent (A2A) protocol:
  - Agent Card:     GET  /.well-known/agent.json
  - JSON-RPC 2.0:   POST /
  - Methods:        tasks/send, tasks/get, tasks/cancel, tasks/sendSubscribe (SSE)
  - Task lifecycle: submitted → working → completed | failed | canceled

Ref: https://google.github.io/A2A/
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from mospi_server import know_about_mospi_api, get_indicators, get_metadata, get_data


# ---------------------------------------------------------------------------
# A2A Data Models
# ---------------------------------------------------------------------------

class TaskState(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class TextPart(BaseModel):
    type: str = "text"
    text: str


class Message(BaseModel):
    role: str                          # "user" | "agent"
    parts: List[TextPart]
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class Artifact(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parts: List[TextPart]
    index: int = 0


class TaskStatus(BaseModel):
    state: TaskState
    message: Optional[Message] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class Task(BaseModel):
    id: str
    sessionId: Optional[str] = None
    status: TaskStatus
    artifacts: List[Artifact] = []
    history: List[Message] = []
    metadata: Dict[str, Any] = {}


class TaskSendParams(BaseModel):
    id: Optional[str] = None
    sessionId: Optional[str] = None
    message: Message
    metadata: Dict[str, Any] = {}


class TaskQueryParams(BaseModel):
    id: str
    historyLength: Optional[int] = None


class TaskCancelParams(BaseModel):
    id: str


# ---------------------------------------------------------------------------
# In-memory task store
# ---------------------------------------------------------------------------

_tasks: Dict[str, Task] = {}


# ---------------------------------------------------------------------------
# Google ADK runner (lazy, created once on startup)
# ---------------------------------------------------------------------------

def _build_adk_runner():
    try:
        from google.adk.agents import Agent
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
    except ImportError as exc:
        raise RuntimeError(
            "google-adk is not installed. Run: pip install -r requirements.txt"
        ) from exc

    instructions = (
        "You are the MoSPI A2A assistant. Always follow the tool workflow exactly: "
        "1_know_about_mospi_api -> 2_get_indicators -> 3_get_metadata -> 4_get_data. "
        "Use returned metadata codes and never guess filters."
    )

    agent = Agent(
        name="mospi_a2a_agent",
        model=os.getenv("ADK_MODEL", "gemini-3.1-flash-lite-preview"),
        instruction=instructions,
        tools=[know_about_mospi_api, get_indicators, get_metadata, get_data],
    )

    app_name = os.getenv("ADK_APP_NAME", "mospi_a2a_server")
    session_service = InMemorySessionService()

    try:
        runner = Runner(app_name=app_name, agent=agent, session_service=session_service)
    except (TypeError, ValueError):
        runner = Runner(agent=agent, session_service=session_service)

    return runner, session_service


# ---------------------------------------------------------------------------
# ADK invocation helper
# ---------------------------------------------------------------------------

async def _run_agent(task: Task, user_text: str) -> str:
    """Run the ADK agent and return the response text.

    google-adk InMemorySessionService requires sessions to be explicitly
    created before run_async is called. We create it here (or reuse if it
    already exists), then iterate the async-generator to collect the final
    model response.
    """
    runner = app.state.runner
    session_service = app.state.session_service
    user_id = "a2a-user"
    session_id = task.sessionId or task.id

    # Create the session if it doesn't already exist
    try:
        existing = await session_service.get_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )
        if existing is None:
            await session_service.create_session(
                app_name=runner.app_name,
                user_id=user_id,
                session_id=session_id,
            )
    except Exception:
        # Some versions raise instead of returning None for missing sessions
        await session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )

    try:
        from google.genai import types as genai_types
        new_message = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=user_text)],
        )
    except ImportError:
        new_message = user_text  # type: ignore

    RETRYABLE = ("429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE")
    for attempt in range(3):
        try:
            final_text = ""
            last_text = ""

            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message,
            ):
                # Strategy 1: explicit is_final_response() marker
                is_final = (
                    hasattr(event, "is_final_response")
                    and callable(event.is_final_response)
                    and event.is_final_response()
                )

                # Extract text from event.content (standard ADK structure)
                text_from_content = ""
                if hasattr(event, "content") and event.content:
                    parts = getattr(event.content, "parts", None) or []
                    for part in parts:
                        t = getattr(part, "text", None)
                        if t:
                            text_from_content += t

                # Extract text from event.response (some ADK versions)
                text_from_response = ""
                resp = getattr(event, "response", None)
                if resp:
                    t = getattr(resp, "text", None)
                    if t:
                        text_from_response = t

                # Prefer content text, fall back to response text
                chunk = text_from_content or text_from_response

                if chunk:
                    last_text = chunk          # always track latest non-empty text
                    if is_final:
                        final_text = chunk     # lock in the final answer
                        break

                elif is_final:
                    # Final event had no text itself — use the last text we saw
                    final_text = last_text
                    break

            # If we never hit a final event, use whatever we accumulated
            return final_text or last_text or "Agent returned no text response."

        except Exception as exc:
            err = str(exc)
            if any(code in err for code in RETRYABLE) and attempt < 2:
                wait = [15, 60][attempt]   # 15s then 60s
                await asyncio.sleep(wait)
                continue
            raise RuntimeError(err) from exc


# ---------------------------------------------------------------------------
# FastAPI lifespan — build runner once, cleanly
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    runner, session_service = _build_adk_runner()
    app.state.runner = runner
    app.state.session_service = session_service
    yield
    app.state.runner = None
    app.state.session_service = None


app = FastAPI(
    title="MoSPI A2A Server",
    version="0.2.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Agent Card — mandatory A2A discovery endpoint
# ---------------------------------------------------------------------------

@app.get("/.well-known/agent.json")
def agent_card() -> Dict[str, Any]:
    """A2A Agent Card: describes this agent's identity and capabilities."""
    base_url = os.getenv("AGENT_BASE_URL", "http://localhost:8080")
    return {
        "name": "MoSPI Statistical Data Agent",
        "description": (
            "AI agent for querying official Indian government statistics from MoSPI: "
            "employment (PLFS), inflation (CPI/WPI), industrial production (IIP), "
            "factory data (ASI), national accounts (NAS), and energy statistics."
        ),
        "url": base_url,
        "version": "0.2.0",
        "documentationUrl": "https://github.com/kumasura/esankhyiki-A2A",
        "provider": {
            "organization": "esankhyiki",
            "url": "https://github.com/kumasura/esankhyiki-A2A",
        },
        "capabilities": {
            "streaming": True,       # tasks/sendSubscribe via SSE
            "pushNotifications": False,
            "stateTransitionHistory": True,
        },
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": [
            {
                "id": "mospi-query",
                "name": "MoSPI Data Query",
                "description": (
                    "Query 7 MoSPI statistical datasets using natural language. "
                    "Follows a strict 4-step tool workflow: "
                    "know_api → get_indicators → get_metadata → get_data."
                ),
                "tags": [
                    "statistics", "india", "government", "GDP", "inflation",
                    "employment", "CPI", "WPI", "IIP", "NAS", "PLFS", "ASI", "energy"
                ],
                "examples": [
                    "What is the unemployment rate in India for 2023?",
                    "Give me CPI inflation data for food group in 2024.",
                    "Show IIP index for manufacturing sector monthly for 2023-24.",
                    "What is India's GDP growth rate for 2022-23?",
                ],
            }
        ],
    }


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# JSON-RPC 2.0 dispatcher — the A2A entry point
# ---------------------------------------------------------------------------

@app.post("/")
async def jsonrpc_handler(request: Request):
    """
    Main A2A endpoint. Accepts JSON-RPC 2.0 requests and dispatches to:
      - tasks/send
      - tasks/get
      - tasks/cancel
      - tasks/sendSubscribe  (returns SSE stream)
    """
    try:
        body = await request.json()
    except Exception:
        return _error_response(None, -32700, "Parse error")

    # Validate JSON-RPC envelope
    if body.get("jsonrpc") != "2.0":
        return _error_response(body.get("id"), -32600, "Invalid Request: jsonrpc must be '2.0'")

    method = body.get("method")
    params = body.get("params", {})
    req_id = body.get("id")

    if method == "tasks/send":
        return await _handle_tasks_send(params, req_id)

    elif method == "tasks/get":
        return await _handle_tasks_get(params, req_id)

    elif method == "tasks/cancel":
        return await _handle_tasks_cancel(params, req_id)

    elif method == "tasks/sendSubscribe":
        # Returns an SSE StreamingResponse — cannot wrap in normal JSONResponse
        return await _handle_tasks_send_subscribe(params, req_id)

    else:
        return _error_response(req_id, -32601, f"Method not found: '{method}'")


# ---------------------------------------------------------------------------
# tasks/send  — submit a task and wait for completion
# ---------------------------------------------------------------------------

async def _handle_tasks_send(params: dict, req_id: Any) -> JSONResponse:
    try:
        send_params = TaskSendParams(**params)
    except Exception as exc:
        return _error_response(req_id, -32602, f"Invalid params: {exc}")

    task_id = send_params.id or str(uuid.uuid4())
    user_text = _extract_text(send_params.message)

    # Create task
    task = Task(
        id=task_id,
        sessionId=send_params.sessionId,
        status=TaskStatus(
            state=TaskState.SUBMITTED,
            message=send_params.message,
        ),
        history=[send_params.message],
        metadata=send_params.metadata,
    )
    _tasks[task_id] = task

    # Transition to working
    task.status = TaskStatus(state=TaskState.WORKING)

    # Run agent
    try:
        response_text = await _run_agent(task, user_text)
        agent_message = Message(
            role="agent",
            parts=[TextPart(text=response_text)],
        )
        task.history.append(agent_message)
        task.status = TaskStatus(
            state=TaskState.COMPLETED,
            message=agent_message,
        )
        task.artifacts = [
            Artifact(
                name="response",
                parts=[TextPart(text=response_text)],
                index=0,
            )
        ]
    except Exception as exc:
        error_message = Message(
            role="agent",
            parts=[TextPart(text=f"Error: {exc}")],
        )
        task.history.append(error_message)
        task.status = TaskStatus(
            state=TaskState.FAILED,
            message=error_message,
        )

    return _success_response(req_id, task.model_dump())


# ---------------------------------------------------------------------------
# tasks/get  — retrieve a task by ID
# ---------------------------------------------------------------------------

async def _handle_tasks_get(params: dict, req_id: Any) -> JSONResponse:
    try:
        query = TaskQueryParams(**params)
    except Exception as exc:
        return _error_response(req_id, -32602, f"Invalid params: {exc}")

    task = _tasks.get(query.id)
    if not task:
        return _error_response(req_id, -32001, f"Task not found: '{query.id}'")

    result = task.model_dump()
    if query.historyLength is not None:
        result["history"] = result["history"][-query.historyLength:]

    return _success_response(req_id, result)


# ---------------------------------------------------------------------------
# tasks/cancel  — cancel a task (only if still working)
# ---------------------------------------------------------------------------

async def _handle_tasks_cancel(params: dict, req_id: Any) -> JSONResponse:
    try:
        cancel_params = TaskCancelParams(**params)
    except Exception as exc:
        return _error_response(req_id, -32602, f"Invalid params: {exc}")

    task = _tasks.get(cancel_params.id)
    if not task:
        return _error_response(req_id, -32001, f"Task not found: '{cancel_params.id}'")

    if task.status.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELED):
        return _error_response(
            req_id, -32002,
            f"Cannot cancel task in state '{task.status.state}'"
        )

    task.status = TaskStatus(state=TaskState.CANCELED)
    return _success_response(req_id, task.model_dump())


# ---------------------------------------------------------------------------
# tasks/sendSubscribe  — streaming SSE response
# ---------------------------------------------------------------------------

async def _handle_tasks_send_subscribe(params: dict, req_id: Any):
    try:
        send_params = TaskSendParams(**params)
    except Exception as exc:
        # Can't return SSE for errors at this stage — return plain JSON
        return _error_response(req_id, -32602, f"Invalid params: {exc}")

    task_id = send_params.id or str(uuid.uuid4())
    user_text = _extract_text(send_params.message)

    task = Task(
        id=task_id,
        sessionId=send_params.sessionId,
        status=TaskStatus(state=TaskState.SUBMITTED, message=send_params.message),
        history=[send_params.message],
        metadata=send_params.metadata,
    )
    _tasks[task_id] = task

    async def event_stream() -> AsyncGenerator[str, None]:
        # Emit submitted
        yield _sse_event(req_id, task, TaskState.SUBMITTED)

        # Emit working
        task.status = TaskStatus(state=TaskState.WORKING)
        yield _sse_event(req_id, task, TaskState.WORKING)

        # Run agent
        try:
            response_text = await _run_agent(task, user_text)
            agent_message = Message(
                role="agent",
                parts=[TextPart(text=response_text)],
            )
            task.history.append(agent_message)
            task.artifacts = [
                Artifact(
                    name="response",
                    parts=[TextPart(text=response_text)],
                    index=0,
                )
            ]
            task.status = TaskStatus(
                state=TaskState.COMPLETED,
                message=agent_message,
            )
            yield _sse_event(req_id, task, TaskState.COMPLETED, final=True)

        except Exception as exc:
            error_message = Message(
                role="agent",
                parts=[TextPart(text=f"Error: {exc}")],
            )
            task.history.append(error_message)
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message=error_message,
            )
            yield _sse_event(req_id, task, TaskState.FAILED, final=True)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_text(message: Message) -> str:
    """Pull plain text from the first text part of a message."""
    for part in message.parts:
        if part.type == "text":
            return part.text
    return ""


def _success_response(req_id: Any, result: Any) -> JSONResponse:
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "result": result,
    })


def _error_response(req_id: Any, code: int, message: str) -> JSONResponse:
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": code, "message": message},
    })


def _sse_event(req_id: Any, task: Task, state: TaskState, final: bool = False) -> str:
    """Format a single SSE event as JSON-RPC 2.0 notification."""
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "id": task.id,
            "status": task.status.model_dump(),
            "artifacts": [a.model_dump() for a in task.artifacts] if final else [],
            "final": final,
        },
    }
    return f"data: {json.dumps(payload)}\n\n"


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))