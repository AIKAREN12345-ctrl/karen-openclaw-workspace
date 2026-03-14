# Deep Research: OpenClaw Cron Jobs + Local LLM Integration

**Research Date:** 2026-03-05  
**Researcher:** Karen (Subagent)  
**System:** OpenClaw 2026.3.1 on Windows 11  
**Sources:** OpenClaw CLI, configuration files, runtime logs, local testing

---

## Executive Summary

This research documents the architecture, configuration options, and real-world pitfalls of using OpenClaw's cron job system with local LLMs (Ollama). Based on analysis of 9 active cron jobs and their execution history, we identify critical failure patterns and provide actionable recommendations for reliable automation.

**Key Finding:** Isolated sessions (`sessionTarget: isolated`) with Ollama models are experiencing systematic failures due to sandbox isolation preventing localhost access. The workaround is to use `sessionTarget: main` for Ollama-based cron jobs.

---

## 1. Cron Job Architecture

### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        OpenClaw Gateway                         │
│                     (WebSocket Control Plane)                   │
├─────────────────────────────────────────────────────────────────┤
│  Cron Scheduler  │  Job Store (JSONL)  │  Session Manager       │
└────────┬─────────────────┬──────────────────┬───────────────────┘
         │                 │                  │
    ┌────▼────┐      ┌────▼────┐      ┌─────▼──────┐
    │  Cron   │      │  Job    │      │  Agent     │
    │ Engine  │◄────►│  State  │      │  Runtime   │
    └────┬────┘      └─────────┘      └─────┬──────┘
         │                                   │
         ▼                                   ▼
    ┌─────────┐                        ┌──────────┐
    │  Wake   │                        │  Model   │
    │  Events │                        │  Router  │
    └─────────┘                        └────┬─────┘
                                            │
                    ┌───────────────────────┼───────────────┐
                    ▼                       ▼               ▼
              ┌─────────┐            ┌──────────┐    ┌──────────┐
              │  Cloud  │            │  Ollama  │    │  System  │
              │  APIs   │            │  Local   │    │  Events  │
              └─────────┘            └──────────┘    └──────────┘
