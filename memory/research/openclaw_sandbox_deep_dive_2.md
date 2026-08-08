# OpenClaw Sandbox Isolation Deep Dive Research

**Research Date:** 2026-04-13  
**Researcher:** Karen (OpenClaw Agent)  
**Objective:** Investigate OpenClaw sandbox isolation, undocumented workarounds, Windows-specific solutions, and the localhost/Ollama connection issue

---

## Executive Summary

OpenClaw's sandbox isolation is implemented primarily through Docker containers with network namespace isolation. The key issue affecting local Ollama usage in subagents is that **sandboxed agents run in isolated network namespaces that cannot reach the host's localhost services** (like Ollama on port 11434).

**Critical Finding:** There is NO documented workaround to allow sandboxed agents to access host localhost services. The `local-automation` agent type was designed for this purpose but appears to have sandbox isolation issues that prevent Ollama access.

---

## 1. How OpenClaw Sandbox Isolation Works

### 1.1 Sandbox Modes

From the official documentation and source code analysis:

| Mode | Description |
|------|-------------|
| `"off"` | No sandboxing - tools run on the host |
| `"non-main"` | Sandbox only non-main sessions (default) |
| `"all"` | Every session runs in a sandbox |

The `non-main` mode is based on `session.mainKey` (default `"main"`), not agent id. Group/channel sessions use their own keys and count as non-main, so they get sandboxed.

### 1.2 Network Isolation Implementation

**Source:** GitHub commit `14b6eea6e` (2026-02-24) - "block container namespace joins by default"

```typescript
// From src/agents/sandbox/validate-sandbox-security.ts
export function validateNetworkMode(
  network: string | undefined,
  options?: ValidateNetworkModeOptions,
): void {
  const normalized = network?.trim().toLowerCase();
  
  // Blocks "host" network mode entirely
  if (BLOCKED_NETWORK_MODES.has(normalized)) {
    throw new Error(
      `Sandbox security: network mode "${network}" is blocked. ` +
        'Network "host" mode bypasses container network isolation.'
    );
  }

  // Blocks "container:*" namespace joins by default
  if (normalized.startsWith("container:") && options?.allowContainerNamespaceJoin !== true) {
    throw new Error(
      `Sandbox security: network mode "${network}" is blocked by default. ` +
        'Network "container:*" joins another container namespace and bypasses sandbox network isolation.'
    );
  }
}
```

### 1.3 Default Network Configuration

**Key Finding:** By default, sandbox containers run with **no network access**:

```json
// Default sandbox docker config
{
  "agents": {
    "defaults": {
      "sandbox": {
        "docker": {
          "network": "none"  // No egress by default
        }
      }
    }
  }
}
```

---

## 2. The Ollama + Subagent Problem

### 2.1 Issue Description

**GitHub Issue #23827** - "Sub-agents with Ollama models timeout with no output"  
**GitHub Issue #24654** - "Subagent spawning fails with local Ollama models"

**Root Cause:** When subagents spawn with `local-automation` or any sandboxed agent type, they run inside Docker containers with isolated network namespaces. The Ollama API at `localhost:11434` on the host is unreachable from inside the container because:

1. `localhost` inside the container refers to the container's loopback, not the host's
2. The default network mode is `"none"` (no egress)
3. Even with `"bridge"` mode, the container gets its own IP and cannot reach host localhost

### 2.2 Diagnostic Evidence

From GitHub issue #24654:

```bash
# This works from host:
curl -s http://localhost:11434/api/generate \
  -d '{"model":"llama3.2:latest","prompt":"test","stream":false}'

# Subagent with Ollama model fails:
sessions_spawn({
  "task": "Reply TEST_OK",
  "model": "ollama/llama3.2:latest",
  "timeoutSeconds": 60
})
# Result: status "failed", runtimeMs: 168, no transcript
```

### 2.3 Control Tests

| Scenario | Model | Result |
|----------|-------|--------|
| Main session | `moonshot/kimi-k2.5` | ✅ Works |
| Main session | `ollama/llama3.2:latest` | ✅ Works |
| Subagent | `moonshot/kimi-k2.5` | ✅ Works |
| Subagent | `ollama/llama3.2:latest` | ❌ **Fails** |

