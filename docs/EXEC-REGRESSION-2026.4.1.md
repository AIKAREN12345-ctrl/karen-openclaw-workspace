# OpenClaw 2026.4.1 - Exec Tool Regression

**Date:** 2026-04-03  
**Issue:** `exec` tool blocks all interpreter commands in interactive sessions  
**GitHub Issue:** [#48457](https://github.com/openclaw/openclaw/issues/48457)

---

## Summary

After updating to OpenClaw 2026.4.1, the `exec` tool fails for ALL interpreter commands in interactive sessions with error:

```
INVALID_REQUEST: SYSTEM_RUN_DENIED: approval cannot safely bind this interpreter/runtime command
```

This affects PowerShell, Python, Node, Bash, and all other interpreter/runtime binaries.

---

## What's Broken

| Tool | Command | Status |
|------|---------|--------|
| `exec` | `powershell -Command "Get-Date"` | ❌ Blocked |
| `exec` | `python script.py` | ❌ Blocked |
| `exec` | `gh --version` | ❌ Blocked |
| `exec` | `npm install` | ❌ Blocked |
| `exec` | `openclaw doctor` | ❌ Blocked |

---

## What's Working

| Tool | Use Case | Status |
|------|----------|--------|
| `read` / `write` / `edit` | File operations | ✅ Working |
| `browser` | Chrome/CDP automation | ✅ Working |
| `sessions_history` / `sessions_list` | Session management | ✅ Working |
| `memory_search` | Semantic search | ✅ Working |
| `ollama_web_search` / `ollama_web_fetch` | Web search | ✅ Working |
| `subagents` / `sessions_spawn` | Agent spawning | ✅ Working |

---

## Root Cause

Bug #48457: The `system.run.prepare` handler calls `buildSystemRunApprovalPlan()` **unconditionally** — it performs interpreter binding checks even when approvals are disabled (`security=full`, `ask=off`).

The interpreter resolver has a separate safety gate that blocks all runtime commands regardless of trust settings. Two systems (approval layer + interpreter resolver) independently decide what's safe, they disagree, and the user gets a deny from a config that says allow.

---

## Affected Configurations Tested

| Config | Result |
|--------|--------|
| `security=full`, `ask=off` | ❌ Blocked |
| `security=allowlist`, `ask=off` | ❌ Blocked |
| `security=allowlist`, `ask=on-miss` | ❌ Blocked |
| PowerShell in allowlist | ❌ Blocked |
| Python in allowlist | ❌ Blocked |
| `strictInlineEval=true` | ❌ Blocked |
| Gateway restart | ❌ No effect |
| Config revert | ❌ No effect |

---

## Workarounds

### Option 1: Use Browser/CDP (Recommended)
```javascript
// Navigate and interact with websites
browser action=navigate url=https://example.com
browser action=snapshot
browser action=act request={"kind":"click","ref":"ax1"}
```

### Option 2: File Operations
```javascript
// Read, write, edit files
read file_path=C:/path/to/file.txt
write file_path=C:/path/to/file.txt content="text"
edit file_path=C:/path/to/file.txt edits=[...]
```

### Option 3: Web Search/Fetch
```javascript
// Search and fetch web content
ollama_web_search query="search term"
ollama_web_fetch url=https://example.com
```

### Option 4: Subagent Spawning
```javascript
// Spawn isolated agents for tasks
sessions_spawn task="research topic" mode=run
```

---

## What Does Work (Cron Jobs)

Cron jobs using `local-automation` agent still work because they use a different code path that bypasses the interactive session bug.

Example working cron jobs:
- Hourly memory logs
- Ollama heartbeat
- GitHub backups

---

## Fix Options

### Option 1: Downgrade to 2026.3.8 (Immediate)
```powershell
npm install -g openclaw@2026.3.8
# Or
pnpm install -g openclaw@2026.3.8
```

### Option 2: Wait for Patch
- GitHub issue #48457 is open
- No ETA from OpenClaw team
- Affects all 2026.4.1 users

### Option 3: Node-Side Patch (Advanced)
Modify OpenClaw source code to bypass binding check when `security=full` + `ask=off`.

---

## Decision Log

**2026-04-03 17:54:** Decision to downgrade to 2026.3.8 due to severity of regression and no viable workaround for shell command automation.

---

## References

- **GitHub Issue:** [#48457 - nodes.run fails for interpreter one-liners](https://github.com/openclaw/openclaw/issues/48457)
- **Related:** [#59006 - Update 2026.4.1 broke exec completely](https://github.com/openclaw/openclaw/issues/59006)
- **Related:** [#59855 - exec approval mechanism broke single-operator setups](https://github.com/openclaw/openclaw/issues/59855)

---

## Last Updated

2026-04-03 17:54 UTC by Karen
