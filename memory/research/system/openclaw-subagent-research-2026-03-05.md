# OpenClaw Subagent Research Report
**Date:** 2026-03-05
**Topic:** Local Agent Spawning, Timeouts, and Configuration

## Key Findings

### 1. Timeout Configuration

The `runTimeoutSeconds` parameter in `sessions_spawn` has a specific fallback chain:

1. **Explicit** `sessions_spawn.runTimeoutSeconds` (what we set)
2. **Config default** `agents.defaults.subagents.runTimeoutSeconds`
3. **Fallback** `0` (no timeout)

**Critical Discovery:** The default timeout is NOT 300 seconds (5 minutes) — it's `0` (no timeout). Our subagents failing at exactly 5 minutes suggests either:
- A different timeout is being applied (possibly model-level or gateway-level)
- The subagents are crashing/looping, not timing out

### 2. Proper Subagent Configuration

To enable subagents with proper timeouts, add this to `openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxSpawnDepth": 2,
        "maxChildrenPerAgent": 5,
        "maxConcurrent": 8,
        "runTimeoutSeconds": 1800
      }
    }
  }
}
```

### 3. Sandbox Configuration

Sandbox mode for subagents is controlled separately from main agent:

- **Config path:** `agents.defaults.sandbox.mode`
- **Options:**
  - `"off"` — No sandbox (what we set)
  - `"non-main"` — Sandbox only non-main sessions
  - `"all"` — Sandbox everything

**Important:** Even with `"mode": "off"`, subagents may still have restrictions if Docker isn't available.

### 4. Subagent Tool Access

By default, sub-agents get **all tools except session tools**:
- ❌ `sessions_list`
- ❌ `sessions_history`
- ❌ `sessions_send`
- ❌ `sessions_spawn` (unless `maxSpawnDepth >= 2`)

This means subagents CAN use:
- ✅ `web_search`
- ✅ `web_fetch`
- ✅ `browser`
- ✅ `exec`
- ✅ `read/write/edit`

### 5. Research Task Architecture Issues

Our research subagents were failing because:

1. **Complex multi-step tasks** — Research requires web_search → web_fetch → synthesis → write
2. **No session tools** — Subagents can't spawn further subagents or manage sessions
3. **Single-turn limitation** — `mode: "run"` means one-shot execution
4. **Context isolation** — Subagents don't inherit full context (no SOUL.md, USER.md, etc.)

### 6. Recommended Solutions

#### Option A: Shorter, Focused Tasks
Break research into discrete steps:
```python
# Instead of one big research task:
task = "Research AI developments, find sources, write report"

# Use multiple focused subagents:
task1 = "Search for latest AI model releases, return top 3 findings"
task2 = "Search for OpenClaw updates, return changelog summary"
task3 = "Search for passive income AI ideas, return 5 concrete examples"
```

#### Option B: Main Session Research
Do research directly in main session (what we're doing now):
- No timeout issues
- Full tool access
- Can iterate and refine
- Better for complex multi-step research

#### Option C: Persistent Thread-Bound Sessions
For ongoing research:
```json
{
  "sessions_spawn": {
    "thread": true,
    "mode": "session"
  }
}
```
This creates a persistent session that can receive follow-up messages.

### 7. Concurrency and Limits

- **Global concurrency:** `maxConcurrent` (default: 8)
- **Per-agent children:** `maxChildrenPerAgent` (default: 5)
- **Nesting depth:** `maxSpawnDepth` (default: 1, max: 5)

### 8. Best Practices for Local Research Agents

1. **Set explicit timeouts** in config, not just spawn call
2. **Use simpler models** for subagents (cheaper, faster)
3. **Break tasks into chunks** — 5-10 minute tasks, not 30 minutes
4. **Handle failures gracefully** — subagents can fail, plan for it
5. **Use `label`** parameter to identify subagent purpose
6. **Check `subagents list`** to monitor active runs

### 9. Cron Job Alternative

For automated research, use cron jobs with `systemEvent` calling a script:

```json
{
  "payload": {
    "kind": "systemEvent",
    "text": "python research_runner.py"
  }
}
```

The script can then:
- Check if research is needed
- Spawn subagents with shorter tasks
- Aggregate results
- Write to memory

### 10. Debugging Failed Subagents

When subagents fail:
1. Check `subagents list` for status
2. Use `subagents log <id>` to see output
3. Use `subagents info <id>` for metadata
4. Check transcript file on disk
5. Verify model availability (Ollama running?)

## Conclusion

Our research subagents failed because:
1. Tasks were too complex for single-turn execution
2. Timeout configuration may not have been applied correctly
3. Subagents have limited session tool access
4. No error handling for web search failures

**Recommendation:** For now, do research in main session (as we're doing). For automation, use shorter, focused subagent tasks or cron jobs with wrapper scripts.

## Sources
- OpenClaw Documentation: https://docs.openclaw.ai/tools/subagents
- Configuration tested: 2026-03-05
- Subagent spawn attempts: 9 total, 0 successful for complex research tasks