**Conclusion:** Issue is specific to **subagent + local model combination**.

---

## 3. Documented Workarounds (Limited)

### 3.1 Official "Solution": Use API Models for Subagents

From GitHub issue #24654:

```bash
# Use cloud API models instead of local Ollama
sessions_spawn --model moonshot/kimi-k2.5  # Works reliably
```

**Cost:** ~$0.01-0.05 per subagent task

### 3.2 Disable Sandbox Mode Entirely

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "off"
      }
    }
  }
}
```

**WARNING:** This removes ALL sandbox protection. Use with extreme caution.

### 3.3 Use `agent:main` for Ollama Tasks

From TOOLS.md in workspace:

```markdown
### Model Routing Strategy
- **Kimi (k2p5):** Interactive conversations, complex coding, reasoning
- **Local models:** Automation, heartbeats, background tasks
- **Issue:** `local-automation` agent cannot use Ollama due to sandbox isolation
- **Workaround:** Use `agent:main` for Ollama tasks
```

---

## 4. Undocumented Workarounds & Hacks

### 4.1 Network Namespace Sharing (BROKEN/REMOVED)

**GitHub PR #41808** - "allow sandbox browser to access sandbox localhost via network namespace sharing"

This PR attempted to allow sandbox browser to access sandbox localhost via `--network=container:<id>` namespace sharing. However, it was **closed without merging** due to security concerns:

> "Closing this. Network namespace sharing (`--network container:<id>`) exposes the browser's CDP port on the sandbox container's localhost, allowing the exec tool to directly access CDP and read all credentials (cookies including httpOnly, localStorage, sessionStorage) from the browser."

**Status:** NOT a viable workaround.

### 4.2 Browser Bridge Binding Hack

**GitHub Issue #8273** - "Sandbox browser unreachable from agent container"

For browser-specific localhost access, there's a hack to bind the bridge to `0.0.0.0`:

```bash
# Make bridge listen on all interfaces
sed -i 's/return await startBrowserBridgeServer({/return await startBrowserBridgeServer({\n host: "0.0.0.0",/' $(find /path/to/openclaw -name "browser.js" -path "*/sandbox/*")

# Advertise the Docker bridge IP instead of localhost
sed -i 's/const baseUrl = `http:\/\/${host}:${resolvedPort}`;/const baseUrl = `http:\/\/${host === "0.0.0.0" ? "172.17.0.1" : host}:${resolvedPort}`;/' $(find /path/to/openclaw -name "bridge-server.js" -path "*/browser/*")

openclaw gateway restart
openclaw sandbox recreate --browser --all --force
```

**Note:** This is for browser tool only, not general Ollama access.

### 4.3 Custom Bridge Network with Host Access

**Theoretical approach** (not confirmed working):

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "docker": {
          "network": "host.docker.internal",
          "extraHosts": ["host.docker.internal:host-gateway"]
        }
      }
    }
  }
}
```

**Issue:** On Windows, `host.docker.internal` may not work as expected in all Docker configurations.

---

## 5. Windows-Specific Issues & Solutions

### 5.1 Windows Node Approval Socket Bug

**GitHub Issue #20386** - "Node host approval socket not responding on Windows/WSL"

Windows nodes have a **completely broken** exec-approvals named pipe mechanism:

```
exec denied: approval timed out
```

**Status:** Confirmed bug in OpenClaw 2026.3.24. No user-side workaround available.

### 5.2 WSL2 + OpenClaw Gateway

**GitHub Issue #39214** - "Browser relay binds to 127.0.0.1 only — unreachable from Windows host when running in WSL2"

When running OpenClaw Gateway in WSL2, services bind to `127.0.0.1` which is unreachable from Windows host.

**Workaround using socat:**

```bash
# Inside WSL2 - forward LAN IP to loopback
socat TCP-LISTEN:18792,bind=<WSL2_LAN_IP>,fork,reuseaddr TCP:127.0.0.1:18792
```

