# MoSPI Intelligence Stack: MCP + A2A Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.0-green.svg)](https://gofastmcp.com)
[![A2A Protocol](https://img.shields.io/badge/A2A-Compliant-blueviolet)](https://google.github.io/A2A/)
[![Google ADK](https://img.shields.io/badge/Google_ADK-Powered-orange)](https://google.github.io/adk-docs/)

An AI agent stack for querying official Indian government statistics from MoSPI. Built on two complementary protocols: **MCP** (Model Context Protocol) (https://github.com/nso-india/esankhyiki-mcp) for tool interoperability, and **A2A** (Agent-to-Agent) for inter-agent communication.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [A2A Agent](#a2a-agent)
  - [Protocol Compliance](#protocol-compliance)
  - [Running the A2A Server](#running-the-a2a-server)
  - [A2A Endpoints](#a2a-endpoints)
  - [Example Requests](#example-requests)
  - [Task Lifecycle](#task-lifecycle)
  - [SSE Streaming](#sse-streaming)
- [MCP Server](#mcp-server)
  - [Datasets](#datasets)
  - [MCP Tools](#mcp-tools)
  - [Agent Workflow](#agent-workflow)
  - [Installation](#installation)
  - [Running the MCP Server](#running-the-mcp-server)
  - [Connecting from an MCP Client](#connecting-from-an-mcp-client)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Resources](#resources)
- [License](#license)

---

## Overview

This project is an **AI agent foundation layer** for official Indian government statistics. It exposes 7 MoSPI statistical datasets through two interoperable protocol layers:

| Layer | Protocol | Purpose |
|-------|----------|---------|
| **Tool Layer** | MCP (FastMCP 3.0) | Structured, validated access to MoSPI APIs via 4 sequential tools |
| **Agent Layer** | A2A (Google ADK) | Full agent-to-agent communication with task lifecycle and SSE streaming |

**Key Features:**
- 7 statistical datasets: employment, inflation, industrial production, GDP, and energy
- Fully A2A-compliant agent with JSON-RPC 2.0, task lifecycle, and SSE streaming
- Agent Card at `/.well-known/agent.json` for automatic agent discovery
- Sequential 4-tool MCP workflow designed to prevent LLM hallucination
- Swagger-driven parameter validation
- Auto-retry on transient Gemini 429/503 errors
- Full OpenTelemetry integration for observability
- Production-ready Docker deployment

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    A2A Clients / Agents                     │
│                 (Other agents, orchestrators)               │
└──────────────────────────┬──────────────────────────────────┘
                           │ JSON-RPC 2.0  (POST /)
                           │ SSE Streaming (tasks/sendSubscribe)
┌──────────────────────────▼──────────────────────────────────┐
│                   a2a_server.py                             │
│              A2A-Compliant Agent Server                     │
│                                                             │
│  /.well-known/agent.json  →  Agent Card (discovery)        │
│  tasks/send               →  Submit + await task           │
│  tasks/get                →  Retrieve task by ID           │
│  tasks/cancel             →  Cancel in-progress task       │
│  tasks/sendSubscribe      →  SSE streaming response        │
│                                                             │
│            Powered by Google ADK Runner                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ Tool calls
┌──────────────────────────▼──────────────────────────────────┐
│                   mospi_server.py                           │
│              FastMCP 3.0 Tool Server                        │
│                                                             │
│  1_know_about_mospi_api  →  Dataset discovery              │
│  2_get_indicators        →  List indicators                 │
│  3_get_metadata          →  Get valid filter values        │
│  4_get_data              →  Fetch data (Swagger-validated) │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────────┐
│              api.mospi.gov.in                               │
│   PLFS  |  CPI  |  IIP  |  ASI  |  NAS  |  WPI  |  ENERGY │
└─────────────────────────────────────────────────────────────┘

mospi-mcp-api/
├── a2a_server.py            # A2A-compliant agent server (Google ADK)
├── test_a2a.ps1             # To test A2A Agent
├── mospi_server.py          # FastMCP server — tools, validation, routing
├── mospi/
│   └── client.py            # MoSPI API HTTP client
├── swagger/                 # Swagger YAML specs (source of truth for params)
├── observability/
│   └── telemetry.py         # OpenTelemetry middleware
├── tests/                   # Per-dataset test files
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## A2A Agent

The A2A server is a fully compliant implementation of the [Agent-to-Agent (A2A) protocol](https://google.github.io/A2A/), powered by **Google ADK**. It wraps the MCP tool chain into a standards-based agent interface that any A2A-compatible client or orchestrator can communicate with.

### Protocol Compliance

| A2A Requirement | Status | Detail |
|----------------|--------|--------|
| Agent Card | ✅ | `GET /.well-known/agent.json` |
| JSON-RPC 2.0 | ✅ | Single `POST /` dispatcher |
| `tasks/send` | ✅ | Submit task, await completion |
| `tasks/get` | ✅ | Retrieve task + history by ID |
| `tasks/cancel` | ✅ | Cancel in-progress tasks |
| `tasks/sendSubscribe` | ✅ | SSE streaming with state events |
| Task lifecycle | ✅ | `submitted → working → completed / failed / canceled` |
| Artifacts | ✅ | Final response wrapped in artifact object |
| State history | ✅ | Full message history per task |

### Running the A2A Server

```bash
# Set your Gemini API key
export GOOGLE_API_KEY=your_key       # Linux/macOS
$env:GOOGLE_API_KEY = "your_key"     # Windows PowerShell

# Optional: override the default model
export ADK_MODEL=gemini-2.0-flash

# Start the server (runs on port 8080)
python a2a_server.py
```

### A2A Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/.well-known/agent.json` | GET | Agent Card — capabilities, skills, version |
| `/health` | GET | Health check |
| `/` | POST | JSON-RPC 2.0 dispatcher for all A2A methods |

### Example Requests

**Discover the agent:**
```bash
curl http://localhost:8080/.well-known/agent.json
```

**Submit a task (`tasks/send`):**
```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-1",
    "method": "tasks/send",
    "params": {
      "id": "task-001",
      "sessionId": "my-session",
      "message": {
        "role": "user",
        "parts": [{ "type": "text", "text": "What is the unemployment rate in India for 2022-23?" }]
      }
    }
  }'
```

**Example response:**
```json
{
  "jsonrpc": "2.0",
  "id": "req-1",
  "result": {
    "id": "task-001",
    "status": {
      "state": "completed",
      "message": {
        "role": "agent",
        "parts": [{ "type": "text", "text": "According to PLFS data for 2022-23, the unemployment rate in India was 3.2% for persons aged 15 years and above." }]
      }
    },
    "artifacts": [
      { "name": "response", "parts": [{ "type": "text", "text": "..." }], "index": 0 }
    ],
    "history": [...]
  }
}
```

**Retrieve a task by ID (`tasks/get`):**
```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-2",
    "method": "tasks/get",
    "params": { "id": "task-001", "historyLength": 5 }
  }'
```

**Stream a task response (`tasks/sendSubscribe`):**
```bash
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-3",
    "method": "tasks/sendSubscribe",
    "params": {
      "id": "task-stream-001",
      "message": {
        "role": "user",
        "parts": [{ "type": "text", "text": "Show IIP manufacturing index for April 2023." }]
      }
    }
  }'
```

### Task Lifecycle

```
  [Client submits task]
         │
         ▼
    ┌─────────┐
    │SUBMITTED│  ← task created, user message stored
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ WORKING │  ← ADK agent running 4-step MCP tool chain
    └────┬────┘
         │
    ┌────┴──────────────┐
    ▼                   ▼
┌─────────┐        ┌────────┐
│COMPLETED│        │ FAILED │  ← error stored in task history
└─────────┘        └────────┘
```

### SSE Streaming

`tasks/sendSubscribe` emits three Server-Sent Events in sequence:

```
data: {"result": {"status": {"state": "submitted"}, "final": false}}

data: {"result": {"status": {"state": "working"}, "final": false}}

data: {"result": {"status": {"state": "completed"}, "artifacts": [...], "final": true}}
```

---

## MCP Server

The MCP server is the data access layer. It exposes 4 tools over the Model Context Protocol that are used by the A2A agent internally, and can also be connected to directly from any MCP client (Claude Desktop, Cursor, etc.).

### Datasets

| Dataset | Full Name | Use For |
|---------|-----------|---------|
| **PLFS** | Periodic Labour Force Survey | Jobs, unemployment, wages, workforce participation |
| **CPI** | Consumer Price Index | Retail inflation, cost of living, commodity prices |
| **IIP** | Index of Industrial Production | Industrial growth, manufacturing output |
| **ASI** | Annual Survey of Industries | Factory performance, industrial employment |
| **NAS** | National Accounts Statistics | GDP, economic growth, national income |
| **WPI** | Wholesale Price Index | Wholesale inflation, producer prices |
| **ENERGY** | Energy Statistics | Energy production, consumption, fuel mix |

### MCP Tools

```
1_know_about_mospi_api  →  2_get_indicators  →  3_get_metadata  →  4_get_data
```

| Step | Tool | Description |
|------|------|-------------|
| 1 | `1_know_about_mospi_api()` | Overview of all 7 datasets. Always the first call. |
| 2 | `2_get_indicators(dataset)` | List available indicators for the chosen dataset. |
| 3 | `3_get_metadata(dataset, ...)` | Get valid filter values and Swagger-validated API parameters. |
| 4 | `4_get_data(dataset, filters)` | Fetch data using filter values returned by step 3. |

> **Important:** Tools must be called in order. Skipping `3_get_metadata` produces invalid filter codes and wrong results.

### Agent Workflow

1. **Understand capability space** via `1_know_about_mospi_api`
2. **Narrow intent to indicators** via `2_get_indicators`
3. **Resolve valid parameters** via `3_get_metadata`
4. **Execute retrieval safely** via `4_get_data`

### Installation

```bash
git clone https://github.com/kumasura/esankhyiki-A2A.git
cd esankhyiki-A2A

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Running the MCP Server

```bash
# HTTP transport (remote/web access) — runs at http://localhost:8000/mcp
python mospi_server.py

# Or via FastMCP CLI
fastmcp run mospi_server.py:mcp --transport http --port 8000

# stdio transport (local MCP clients like Claude Desktop)
fastmcp run mospi_server.py:mcp
```

### Connecting from an MCP Client

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        overview = await client.call_tool("1_know_about_mospi_api", {})
        indicators = await client.call_tool("2_get_indicators", {
            "dataset": "PLFS",
            "user_query": "unemployment rate"
        })
        print(indicators)

asyncio.run(main())
```

---

## Deployment

### Docker

```bash
docker build -t mospi-mcp .
docker run -d -p 8000:8000 -p 8080:8080 --name mospi-server mospi-mcp
```

### Docker Compose

Includes Jaeger for distributed tracing visualization:

```bash
docker-compose up -d
```

Services:
- **MoSPI MCP Server**: http://localhost:8000/mcp
- **MoSPI A2A Server**: http://localhost:8080
- **Jaeger UI**: http://localhost:16686

### FastMCP Cloud

1. Push code to GitHub
2. Sign in to [FastMCP Cloud](https://fastmcp.cloud)
3. Create project with entrypoint `mospi_server.py:mcp`

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key for the A2A agent | *(required)* |
| `ADK_MODEL` | Gemini model to use | `gemini-2.0-flash` |
| `ADK_APP_NAME` | ADK application name | `mospi_a2a_server` |
| `AGENT_BASE_URL` | Public URL of this agent (for Agent Card) | `http://localhost:8080` |
| `PORT` | A2A server port | `8080` |
| `OTEL_SERVICE_NAME` | Service name in traces | `mospi-mcp-server` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | `http://localhost:4317` |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | Protocol (`grpc` or `http/protobuf`) | `grpc` |
| `OTEL_TRACES_EXPORTER` | Exporter type (`otlp`, `console`, `none`) | `otlp` |

See `.env.example` for full configuration options.

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Adding new datasets
- Project structure
- Development setup
- Code style

---

## Resources

- [MoSPI Open APIs](https://api.mospi.gov.in) — Official API documentation and e-Sankhyiki portal
- [Google ADK Documentation](https://google.github.io/adk-docs/) — Agent Development Kit
- [FastMCP Documentation](https://gofastmcp.com) — MCP framework docs
- [Model Context Protocol](https://modelcontextprotocol.io) — MCP specification

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
