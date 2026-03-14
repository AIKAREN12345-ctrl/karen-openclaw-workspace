# OpenClaw 2026.3.1 Node Command Syntax Research

**Date:** 2026-03-03  
**OpenClaw Version:** 2026.3.1  
**Research Focus:** New `nodes run` command format, `systemRunPlan`, and canonical path requirements

---

## Executive Summary

OpenClaw 2026.3.1 introduced significant breaking changes to the `nodes run` command syntax. The old format using `command: ["executable", "arg1", "arg2"]` no longer works directly. Instead, commands must now go through a **preparation phase** that creates a `systemRunPlan`, and executables must use **canonical (resolved) paths** rather than bare command names.

---

## 1. The New Node Run Command Format

### Old Syntax (No Longer Works)
```json
{
  "tool": "nodes",
  "command": ["ollama", "list"]
}
```

**Errors you'll see:**
- `"rawCommand does not match command"`
- `"SYSTEM_RUN_DENIED: approval requires a stable executable path"`

### New Syntax - Two-Phase Process

The new flow requires:
1. **Preparation Phase**: Call `system.run.prepare` to validate and create a `systemRunPlan`
2. **Execution Phase**: Call `system.run` with the approved plan

### CLI Usage (Recommended)

```bash
# Using --raw (shell command string)
openclaw nodes run --node <id> --raw "ollama list"

# Using argv-style (explicit command array)
openclaw nodes run --node <id> -- ollama list

# With options
openclaw nodes run --node <id> --cwd /home/user --env KEY=val --raw "ollama list"
```

### Programmatic Usage (via node.invoke)

```json
// Step 1: Prepare the run
{
  "tool": "nodes",
  "action": "invoke",
  "node": "<node-id>",
  "command": "system.run.prepare",
  "params": {
    "command": ["/usr/local/bin/ollama", "list"],
    "rawCommand": "/usr/local/bin/ollama list",
    "cwd": "/home/user",
    "agentId": "main"
  }
}

// Returns: { plan: { argv, cwd, rawCommand, agentId, sessionKey }, cmdText }

// Step 2: Execute with approval
{
  "tool": "nodes", 
  "action": "invoke",
  "node": "<node-id>",
  "command": "system.run",
  "params": {
    "command": ["/usr/local/bin/ollama", "list"],
    "rawCommand": "/usr/local/bin/ollama list",
    "cwd": "/home/user",
    "approved": true,
    "approvalDecision": "allow-once",
    "runId": "<approval-id>"
  }
}
```

---

## 2. What is systemRunPlan?

The `systemRunPlan` is a **structured command execution plan** that serves as the authoritative context for approval and execution. It was introduced in 2026.3.1 to improve security and prevent command injection.

### Structure

```typescript
interface SystemRunPlan {
  argv: string[];        // Resolved command arguments with canonical executable path
  cwd: string | null;    // Working directory
  rawCommand: string | null;  // Original command text (for display)
  agentId: string | null;     // Agent identifier
  sessionKey: string | null;  // Session key for binding
}
```

### Purpose

1. **Security**: The plan is created during `system.run.prepare` and validated against the allowlist
2. **Approval Binding**: When approvals are required, the `systemRunPlan` is included in the approval request
3. **Consistency**: Ensures the command that was approved is exactly what gets executed
4. **Audit Trail**: Tracks resolved paths and execution context

### Approval Flow with systemRunPlan

```
1. Client calls system.run.prepare with command
2. Node resolves executable to canonical path
3. Node returns systemRunPlan
4. Client requests approval with systemRunPlan
5. User approves (binding includes the plan)
6. Client calls system.run with approved plan
7. Node validates execution matches approved plan
```

---

## 3. How to Run Simple Commands

### Finding Canonical Paths

**Critical**: Commands must use **canonical (absolute, resolved) paths** - not bare command names.

```bash
# Find the canonical path for ollama
which ollama
# Output: /usr/local/bin/ollama

# On Windows
where ollama
# Output: C:\Program Files\Ollama\ollama.exe

# Use realpath for symlinks
realpath $(which ollama)
```

### Examples

#### Ollama List
```bash
# CLI
openclaw nodes run --node <id> --raw "/usr/local/bin/ollama list"

# Or with argv
openclaw nodes run --node <id> -- /usr/local/bin/ollama list
```

#### Ollama Remove Model
```bash
openclaw nodes run --node <id> --raw "/usr/local/bin/ollama rm llama3.2:3b"
```

#### Windows Example
```bash
openclaw nodes run --node <id> --raw "C:\Program Files\Ollama\ollama.exe list"
```

### Using --raw vs argv

| Method | Platform | Shell Used |
|--------|----------|------------|
| `--raw "cmd"` | macOS/Linux | `/bin/sh -lc "cmd"` |
| `--raw "cmd"` | Windows | `cmd.exe /d /s /c "cmd"` |
| `-- arg1 arg2` | All | Direct execution (no shell wrapper) |

**Recommendation**: Use `--raw` for simple commands, `--` for commands needing precise argument handling.

