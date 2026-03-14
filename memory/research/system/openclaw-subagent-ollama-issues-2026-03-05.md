# OpenClaw Subagent + Local Ollama Model Issues Research
**Date:** 2026-03-05
**Source:** GitHub Issues (openclaw/openclaw)

## Key Findings from GitHub Issues

### Critical Issues Affecting Our Setup

**1. Subagent Spawning Fails with Local Ollama Models**
- **Issue #24654**: "Bug: Subagent spawning fails with local Ollama models (ollama/*)"
- **Status**: Open
- **Impact**: Subagents may fail to spawn or hang when using Ollama models

**2. Ollama Subagent Timeout Issues**
- **Issue #27883**: "Ollama subagent timeout - shell curl works, subagent hangs"
- **Status**: Closed (completed)
- **Finding**: Subagents hang when trying to reach Ollama, but shell curl works fine
- **Solution**: Sandbox isolation issue - subagents couldn't reach localhost

**3. Local Ollama Models Hang Indefinitely**
- **Issue #31399**: "Local Ollama models hang indefinitely (timeout), remote ollama.com models work fine"
- **Status**: Open
- **Impact**: Local models timeout while remote models work

**4. Isolated Sessions Cannot Access Built-in Provider Env Vars**
- **Issue #29886**: "Isolated sessions (cron/subagents) cannot access built-in provider env vars from openclaw.json"
- **Status**: Open
- **Impact**: Cron jobs and subagents may not have access to Ollama configuration

**5. Tool Surface Mismatch Across Runtime Lanes**
- **Issue #30685**: "Tool surface mismatch (session_status available in main, missing in subagent lane)"
- **Status**: Open
- **Impact**: Subagents have different tool availability than main session

**6. Cron Announce Delivery Times Out for Slow Local Models**
- **Issue #22027**: "Cron announce delivery times out for slow local models (15s hardcoded timeout)"
- **Status**: Closed (completed)
- **Finding**: 15-second hardcoded timeout too short for local models

**7. Compaction Fails with Slow Local Models**
- **Issue #27595**: "Compaction does not auto-trigger reliably and fails under 5min JS timeout with slow local models"
- **Status**: Open
- **Impact**: Memory compaction may fail with slow local models

**8. Ollama Native API Hangs on ARM Without GPU**
- **Issue #33163**: "Ollama native API: 'waiting for llama runner to start responding' infinite waiting"
- **Status**: Open

## Why Our Research Job Should Work

Based on the GitHub issues, the key problems were:

1. **Sandbox isolation** — Subagents couldn't reach Ollama on localhost
   - ✅ **FIXED**: We disabled sandbox (`"mode": "off"`)

2. **Timeout too short** — Default timeouts too short for local models
   - ✅ **FIXED**: We set 20-minute timeout (`timeoutSeconds: 1200`)

3. **Isolated sessions env vars** — Cron jobs couldn't access Ollama config
   - ✅ **MITIGATED**: Using isolated sessions with explicit model override

## Configuration That Should Work

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "off"
      }
    }
  },
  "cron": {
    "enabled": true
  }
}
```

With cron jobs:
- `sessionTarget`: "isolated"
- `payload.model`: "ollama/qwen2.5:14b"
- `timeoutSeconds`: 1200 (20 minutes)

## Known Limitations

1. **Local models are slower** — Expect 10-20 minutes for research tasks
2. **First load takes time** — Ollama needs to load model into RAM
3. **Isolated sessions** — Don't have access to all main session tools
4. **No session tools** — Subagents can't spawn other subagents (depth 1)

## Sources
- https://github.com/openclaw/openclaw/issues?q=subagent+local+model+ollama
- 22 open issues, 40 closed issues related to this topic
