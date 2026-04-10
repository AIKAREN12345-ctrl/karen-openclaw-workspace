# OpenClaw + Ollama Native Integration Research

**Date:** 2026-04-07  
**Researcher:** Karen (subagent)  
**Topic:** Current status, issues, and solutions for Ollama integration with OpenClaw in 2026

---

## Executive Summary

OpenClaw has **mature native Ollama integration** as of 2026, with official support for both local and cloud models. However, **sandbox isolation creates connectivity issues** for subagents and cron jobs attempting to reach localhost Ollama instances. This is a known architectural limitation, not a bug.

---

## 1. Current Integration Status (2026)

### Native API Support
- OpenClaw integrates with Ollama's **native API** (`/api/chat`), NOT the OpenAI-compatible `/v1` endpoint
- Full support for **streaming** and **tool calling** simultaneously
- **Auto-discovery** of local Ollama models when `OLLAMA_API_KEY` is set

### Setup Methods

#### Quick Start (Recommended)
```bash
openclaw onboard
# Select Ollama → choose Local or Cloud + Local
```

#### Manual Setup
```bash
export OLLAMA_API_KEY="ollama-local"
# Or: openclaw config set models.providers.ollama.apiKey "ollama-local"
```

#### One-Command Launch (Ollama 0.17+)
```bash
ollama launch openclaw --model kimi-k2.5:cloud
```

### Recommended Models (2026)

**Cloud Models** (via Ollama cloud):
- `kimi-k2.5:cloud` - Multimodal reasoning with subagents
- `minimax-m2.5:cloud` - Fast coding and productivity
- `glm-5:cloud` - Reasoning and code generation

**Local Models** (requires GPU VRAM):
- `glm-4.7-flash` (~25 GB) - Reasoning and code generation
- `qwen3-coder` (~25 GB) - Efficient all-purpose assistant
- `gemma4` - New local default (replacing llama3.3)

---

## 2. Critical Issue: Sandbox Isolation Blocks Localhost Access

### The Problem

Subagents (including `local-automation` agents used in cron jobs) run in **Docker sandbox containers** with `network: "none"` by default. This prevents them from accessing:
- `localhost:11434` (Ollama default)
- `127.0.0.1:11434`
- Any host-local services

### Evidence from GitHub Issues

**Issue #24654** - "Bug: Subagent spawning fails with local Ollama models"
- Subagents with Ollama models fail immediately (~168ms runtime)
- Same models work fine in main session
- Root cause: Subagent cannot reach Ollama API due to network isolation
- **Status:** Closed as fixed on main (March 2026) - fixes include subagent auth inheritance and model-path hardening

**Issue #23827** - "Sub-agents with Ollama models timeout with no output"
- Subagents timeout with `stopReason: "error"` and zero tokens
- Direct curl to Ollama works fine
- **Status:** Closed as "not planned" - tracked under broader Ollama workstream

### Sandbox Security Defaults

```typescript
// From OpenClaw sandbox source (src/agents/sandbox/config.ts)
{
  network: "none",        // No network access!
  readOnlyRoot: true,     // Read-only filesystem
  capDrop: ["ALL"],       // Drop all Linux capabilities
}
```

---

## 3. Solutions and Workarounds

### Solution 1: Use `agent:main` for Ollama Tasks

**Recommended approach** - Use the main agent instead of `local-automation` for Ollama-dependent tasks:

```json
// In cron job or subagent spawn
{
  "agent": "main",  // Instead of "local-automation"
  "model": "ollama/qwen2.5:14b"
}
```

**Why this works:** Main session runs on the host, not in a sandbox, so it can access localhost services.

### Solution 2: Configure Sandbox Network Access

**For Docker-based deployments only** - Modify sandbox config to allow network:

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        docker: {
          network: "bridge"  // WARNING: Reduces isolation
        }
      }
    }
  }
}
```

**Security Warning:** This reduces sandbox isolation. Only use if you understand the trade-offs.

### Solution 3: Use Ollama Cloud Models

Cloud models don't require local Ollama access:

```bash
ollama signin
# Then use: ollama/kimi-k2.5:cloud
```

### Solution 4: Run Ollama on Accessible Network Interface

If sandbox has bridge network, bind Ollama to host interface:

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

Then configure OpenClaw to use host IP instead of localhost.

---

## 4. Important Configuration Notes

### DO NOT Use `/v1` Endpoint

```json5
// WRONG - Breaks tool calling
{
  baseUrl: "http://localhost:11434/v1"
}

// CORRECT - Native Ollama API
{
  baseUrl: "http://localhost:11434"
}
```

### Auto-Discovery vs Explicit Config

**Auto-discovery** (recommended for simple setups):
- Set `OLLAMA_API_KEY` (any value)
- Don't define `models.providers.ollama`
- OpenClaw queries `/api/tags` and discovers models automatically

**Explicit config** (needed for remote Ollama or custom settings):
```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434",
        apiKey: "ollama-local",
        api: "ollama",
        models: [...]  // Must define manually
      }
    }
  }
}
```

---

## 5. Windows-Specific Considerations

From TOOLS.md (Karen's system):
- Ollama runs natively on Windows
- OpenClaw 2026.2.24 introduced stricter sandbox isolation
- `local-automation` agent cannot reach Ollama due to sandbox constraints
- **Confirmed workaround:** Use `agent:main` for Ollama tasks

---

## 6. Key Takeaways

1. **Ollama integration is mature and well-supported** - Official docs, onboarding wizard, cloud models
2. **Sandbox isolation is the root cause** of subagent + Ollama failures, not Ollama itself
3. **Use `agent:main` for Ollama tasks** - Simplest workaround for automation
4. **Avoid `/v1` endpoint** - Always use native Ollama API URL
5. **Consider cloud models** - If local sandbox issues persist, Ollama cloud models work reliably

---

## References

- [Official Ollama Provider Docs](https://docs.openclaw.ai/providers/ollama)
- [OpenClaw Sandbox Documentation](https://openclawlab.com/en/docs/gateway/sandboxing/)
- [GitHub Issue #24654](https://github.com/openclaw/openclaw/issues/24654) - Subagent Ollama failures
- [GitHub Issue #23827](https://github.com/openclaw/openclaw/issues/23827) - Subagent timeouts
- [Ollama Blog - OpenClaw Tutorial](https://ollama.com/blog/openclaw-tutorial) (Feb 2026)
- [OpenClaw Book - Sandbox Mechanism](https://www.openclawbook.xyz/en/ch24-security-model/24.3-sandbox-mechanism)

---

*Research compiled by Karen subagent for Ken's OpenClaw system analysis.*