**Better Fix:** Set `browser.relayBindHost: "0.0.0.0"` in config (added in PR #39364).

### 5.3 Docker Desktop on Windows

**GitHub Issue #4941** - "Dashboard 'pairing required' when running gateway in Docker Desktop on Windows"

Docker Desktop on Windows has specific networking limitations that affect sandbox functionality.

---

## 6. Process-Level vs Docker Isolation

### 6.1 Current Implementation

OpenClaw uses **Docker containers** for sandboxing, NOT process-level isolation:

```
┌─────────────────────────────────────────┐
│           Host System                   │
│  ┌─────────────────────────────────┐    │
│  │     OpenClaw Gateway            │    │
│  │  (runs on host)                 │    │
│  └─────────────────────────────────┘    │
│              │                          │
│  ┌───────────┴───────────┐              │
│  │   Docker Engine       │              │
│  │  ┌───────────────┐    │              │
│  │  │   Sandbox     │    │              │
│  │  │   Container   │    │              │
│  │  │  (isolated    │    │              │
│  │  │   network)    │    │              │
│  │  └───────────────┘    │              │
│  └───────────────────────┘              │
└─────────────────────────────────────────┘
```

### 6.2 Why Not Process Isolation?

From the documentation:

> "This is not a perfect security boundary, but it materially limits filesystem and process access when the model does something dumb."

Docker provides:
- Network namespace isolation
- Filesystem isolation (overlayfs)
- Process namespace isolation
- Resource limits (cgroups)

Process-level isolation (like `nsjail` or `firejail`) would provide similar isolation but OpenClaw chose Docker for portability.

---

## 7. Environment Variables & Hidden Configs

### 7.1 Known Environment Variables

From the documentation:

| Variable | Purpose |
|----------|---------|
| `OPENCLAW_SANDBOX` | Enable sandbox in Docker deployments |
| `OPENCLAW_DOCKER_SOCKET` | Override Docker socket location |
| `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS` | Disable GPU flags for browser |
| `OPENCLAW_BROWSER_DISABLE_EXTENSIONS` | Allow browser extensions |
| `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT` | Control Chromium renderer processes |

### 7.2 Hidden/Dangerous Config Options

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "docker": {
          "dangerouslyAllowContainerNamespaceJoin": true,
          "dangerouslyAllowExternalBindSources": true,
          "dangerouslyAllowReservedContainerTargets": true
        }
      }
    }
  }
}
```

**WARNING:** These are explicitly marked as "dangerous" in the code and bypass security protections.

### 7.3 Sandbox Browser Specific Config

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "browser": {
          "allowHostControl": true,
          "cdpSourceRange": "172.21.0.1/32",
          "network": "openclaw-sandbox-browser"
        }
      }
    }
  }
}
```

---

## 8. Security Advisories & Patches

### 8.1 GHSA-ww6v-v748-x7g9

**Published:** Feb 25, 2026  
**Affected:** openclaw <= 2026.2.23  
**Patched:** >= 2026.2.24

**Summary:** Sandbox network isolation bypass via `docker.network=container:<id>`

In versions <= 2026.2.23, setting `network: "container:<id>"` allowed sandbox containers to join another container's network namespace and reach services available in that namespace.

**Fix:** Block `container:*` namespace joins by default (commit `14b6eea6e`).

### 8.2 2026.2.24 Security Changes

From the changelog:

> **BREAKING:** Security/Sandbox: block Docker `network: "container:<id>"` namespace-join mode by default for sandbox and sandbox-browser containers.

---

## 9. Successful User Reports

### 9.1 Confirmed Working Configurations

| Configuration | Local Ollama | Subagent Ollama | Notes |
|--------------|--------------|-----------------|-------|
| `sandbox.mode: "off"` | ✅ | ✅ | No isolation |
| `sandbox.mode: "non-main"` + `agent:main` | ✅ | ✅ | Main agent only |
| `sandbox.mode: "non-main"` + `local-automation` | ✅ | ❌ | **BROKEN** |
| `sandbox.mode: "all"` | ❌ | ❌ | All sandboxed |

### 9.2 Community Workarounds

From GitHub issue #24654 comments:

> "Pretty much same experience using Ollama qwen3.5. Looks like the Ollama implementation is not functioning as expected. Will need to test with llama.cpp or vllm."