```

### 1.2 Job Configuration Schema

Cron jobs are stored in `~/.openclaw/cron/jobs.json` with the following structure:

```json5
{
  "id": "unique-job-id",           // Auto-generated or specified
  "agentId": "main",               // Which agent context to use
  "name": "human-readable-name",
  "enabled": true,
  "createdAtMs": 1772718660000,
  "updatedAtMs": 1772718660000,
  "schedule": {
    "kind": "cron",               // "cron" | "interval" | "once"
    "expr": "0 * * * *",          // Standard cron expression (5-field)
    "tz": "Europe/Dublin",        // IANA timezone
    "staggerMs": 300000           // Random delay (0 to N ms)
  },
  "sessionTarget": "isolated",    // "main" | "isolated"
  "wakeMode": "now",              // "now" | "next-heartbeat"
  "payload": {
    "kind": "agentTurn",          // "agentTurn" | "systemEvent"
    "message": "Agent prompt",
    "model": "ollama/qwen2.5:14b",
    "timeoutSeconds": 2700        // CRITICAL: Default 30s often insufficient
  },
  "delivery": {
    "mode": "none"                // "none" | "announce" | channel-specific
  }
}
```

### 1.3 Schedule Types

| Type | Description | Example |
|------|-------------|---------|
| `cron` | Standard cron expression | `"0 */2 * * *"` (every 2 hours) |
| `interval` | Duration-based | `"every": "10m"` |
| `once` | One-time execution | `"at": "+20m"` or ISO timestamp |

### 1.4 Key Configuration Options

**Critical Parameters:**

- `--timeout-seconds <n>`: Maximum execution time (default: 30s, often needs 1800s+ for research)
- `--stagger <duration>`: Random delay to prevent thundering herd (e.g., `5m`)
- `--exact`: Disable staggering entirely
- `--light-context`: Use lightweight bootstrap (faster startup, less context)
- `--thinking <level>`: Control reasoning depth (`off|minimal|low|medium|high`)

---

## 2. Local LLM (Ollama) Integration

### 2.1 Model Configuration

Ollama models are configured in `~/.openclaw/openclaw.json`:

```json5
{
  "models": {
    "providers": {
      "ollama": {
        "baseUrl": "http://localhost:11434",
        "apiKey": "ollama-local",
        "api": "ollama",
        "models": [
          {
            "id": "qwen2.5:14b",
            "name": "Qwen 2.5 14B",
            "reasoning": false,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 128000,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

### 2.2 Model Selection for Cron Jobs

| Model | Size | Tool Support | Best For | Context Window |
|-------|------|--------------|----------|----------------|
| `qwen2.5:7b` | 4.7 GB | Excellent | General automation, tool calling | 128K |
| `qwen2.5:14b` | 9.0 GB | Excellent | Complex reasoning, research | 128K |
| `llama3.2:3b` | 2.0 GB | Poor | Avoid - tool calling broken | 128K |
| `phi3:mini` | 2.2 GB | Untested | Low-resource fallback | 128K |

**Recommendation:** Use `qwen2.5:7b` for most cron jobs (best speed/tool balance). Use `14b` only when reasoning quality is critical.

### 2.3 Keep-Alive Strategy

Local models unload after periods of inactivity, causing cold-start delays. Implement a keep-alive cron:

```json5
{
  "id": "ollama-keepalive",
  "name": "ollama-keepalive",
  "schedule": { "kind": "cron", "expr": "*/10 * * * *" },
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "powershell -Command 'ollama run qwen2.5:14b \"keepalive\" 2>&1 | Out-Null; ollama ps'"
  }
}
```

**Why this works:**
- Uses `sessionTarget: main` (bypasses sandbox)
- Runs PowerShell directly on the node
- `ollama ps` confirms model is loaded

---

## 3. Session Targets: Main vs Isolated

### 3.1 Architecture Differences

```
┌─────────────────────────────────────────────────────────────────┐
│                     SESSION TARGET COMPARISON                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MAIN SESSION                    ISOLATED SESSION               │
│  ─────────────                   ────────────────               │
│                                                                 │
│  ┌──────────────┐                ┌──────────────┐              │
│  │  Shared      │                │  Private     │              │
│  │  Context     │                │  Context     │              │
│  │  (with user) │                │  (isolated)  │              │
│  └──────┬───────┘                └──────┬───────┘              │
│         │                               │                      │
│         ▼                               ▼                      │
│  ┌──────────────┐                ┌──────────────┐              │
│  │  Sandbox:    │                │  Sandbox:    │              │
│  │  OFF (direct)│                │  ON (isolated)│             │
│  └──────┬───────┘                └──────┬───────┘              │
│         │                               │                      │
│         ▼                               ▼                      │
│  ┌──────────────┐                ┌──────────────┐              │
│  │  Can access  │                │  CANNOT      │              │
│  │  localhost   │                │  access      │              │
│  │  (Ollama ✓)  │                │  localhost   │              │
│  └──────────────┘                │  (Ollama ✗)  │              │
│                                  └──────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 When to Use Each

| Use Case | Target | Reason |
|----------|--------|--------|
| Ollama-based tasks | `main` | Sandbox blocks localhost:11434 |
| Web search with cloud models | `isolated` | Clean context, no history pollution |
| Sensitive operations | `isolated` | Security isolation |
| Long-running research | `isolated` | Won't block main session |
| System commands | `main` | Usually needs node access |
| Quick status checks | `main` | Lower overhead |

### 3.3 The Critical Issue: Ollama + Isolated Sessions

**Problem:** Isolated sessions run in a sandboxed environment that cannot access `localhost:11434` (Ollama's default port).

**Evidence from logs:**
```json
{
  "jobId": "research-openclaw-001",
  "status": "error",
  "error": "fetch failed",
  "model": "qwen2.5:14b",
  "provider": "ollama",
  "consecutiveErrors": 5
}
```

**Root Cause:**
- Isolated sessions use sandbox containers for security
- Sandbox network policy blocks localhost access
- Ollama runs on `localhost:11434`
- Result: Connection timeout / fetch failed

**Workaround:**
```json5
// ❌ BROKEN - Isolated + Ollama
{
  "sessionTarget": "isolated",
  "payload": { "model": "ollama/qwen2.5:14b" }
}

// ✓ WORKING - Main + Ollama
{
  "sessionTarget": "main",
  "payload": { "model": "ollama/qwen2.5:14b" }
}
```

---

## 4. Timeout Configurations & Performance Tuning

### 4.1 Default Timeouts

| Layer | Default | Config Key |
|-------|---------|------------|
| Cron job | 30 seconds | `timeoutSeconds` in payload |
| Agent turn | 180 seconds | `agents.defaults.timeoutSeconds` |
| Gateway | 30 seconds | `--timeout` flag |

### 4.2 Recommended Timeouts by Task Type

| Task Type | Recommended Timeout | Reason |
|-----------|---------------------|--------|
| Simple status check | 30-60s | Quick command execution |
| Web search (cloud) | 120-180s | API latency + processing |
| Web search (local) | 300-600s | Model load + inference |
| Research with tools | 1800-2700s | Multiple tool calls |
| Document generation | 1800-3600s | Long-form content |

### 4.3 Real-World Performance Data

From `research-openclaw-001` job analysis:

```
Run 1: 1,200,027 ms (20 min) - Timeout
Run 2: 1,200,023 ms (20 min) - Timeout  
Run 3: 1,200,030 ms (20 min) - Timeout
Run 4: 1,234,832 ms (20.5 min) - Fetch failed
Run 5: 1,234,387 ms (20.5 min) - Fetch failed
```

**Analysis:**
- Job configured with `timeoutSeconds: 2700` (45 min)
- Actual timeout occurring at ~20 minutes
- Suggests secondary timeout layer (possibly sandbox or gateway)

### 4.4 Stagger Configuration

**Purpose:** Prevent all cron jobs from starting simultaneously, overwhelming the system.

```json5
{
  "schedule": {
    "expr": "0 * * * *",      // Every hour at :00
    "staggerMs": 300000       // Random delay 0-5 minutes
  }
}
// Actual start: Between :00 and :05 each hour
```

**Best Practices:**
- Always use stagger for jobs with same cron expression
- Use `--exact` only when timing is critical
- Stagger window should exceed expected job duration

---

## 5. Common Pitfalls & Solutions

### 5.1 Pitfall #1: Isolated Sessions + Local LLMs

**Symptom:** `fetch failed` or timeout errors for Ollama models

**Diagnosis:**
```bash
openclaw cron runs --id <job-id> --limit 10
# Look for: "error": "fetch failed"
```

**Solution:**
```bash
# Edit job to use main session
openclaw cron edit <job-id> --session main
```

### 5.2 Pitfall #2: Insufficient Timeouts

**Symptom:** `cron: job execution timed out`

**Solution:**
```bash
# Set appropriate timeout for research tasks
openclaw cron edit <job-id> --timeout-seconds 2700
```

### 5.3 Pitfall #3: Model Cold Start

**Symptom:** First run slow, subsequent runs fast; timeouts on first run

**Solution:** Implement keep-alive (see Section 2.3)

### 5.4 Pitfall #4: Tool Calling with Wrong Models

**Symptom:** Model outputs tools in content instead of tool_calls

**Affected Models:** `llama3.2:3b`, `gemma:2b`

**Solution:** Use `qwen2.5:7b` or `qwen2.5:14b` for tool-based tasks

### 5.5 Pitfall #5: Consecutive Error Accumulation

**Symptom:** Job shows `consecutiveErrors: 5+`, stops running

**Current Behavior:** OpenClaw does NOT automatically disable jobs with consecutive errors

**Mitigation:** Monitor and manually intervene:
```bash
openclaw cron list  # Check Status column
openclaw cron runs --id <job-id> --limit 5  # Check error pattern
```

### 5.6 Pitfall #6: Delivery Mode Confusion

**Symptom:** Job runs but no notification received

**Configuration:**
```json5
// No notification
"delivery": { "mode": "none" }

// Announce to channel
"delivery": { "mode": "announce" }

// Specific channel
"delivery": { "mode": "channel", "channel": "telegram" }
```

---

## 6. Real-World Examples

### 6.1 Working Configuration: System Monitor

```json5
{
  "id": "ollama-monitor",
  "name": "ollama-monitor",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 */2 * * *",
    "staggerMs": 300000
  },
  "sessionTarget": "main",  // ✓ Required for localhost access
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "powershell -Command \"& {ollama ps; Write-Host 'Ollama status checked'}\""
  },
  "delivery": { "mode": "none" }
}
```

**Status:** ✅ Running successfully (15m ago)

### 6.2 Working Configuration: Git Backup

```json5
{
  "id": "github-backup",
  "name": "github-backup",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 2 * * *",
    "tz": "Europe/Dublin"
  },
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "cd C:\\Users\\Karen\\.openclaw\\workspace && git add -A && git commit -m 'Daily backup' && git push origin master"
  },
  "delivery": { "mode": "none" }
}
```

**Status:** ✅ Running successfully (16h ago)

### 6.3 Broken Configuration: Research with Isolated Session

```json5
{
  "id": "research-openclaw-001",
  "name": "research-openclaw",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 * * * *",
    "tz": "Europe/Dublin",
    "staggerMs": 300000
  },
  "sessionTarget": "isolated",  // ❌ BREAKS Ollama access
  "payload": {
    "kind": "agentTurn",
    "message": "Find 3 recent OpenClaw updates...",
    "model": "ollama/qwen2.5:14b",  // Cannot reach localhost
    "timeoutSeconds": 2700
  }
}
```

**Status:** ❌ 5 consecutive errors, last: `fetch failed`

### 6.4 Recommended Fix: Research with Main Session

```json5
{
  "id": "research-openclaw-001",
  "name": "research-openclaw",
  "schedule": {
    "kind": "cron",
    "expr": "0 * * * *",
    "tz": "Europe/Dublin",
    "staggerMs": 300000
  },
  "sessionTarget": "main",  // ✓ Fixed: Use main for Ollama
  "payload": {
    "kind": "agentTurn",
    "message": "Find 3 recent OpenClaw updates...",
    "model": "ollama/qwen2.5:14b",
    "timeoutSeconds": 2700
  },
  "delivery": { "mode": "none" }
}
```

---

## 7. Best Practices Summary

### 7.1 For Ollama-Based Cron Jobs

1. **Always use `sessionTarget: main`** - Isolated sessions cannot access localhost
2. **Set timeout to 1800s minimum** - Model loading + inference takes time
3. **Implement keep-alive** - Prevent cold-start delays
4. **Use `qwen2.5:7b` for most tasks** - Best tool support / speed balance
5. **Add stagger to hourly jobs** - Prevent thundering herd

### 7.2 For Cloud Model Cron Jobs

1. **Can use `sessionTarget: isolated`** - Clean context, no localhost needed
2. **Timeout 120-180s usually sufficient** - APIs are faster than local inference
3. **Consider `light-context: true`** - Faster startup if no history needed

### 7.3 For System Event Jobs

1. **Always use `sessionTarget: main`** - Needs node access
2. **Use PowerShell for Windows** - Better error handling
3. **Keep timeouts short** - Commands should be quick
4. **Test commands manually first** - Verify they work outside cron

### 7.4 Monitoring & Maintenance

```bash
# Daily health check
openclaw cron list
openclaw cron status

# Investigate failing jobs
openclaw cron runs --id <job-id> --limit 10

# View recent errors
openclaw logs --follow | grep -i error

# Restart gateway if needed
openclaw gateway restart
```

---

## 8. Open Questions & Future Research

1. **Sandbox Network Policy:** Can isolated sessions be configured to allow specific localhost ports?

2. **Alternative Timeout Layers:** What causes the ~20min timeout when job is configured for 45min?

3. **Model Parallelism:** Can multiple Ollama models run concurrently in cron jobs?

4. **Resource Limits:** How to prevent cron jobs from overwhelming system resources?

5. **Auto-Recovery:** Should OpenClaw automatically disable jobs with N consecutive errors?

---

## 9. References

### Configuration Files
- `~/.openclaw/openclaw.json` - Main configuration
- `~/.openclaw/cron/jobs.json` - Cron job definitions
- `~/.openclaw/node.json` - Node configuration

### CLI Commands
- `openclaw cron --help`
- `openclaw cron add --help`
- `openclaw agents list --bindings`
- `openclaw sandbox explain`

### Documentation
- https://docs.openclaw.ai/automation/cron-jobs
- https://docs.openclaw.ai/concepts/models
- https://docs.openclaw.ai/sandbox

### Active Jobs (as of 2026-03-05)
| Job | Schedule | Target | Model | Status |
|-----|----------|--------|-------|--------|
| research-ai-001 | 0 */3 * * * | isolated | ollama/qwen2.5:14b | error |
| research-openclaw-001 | 0 * * * * | isolated | ollama/qwen2.5:14b | error |
| research-income-001 | 0 */6 * * * | isolated | ollama/qwen2.5:14b | pending |
| ollama-keepalive | */10 * * * * | main | - | ok |
| ollama-monitor | 0 */2 * * * | main | - | ok |
| github-backup | 0 2 * * * | main | - | ok |

---

## 10. Action Items

### Immediate (This Session)
- [ ] Fix `research-openclaw-001` - Change `sessionTarget` from `isolated` to `main`
- [ ] Fix `research-ai-001` - Change `sessionTarget` from `isolated` to `main`
- [ ] Fix `research-income-001` - Change `sessionTarget` from `isolated` to `main`

### Short Term (This Week)
- [ ] Document this pattern in TOOLS.md
- [ ] Create monitoring script for cron job health
- [ ] Test if `light-context: true` improves startup time

### Long Term (This Month)
- [ ] Evaluate if isolated sessions can access Ollama via different network config
- [ ] Consider running Ollama on non-localhost interface for sandbox access
- [ ] Implement auto-retry with exponential backoff for failed jobs

---

*Research compiled by Karen subagent on 2026-03-05*  
*System: OpenClaw 2026.3.1 | Windows 11 | Node 24.13.1*