---

## 4. Canonical Path Requirements

### Why Canonical Paths?

The 2026.3.1 security model requires **stable executable paths** for allowlist matching:

1. **No PATH resolution**: Commands like `ollama` (without full path) are rejected
2. **No symlinks**: Symlinks must be resolved to their real targets
3. **Case sensitivity**: Windows paths must match the actual filesystem case

### Getting Canonical Paths

```bash
# Linux/macOS
realpath $(which ollama)
readlink -f $(which ollama)

# Windows (PowerShell)
(Get-Command ollama).Source

# Windows (CMD)
where ollama
```

### Allowlist Configuration

Add canonical paths to the node allowlist:

```bash
# Via CLI
openclaw approvals allowlist add --node <id> "/usr/local/bin/ollama"
openclaw approvals allowlist add --node <id> "/opt/homebrew/bin/rg"

# Direct file edit (on node host)
# ~/.openclaw/exec-approvals.json
{
  "agents": {
    "main": {
      "allowlist": [
        { "pattern": "/usr/local/bin/ollama" },
        { "pattern": "/opt/homebrew/bin/rg" }
      ]
    }
  }
}
```

---

## 5. Complete Working Examples

### Example 1: Basic Command Execution

```bash
# 1. Find canonical path
$ which ollama
/usr/local/bin/ollama

# 2. Run command
$ openclaw nodes run --node desktop-m8ao8ln --raw "/usr/local/bin/ollama list"

# Output:
NAME            ID              SIZE      MODIFIED
qwen2.5:7b      7c00c23f7f      4.7 GB    2 weeks ago
llama3.2:3b     a80c4f17acd     2.0 GB    3 weeks ago
```

### Example 2: With Working Directory

```bash
openclaw nodes run \
  --node desktop-m8ao8ln \
  --cwd /home/user/projects \
  --raw "/usr/bin/git status"
```

### Example 3: With Environment Variables

```bash
openclaw nodes run \
  --node desktop-m8ao8ln \
  --env API_KEY=secret123 \
  --env DEBUG=1 \
  --raw "/usr/local/bin/myscript"
```

### Example 4: Via nodes invoke (Low-level)

```json
{
  "tool": "nodes",
  "action": "invoke",
  "node": "desktop-m8ao8ln",
  "command": "system.run",
  "params": {
    "command": ["/usr/local/bin/ollama", "list"],
    "rawCommand": "/usr/local/bin/ollama list",
    "cwd": "/home/user",
    "approved": true
  }
}
```

---

## 6. Security Modes

### Configuring Security

```bash
# Check current settings
openclaw config get tools.exec

# Set defaults
openclaw config set tools.exec.host node
openclaw config set tools.exec.security allowlist
openclaw config set tools.exec.ask on-miss
openclaw config set tools.exec.node "desktop-m8ao8ln"
```

### Security Levels

| Level | Description |
|-------|-------------|
| `deny` | Block all host exec requests |
| `allowlist` | Allow only explicitly allowlisted commands (recommended) |
| `full` | Allow everything (dangerous) |

### Ask Modes

| Mode | Description |
|------|-------------|
| `off` | Never prompt |
| `on-miss` | Prompt only when command not in allowlist (recommended) |
| `always` | Prompt on every command |

---

## 7. Troubleshooting

### "rawCommand does not match command"

**Cause**: The `rawCommand` string doesn't match the reconstructed command from `argv`.

**Fix**: Ensure both `command` (argv array) and `rawCommand` (string) are provided and consistent:
```json
{
  "command": ["/usr/local/bin/ollama", "list"],
  "rawCommand": "/usr/local/bin/ollama list"
}
```

### "SYSTEM_RUN_DENIED: approval requires a stable executable path"

**Cause**: Using bare command name instead of canonical path.

**Fix**: Use full path:
```bash
# Wrong
openclaw nodes run --node <id> -- ollama list

# Right
openclaw nodes run --node <id> -- /usr/local/bin/ollama list
```

### "exec denied: host=node security=deny"

**Cause**: Security is set to `deny` mode.

**Fix**: Change security mode:
```bash
openclaw config set tools.exec.security allowlist
```

---

## 8. Key Changes from 2026.2.x to 2026.3.1

1. **Two-phase execution**: `system.run.prepare` → approval → `system.run`
2. **Canonical paths required**: No bare command names, symlinks must be resolved
3. **systemRunPlan**: Structured plan object for approval binding
4. **Consistency validation**: `rawCommand` must match reconstructed `argv`
5. **Shell wrapper detection**: Better handling of `sh -c`, `bash -lc`, `cmd.exe /c`

---

## References

- CHANGELOG.md (2026.3.1 section - Security/macOS app beta)
- docs/nodes/index.md
- docs/tools/exec.md
- docs/tools/exec-approvals.md
- Source: dist/nodes-cli-BrPrZexh.js
- Source: dist/nodes-screen-BVl5uK4q.js
- Source: dist/system-run-command-DqBhVJbL.js