Alternative: Use `llama.cpp` or `vllm` instead of Ollama - may have different networking behavior.

---

## 10. Key Source Code References

### 10.1 Sandbox Security Validation

**File:** `src/agents/sandbox/validate-sandbox-security.ts`

Key functions:
- `validateNetworkMode()` - Blocks host and container:* modes
- `validateSandboxSecurity()` - Main validation entry point
- `BLOCKED_NETWORK_MODES` - Set containing "host"

### 10.2 Sandbox Docker Configuration

**File:** `src/config/types.sandbox.ts`

```typescript
export type SandboxDockerSettings = {
  image?: string;
  network?: string;
  user?: string;
  readOnlyRoot?: boolean;
  binds?: string[];
  dangerouslyAllowReservedContainerTargets?: boolean;
  dangerouslyAllowExternalBindSources?: boolean;
  dangerouslyAllowContainerNamespaceJoin?: boolean;
};
```

### 10.3 Sandbox Mode Resolution

**File:** `src/agents/sandbox/config.ts`

```typescript
export function resolveSandboxMode(params: {
  session: { mainKey?: string };
  config: { mode?: SandboxMode };
}): "off" | "sandbox" {
  const mode = params.config.mode ?? "off";
  if (mode === "off") return "off";
  if (mode === "all") return "sandbox";
  // mode === "non-main"
  const isMain = params.session.mainKey === "main";
  return isMain ? "off" : "sandbox";
}
```

---

## 11. Conclusions & Recommendations

### 11.1 The Core Problem

OpenClaw's sandbox isolation is **working as designed** - it intentionally prevents sandboxed containers from accessing host localhost services. This is a security feature, not a bug.

### 11.2 Available Options

| Option | Security | Feasibility | Recommendation |
|--------|----------|-------------|----------------|
| Use `agent:main` for Ollama | Lower | ✅ Easy | **Recommended** |
| Use API models for subagents | N/A | ✅ Easy | Cost-effective for small tasks |
| Disable sandbox entirely | ❌ None | ⚠️ Risky | Not recommended |
| Run Ollama in container | Medium | ❌ Complex | Would require custom setup |
| Wait for official fix | N/A | ⏳ Unknown | No timeline available |

### 11.3 Recommended Configuration

For Windows 11 with Ollama:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "ollama/qwen2.5:14b",
        "fallbacks": ["moonshot/kimi-k2.5"]
      },
      "sandbox": {
        "mode": "non-main"
      }
    },
    "list": [
      {
        "id": "main",
        "model": {
          "primary": "ollama/qwen2.5:14b"
        },
        "sandbox": {
          "mode": "off"
        }
      },
      {
        "id": "local-automation",
        "model": {
          "primary": "moonshot/kimi-k2.5"
        }
      }
    ]
  }
}
```

**Note:** The `local-automation` agent should use API models since sandbox prevents Ollama access.

### 11.4 Future Investigation

Potential areas to explore:

1. **Docker Desktop WSL2 backend** - May have different networking behavior
2. **Custom Ollama container** - Run Ollama in a container on the same Docker network
3. **OpenClaw feature request** - Request `dangerouslyAllowHostNetwork` option (see GitHub issue #54537)
4. **Proxy container** - Create a bridge container that forwards to host Ollama

---

## 12. References

### GitHub Issues
- #23827 - Sub-agents with Ollama models timeout
- #24654 - Subagent spawning fails with local Ollama models
- #11905 - Fails to connect to local Ollama provider
- #8273 - Sandbox browser unreachable from agent container
- #33989 - Sandbox browser SSRF policy blocks localhost
- #41808 - Network namespace sharing PR (closed)
- #54537 - Feature request: dangerouslyAllowHostNetwork
- #20386 - Windows node approval socket bug
- #39214 - WSL2 browser relay binding issue

### Documentation
- https://openclaws.io/docs/gateway/sandboxing
- https://github.com/openclaw/openclaw/security/advisories/GHSA-ww6v-v748-x7g9

### Commits
- `14b6eea6e` - Block container namespace joins by default
- `5552f9073` - Centralize network mode policy helpers

---

*Research compiled by Karen on 2026-04-13*
