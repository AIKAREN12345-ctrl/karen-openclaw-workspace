# OpenClaw 2026.4.1 - VNC/Python Interpreter Block Issue

**Date:** 2026-04-03  
**Issue:** Python-based VNC scripts blocked by security hardening  
**GitHub Issue:** [#48457](https://github.com/openclaw/openclaw/issues/48457)

---

## Problem

After updating to OpenClaw 2026.4.1, all Python interpreter commands fail with:

```
INVALID_REQUEST: SYSTEM_RUN_DENIED: approval cannot safely bind this interpreter/runtime command
```

This affects:
- `python` commands directly
- `python` via batch file wrappers
- `python` via PowerShell
- All interpreter/runtime binaries (Python, Node, Ruby, Bash, etc.)

---

## Root Cause

Confirmed bug in OpenClaw 2026.3.11+ (still present in 2026.4.1):

The `system.run.prepare` handler calls `buildSystemRunApprovalPlan()` **unconditionally** — it performs interpreter binding checks even when approvals are disabled (`security=full`, `ask=off`).

The interpreter resolver has a separate safety gate that blocks all runtime commands regardless of trust settings. Two systems (approval layer + interpreter resolver) independently decide what's safe, they disagree, and the user gets a deny from a config that says allow.

---

## What Was Tried (Failed)

| Attempt | Result |
|---------|--------|
| `security=full` in exec-approvals.json | ❌ Still blocked |
| `security=allowlist` with Python in allowlist | ❌ Still blocked |
| `strictInlineEval=true` | ❌ Still blocked |
| Batch file wrapper | ❌ Detected as shell wrapper, blocked |
| `ask=on-miss` parameter | ❌ Not passed correctly to node |

---

## Current Workarounds

### Option 1: Use Browser/CDP Screenshots (Recommended)
```
browser action=snapshot url=https://example.com
```
✅ Working — Chrome automation fully functional

### Option 2: Run VNC Scripts Manually
```powershell
# Run directly in PowerShell
python C:\Users\Karen\.openclaw\workspace\vnc-screenshot-robust.py
```
✅ Works when run outside OpenClaw

### Option 3: Downgrade to 2026.3.8
Last known working version before the regression.
⚠️ Loses 2026.4.1 security improvements

### Option 4: Wait for Fix
GitHub issue #48457 is open, no ETA provided.

---

## System Status (2026-04-03)

| Component | Status | Notes |
|-----------|--------|-------|
| Gateway | ✅ Running | Port 18789 |
| Node | ✅ Running | DESKTOP-M8AO8LN |
| Telegram | ✅ OK | @Karen_G_Bot |
| Memory | ✅ Active | 200 files, 1335 chunks |
| Browser/CDP | ✅ Working | Chrome port 18800 |
| Ollama | ✅ Running | qwen3.5, nomic-embed-text |
| Semantic Search | ✅ Ready | Vector + FTS |
| Cron Jobs | ✅ 6 active | All healthy |
| VNC Python | ❌ Blocked | Known bug #48457 |

---

## References

- **GitHub Issue:** [#48457 - nodes.run fails for interpreter one-liners](https://github.com/openclaw/openclaw/issues/48457)
- **Related:** [#59006 - Update 2026.4.1 broke exec completely](https://github.com/openclaw/openclaw/issues/59006)
- **Related:** [#59855 - exec approval mechanism broke single-operator setups](https://github.com/openclaw/openclaw/issues/59855)
- **Related:** [#58881 - tools.exec.ask=off ignored](https://github.com/openclaw/openclaw/issues/58881)

---

## Last Updated

2026-04-03 17:24 UTC by Karen
