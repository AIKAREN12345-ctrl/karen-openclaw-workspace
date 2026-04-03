# Errors Log

## [ERR-20260403-001] OpenClaw 2026.4.1 exec regression

**Logged**: 2026-04-03T20:46:00Z
**Priority**: critical
**Status**: resolved
**Area**: config

### Summary
OpenClaw 2026.4.1 blocks ALL interpreter commands (PowerShell, Python, etc.) with SYSTEM_RUN_DENIED error, even when security=full and ask=off.

### Error
```
INVALID_REQUEST: SYSTEM_RUN_DENIED: approval cannot safely bind this interpreter/runtime command
```

### Context
- Upgraded from 2026.3.2 to 2026.4.1
- Config had security=full, ask=off
- All exec commands with interpreters failed
- Affects: python, powershell, bash, node, etc.

### Root Cause
GitHub issue #48457 - system.run.prepare() called unconditionally, hard-fails for interpreter "inline payload" forms regardless of approval settings.

### Resolution
- **Downgraded to 2026.3.2** - immediate fix
- **Documented in**: docs/EXEC-REGRESSION-2026.4.1.md
- **Workaround**: Use script files instead of inline commands
- **Status**: Waiting for OpenClaw team to patch

### Metadata
- Reproducible: yes
- Related Files: docs/EXEC-REGRESSION-2026.4.1.md, docs/VNC-PYTHON-BLOCK-ISSUE.md
- See Also: GitHub issue #48457
- Promoted: AGENTS.md (version pinning note)

---
