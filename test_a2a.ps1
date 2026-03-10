# ============================================================
# A2A Server Test Suite - esankhyiki MoSPI Agent (PowerShell)
# ============================================================
# Prerequisites:
#   pip install -r requirements.txt
#   $env:GOOGLE_API_KEY = "your_key"
#   python a2a_server.py       (runs on port 8080)
#
# Run this script:
#   .\test_a2a.ps1
# ============================================================

$BASE = "http://localhost:8080"

function Section($title) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
}

function Ok($msg)   { Write-Host "[OK] $msg" -ForegroundColor Green }
function Info($msg) { Write-Host "[>>] $msg" -ForegroundColor Yellow }

function Invoke-A2A($body) {
    $json = $body | ConvertTo-Json -Depth 10
    try {
        $response = Invoke-RestMethod -Uri $BASE -Method Post `
            -ContentType "application/json" -Body $json
        $response | ConvertTo-Json -Depth 10
    } catch {
        Write-Host "ERROR: $_" -ForegroundColor Red
    }
}

Section "TEST 1 - Agent Card Discovery"
Info "GET /.well-known/agent.json"
try {
    $card = Invoke-RestMethod -Uri "$BASE/.well-known/agent.json" -Method Get
    $card | ConvertTo-Json -Depth 10
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}
Ok "Should show agent name, skills, streaming true"

Section "TEST 2 - Health Check"
Info "GET /health"
try {
    Invoke-RestMethod -Uri "$BASE/health" -Method Get | ConvertTo-Json
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}

Section "TEST 3 - tasks/send - Unemployment Rate"
Info "Query: unemployment rate 2022-23"
Invoke-A2A @{
    jsonrpc = "2.0"
    id      = "req-001"
    method  = "tasks/send"
    params  = @{
        id        = "task-plfs-001"
        sessionId = "session-test-1"
        message   = @{
            role  = "user"
            parts = @(@{ type = "text"; text = "What is the unemployment rate in India for 2022-23?" })
        }
    }
}
Ok "Expect: result.status.state = completed, artifacts with unemployment data"

Section "TEST 4 - tasks/send - CPI Food Inflation"
Info "Query: CPI food group 2023"
Invoke-A2A @{
    jsonrpc = "2.0"
    id      = "req-002"
    method  = "tasks/send"
    params  = @{
        id        = "task-cpi-001"
        sessionId = "session-test-2"
        message   = @{
            role  = "user"
            parts = @(@{ type = "text"; text = "Give me CPI inflation index for food and beverages group for 2023." })
        }
    }
}
Ok "Expect: result.status.state = completed, CPI food group index values"

Section "TEST 5 - tasks/get - Retrieve task by ID"
Info "Fetching task-plfs-001 with historyLength 5"
Invoke-A2A @{
    jsonrpc = "2.0"
    id      = "req-003"
    method  = "tasks/get"
    params  = @{
        id            = "task-plfs-001"
        historyLength = 5
    }
}
Ok "Expect: same task from TEST 3, up to 5 history messages"

Section "TEST 6 - tasks/get - Non-existent task"
Info "Fetching a task ID that does not exist"
Invoke-A2A @{
    jsonrpc = "2.0"
    id      = "req-004"
    method  = "tasks/get"
    params  = @{ id = "task-does-not-exist" }
}
Ok "Expect: error.code = -32001, Task not found"

Section "TEST 7 - tasks/send - GDP Growth"
Info "Query: India GDP 2022-23"
Invoke-A2A @{
    jsonrpc = "2.0"
    id      = "req-005"
    method  = "tasks/send"
    params  = @{
        id        = "task-nas-001"
        sessionId = "session-test-3"
        message   = @{
            role  = "user"
            parts = @(@{ type = "text"; text = "What is India GDP at current prices for 2022-23 base year 2011-12?" })
        }
    }
}
Ok "Expect: result.status.state = completed, NAS GDP values"

Section "TEST 8 - tasks/cancel"
Info "Attempting to cancel task-plfs-001"
Invoke-A2A @{
    jsonrpc = "2.0"
    id      = "req-006"
    method  = "tasks/cancel"
    params  = @{ id = "task-plfs-001" }
}
Ok "Expect: error -32002 already completed OR state = canceled"

Section "TEST 9 - Invalid JSON-RPC version"
Info "Sending jsonrpc 1.0 instead of 2.0"
Invoke-A2A @{
    jsonrpc = "1.0"
    id      = "req-007"
    method  = "tasks/send"
    params  = @{}
}
Ok "Expect: error.code = -32600, Invalid Request"

Section "TEST 10 - Unknown method"
Info "Calling a method that does not exist"
Invoke-A2A @{
    jsonrpc = "2.0"
    id      = "req-008"
    method  = "tasks/unknownMethod"
    params  = @{}
}
Ok "Expect: error.code = -32601, Method not found"

Section "TEST 11 - tasks/sendSubscribe - SSE Streaming"
Info "Streaming query: IIP manufacturing index April 2023"

$body = @{
    jsonrpc = "2.0"
    id      = "req-009"
    method  = "tasks/sendSubscribe"
    params  = @{
        id        = "task-stream-001"
        sessionId = "session-stream-1"
        message   = @{
            role  = "user"
            parts = @(@{ type = "text"; text = "Show IIP manufacturing index for April 2023." })
        }
    }
} | ConvertTo-Json -Depth 10

try {
    # Load System.Net.Http explicitly - required in Windows PowerShell
    Add-Type -AssemblyName System.Net.Http

    $httpClient = [System.Net.Http.HttpClient]::new()
    $httpClient.Timeout = [System.TimeSpan]::FromSeconds(60)
    $content = [System.Net.Http.StringContent]::new(
        $body,
        [System.Text.Encoding]::UTF8,
        "application/json"
    )
    $response = $httpClient.PostAsync($BASE, $content).Result
    $stream   = $response.Content.ReadAsStreamAsync().Result
    $reader   = [System.IO.StreamReader]::new($stream)
    Write-Host "SSE Events received:" -ForegroundColor Yellow
    while (-not $reader.EndOfStream) {
        $line = $reader.ReadLine()
        if ($line -ne "") {
            Write-Host $line -ForegroundColor Cyan
            if ($line -match '"final"\s*:\s*true') { break }
        }
    }
    $reader.Dispose()
    $httpClient.Dispose()
} catch {
    Write-Host "SSE ERROR: $_" -ForegroundColor Red
}
Ok "Expect: 3 SSE events - submitted, working, completed with final true"

Write-Host ""
Write-Host "===========================================" -ForegroundColor Green
Write-Host "  All tests complete." -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green