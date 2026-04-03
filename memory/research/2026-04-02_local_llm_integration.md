# Comprehensive Report: Local LLM Integration with OpenClaw for Subagents and Automation

**Research Date:** 2026-04-02  
**OpenClaw Version:** 2026.4.1  
**Report Status:** Comprehensive Analysis

---

## Executive Summary

This report provides an in-depth analysis of using local LLMs (primarily via Ollama) with OpenClaw, focusing on the critical sandboxing architecture issues that prevent `local-automation` agents from accessing local LLM services. The research covers current limitations, known workarounds, alternative approaches, and future roadmap considerations.

**Key Finding:** The primary blocker is OpenClaw's Docker-based sandbox isolation, which prevents subagents from reaching localhost services like Ollama. This is a documented architectural limitation, not a bug.

---

## 1. Current OpenClaw Architecture for Subagent Sandboxing (2026.4.1)

### 1.1 Sandboxing Overview

OpenClaw implements Docker-based sandboxing to isolate tool execution and reduce security blast radius. According to the official documentation:

> "OpenClaw can run tools inside sandbox backends to reduce blast radius. This is optional and controlled by configuration (`agents.defaults.sandbox` or `agents.list[].sandbox`). If sandboxing is off, tools run on the host. The Gateway stays on the host; tool execution runs in an isolated sandbox when enabled."

### 1.2 Sandbox Modes

| Mode | Description |
|------|-------------|
| `"off"` | No sandboxing; all tools run on host |
| `"non-main"` | Sandbox only non-main sessions (default recommendation) |
| `"all"` | Every session runs in a sandbox |

### 1.3 The Core Problem: Network Isolation

**Critical Issue:** By default, Docker sandbox containers run with **no network access** (`network: "none"`). This is intentional for security but creates a fundamental conflict with local LLM usage:

- Ollama runs on `localhost:11434` (or `127.0.0.1:11434`)
- Sandboxed agents cannot reach the host's localhost
- The Gateway (on host) can reach Ollama, but subagents (in containers) cannot

From the docs:
> "By default, Docker sandbox containers run with **no network**. Override with `agents.defaults.sandbox.docker.network`."

### 1.4 Security Constraints

OpenClaw enforces strict network security:

- `network: "host"` is **blocked** (intentionally)
- `network: "container:<id>"` is blocked by default
- Break-glass override exists: `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`

---

## 2. Known Workarounds for Local LLM Integration

### 2.1 Workaround #1: Use `agent:main` Instead of `local-automation`

**Current Best Practice:** The most reliable workaround is to use `agent:main` for Ollama-dependent tasks.

**How it works:**
- `agent:main` runs on the host (not in a sandbox)
- Has full access to localhost services
- Can reach Ollama at `http://127.0.0.1:11434`

**Configuration Example:**
```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/qwen2.5-coder:32b",
        fallbacks: ["ollama/llama3.3"]
      }
    }
  }
}
```

**Trade-offs:**
- ✅ Works reliably with Ollama
- ✅ No sandbox isolation issues
- ❌ Loses sandbox security benefits
- ❌ Not suitable for untrusted/remote triggers

### 2.2 Workaround #2: Configure Docker Network Access

**Approach:** Modify sandbox network configuration to allow container-to-host communication.

**Option A: Use Docker Bridge Network**
```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          network: "bridge"  // Allows external network access
        }
      }
    }
  }
}
```

**Option B: Use Host Gateway (Linux only)**
```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          network: "bridge",
          extraHosts: ["host.docker.internal:host-gateway"]
        }
      }
    }
  }
}
```

**Then configure Ollama to bind to `0.0.0.0`:**
```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

**Trade-offs:**
- ✅ Allows sandboxed agents to reach Ollama
- ❌ Reduces security isolation
- ❌ Requires Ollama to listen on all interfaces (security risk)
- ❌ `host.docker.internal` doesn't work reliably on all platforms

### 2.3 Workaround #3: Run Ollama in Docker on Shared Network

**Approach:** Run Ollama as a Docker container on the same Docker network as OpenClaw sandboxes.

**Setup:**
```bash
# Create shared network
docker network create openclaw-ollama

# Run Ollama on shared network
docker run -d --name ollama \
  --network openclaw-ollama \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  ollama/ollama

# Configure OpenClaw to use same network
```

**OpenClaw Configuration:**
```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          network: "openclaw-ollama"
        }
      }
    }
  },
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama:11434"  // Docker DNS name
      }
    }
  }
}
```

**Trade-offs:**
- ✅ Sandboxed agents can reach Ollama
- ✅ Maintains some isolation
- ❌ More complex setup
- ❌ Ollama container must be managed separately
- ❌ Potential performance overhead

### 2.4 Workaround #4: Use SSH Backend for Remote Execution

**Approach:** Use OpenClaw's SSH sandbox backend to offload execution to a machine with Ollama.

**Configuration:**
```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "ssh",
        scope: "session",
        workspaceAccess: "rw",
        ssh: {
          target: "user@ollama-host:22",
          workspaceRoot: "/tmp/openclaw-sandboxes"
        }
      }
    }
  }
}
```

**Trade-offs:**
- ✅ Sandboxed execution on remote host
- ✅ Remote host can run Ollama locally
- ❌ Requires separate machine
- ❌ Browser sandboxing not supported
- ❌ More infrastructure to maintain

### 2.5 Workaround #5: Disable Sandboxing for Specific Agents

**Approach:** Disable sandboxing entirely for agents that need Ollama access.

**Configuration:**
```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "off"  // Disable sandboxing
      }
    }
  }
}
```

Or per-agent:
```json5
{
  agents: {
    list: [
      {
        id: "local-llm-agent",
        sandbox: {
          mode: "off"
        }
      }
    ]
  }
}
```

**Trade-offs:**
- ✅ Simplest solution
- ✅ Full localhost access
- ❌ Loses all sandbox security
- ❌ Not recommended for production

---

## 3. Alternative Local LLM Approaches

### 3.1 LM Studio

**Overview:** GUI-based local LLM runner with OpenAI-compatible API

**Setup with OpenClaw:**
```json5
{
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192
          }
        ]
      }
    }
  }
}
```

**Pros:**
- Better GUI for model management
- OpenAI-compatible API
- Good for experimentation

**Cons:**
- Same sandboxing issues as Ollama (localhost access)
- Not headless (requires GUI)
- Limited to desktop use

### 3.2 vLLM

**Overview:** High-performance inference engine for production use

**Setup:**
```bash
# Install vLLM
pip install vllm

# Run server
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-4-8B-Instruct \
  --port 8000
```

**OpenClaw Configuration:**
```json5
{
  models: {
    providers: {
      vllm: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses"
      }
    }
  }
}
```

**Pros:**
- Production-grade performance
- OpenAI-compatible API
- Supports many models

**Cons:**
- Same localhost access issues
- Requires more setup
- Higher resource requirements

### 3.3 LocalAI

**Overview:** Drop-in OpenAI API replacement for local models

**Pros:**
- OpenAI API compatible
- Supports multiple backends
- Docker deployment available

**Cons:**
- Same network isolation challenges
- Less mature than Ollama

### 3.4 llama.cpp

**Overview:** Low-level C++ implementation for maximum efficiency

**Setup:**
```bash
# Build llama.cpp
make

# Run server
./server -m models/llama-4.gguf --port 8080
```

**Pros:**
- Maximum performance
- Minimal dependencies
- Highly customizable

**Cons:**
- Manual model management
- No automatic tool calling support
- Requires more technical knowledge

---

## 4. Trade-offs: Cost vs Complexity vs Capabilities

### 4.1 Cost Analysis

| Approach | Upfront Cost | Monthly Cost | Notes |
|----------|-------------|--------------|-------|
| **Cloud API (Claude/ChatGPT)** | $0 | $3-200 | Pay per token; most reliable |
| **Local GPU (RTX 4090)** | $1,600 | ~$30 electricity | One-time hardware cost |
| **Local GPU (AMD RX 7900 XTX)** | $1,000 | ~$25 electricity | Requires ROCm setup |
| **CPU-only (no GPU)** | $0 | ~$10 electricity | Very slow; limited models |
| **Cheap Cloud (DeepSeek)** | $0 | $3-8 | Good middle ground |
| **Gemini Free Tier** | $0 | $0 | 1,500 requests/day limit |

### 4.2 Complexity Analysis

| Approach | Setup Complexity | Maintenance | Reliability |
|----------|-----------------|-------------|-------------|
| **Cloud API** | Low | Low | High |
| **Ollama + OpenClaw** | Medium | Medium | Medium |
| **Ollama + Sandbox Workaround** | High | High | Low-Medium |
| **vLLM** | High | High | Medium |
| **LM Studio** | Low | Low | Medium |

### 4.3 Capabilities Analysis

| Model Size | Tool Calling | Reasoning | Context Window | Best For |
|------------|-------------|-----------|----------------|----------|
| **< 8B params** | Poor | Poor | 32K | Simple chat only |
| **8-14B params** | Fair | Fair | 64K | Basic tasks |
| **30B+ params** | Good | Good | 128K+ | Agent operations |
| **70B+ params** | Excellent | Excellent | 128K+ | Complex reasoning |

**Key Insight:** Models under 30B parameters struggle with reliable tool calling for OpenClaw agent operations. Community benchmarks consistently show that local models need 30B+ parameters for reliable agent tasks.

---

## 5. Specific Solutions for Windows 11 with AMD GPU

### 5.1 Ollama on Windows 11 with AMD GPU

**Current Status:** Ollama supports AMD GPUs on Windows via ROCm, but setup is more complex than NVIDIA.

**Supported AMD GPUs (as of 2026):**
- Radeon RX 7900 XTX, 7900 XT, 7900 GRE
- Radeon RX 7800 XT, 7700 XT, 7600 XT
- Radeon RX 6900 XT, 6800 XT, 6700 XT
- Radeon RX 9070 XT (newer series)

**Installation Steps:**

1. **Install AMD ROCm drivers:**
   - Download from AMD's official website
   - ROCm v6.1+ required for Windows

2. **Install Ollama:**
   ```powershell
   # Download from https://ollama.com
   # Run installer
   ```

3. **Verify GPU detection:**
   ```powershell
   ollama run llama3.2
   # Check GPU utilization in Task Manager
   ```

### 5.2 Windows-Specific Sandbox Considerations

**WSL2 Networking Issues:**
- If running OpenClaw in WSL2 and Ollama on Windows host, `127.0.0.1` doesn't resolve correctly
- Use WSL2 IP address instead: `hostname -I` in WSL2
- Or bind Ollama to `0.0.0.0` (less secure)

**Docker Desktop on Windows:**
- `host.docker.internal` should work for container-to-host communication
- Requires Docker Desktop 18.03+

### 5.3 Recommended Windows Setup

**Option A: Native Windows (Recommended)**
- Run both OpenClaw and Ollama on native Windows
- Use `agent:main` for Ollama tasks
- No WSL2 networking complications

**Option B: WSL2 with Network Bridge**
```json5
// OpenClaw config for WSL2
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://host.docker.internal:11434"
      }
    }
  }
}
```

**PowerShell to bind Ollama to all interfaces:**
```powershell
$env:OLLAMA_HOST="0.0.0.0:11434"
ollama serve
```

---

## 6. Future Roadmap: OpenClaw Plans for Local LLM Support

### 6.1 Known GitHub Issues

Several GitHub issues track local LLM improvements:

| Issue | Description | Status |
|-------|-------------|--------|
| #5769 | Tool calling breaks with streaming for Ollama | Open - streaming bug |
| #31399 | Local Ollama models hang/timeout | Partially fixed in 2026.3.8 |
| #41871 | Retest of #31399 - still reproduces | Open |
| #43946 | Configurable LLM timeout per provider | Open |
| #2252 | Configurable Ollama connection timeout | Open |
| #52818 | Ollama cold-start timeout causes fallback | Open |

### 6.2 OpenClaw 2026.4.1 Release Notes

Recent release (April 2026) includes:
- GLM 5.1 integration with non-looping failover
- AWS Bedrock Guardrails integration
- `/tasks` feature for agent task logging
- Per-job cron tool allowlists
- 40+ stability and execution fixes

**Notably absent:** No specific fixes for local LLM sandboxing issues in this release.

### 6.3 Community Proposals

**Proposed but not yet implemented:**

1. **Provider-level streaming control:**
   ```javascript
   // Proposed config
   const shouldStream = !(context.tools?.length && isOllamaProvider(model))
   ```

2. **Sandbox network profiles:**
   - Predefined network configurations for common setups
   - "local-llm" profile that allows localhost access

3. **Local LLM discovery improvements:**
   - Better auto-discovery for Ollama
   - Retry logic for slow-starting local models

### 6.4 Expected Timeline

Based on GitHub activity and community discussions:

- **Short term (2026 Q2):** Better timeout configuration, improved error messages
- **Medium term (2026 Q3):** Potential streaming fixes for Ollama
- **Long term (2026 Q4+):** Possible first-class local LLM sandboxing support

---

## 7. Recommendations

### 7.1 For Immediate Use (Today)

**Best Approach:** Use `agent:main` for Ollama-dependent automation tasks

1. Configure Ollama as primary model for main agent
2. Keep cloud providers as fallbacks
3. Accept that subagents will use cloud models

### 7.2 For Budget-Conscious Users

**Hybrid Approach:**
- Use cheap cloud providers (DeepSeek, Gemini free tier) for subagents
- Use local Ollama for main agent interactive work
- Total cost: $0-10/month

### 7.3 For Privacy-First Deployments

**Full Local Setup:**
- Disable sandboxing: `mode: "off"`
- Run everything on host
- Accept security trade-offs
- Or use Docker network workarounds with careful firewall rules

### 7.4 For Production Use

**Recommended:**
- Use cloud providers for reliability
- If local is required, use vLLM or LM Studio with proper infrastructure
- Implement health checks and fallback chains
- Consider dedicated GPU servers rather than consumer hardware

---

## 8. Configuration Examples

### 8.1 Minimal Working Config (agent:main)

```json5
// ~/.openclaw/openclaw.json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/qwen2.5:14b",
        fallbacks: ["anthropic/claude-sonnet-4-6"]
      }
    }
  }
}
```

### 8.2 Hybrid Cloud/Local Config

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["ollama/qwen2.5:14b", "anthropic/claude-opus-4-6"]
      }
    },
    list: [
      {
        id: "heartbeat",
        model: {
          primary: "ollama/qwen2.5:14b"
        }
      }
    ]
  },
  models: {
    mode: "merge"
  }
}
```

### 8.3 Docker Network Workaround Config

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        docker: {
          network: "bridge"
        }
      },
      model: {
        primary: "ollama/qwen2.5:14b"
      }
    }
  },
  models: {
    providers: {
      ollama: {
        baseUrl: "http://host.docker.internal:11434"
      }
    }
  }
}
```

---

## 9. Troubleshooting Checklist

### 9.1 Ollama Not Responding

- [ ] Is Ollama running? `curl http://localhost:11434`
- [ ] Is the model loaded? Check with `ollama list`
- [ ] Is the model name exact? Check with `ollama list`
- [ ] Is Ollama bound to the right interface? Try `OLLAMA_HOST=0.0.0.0:11434`

### 9.2 Subagent Timeout Issues

- [ ] Is sandbox mode enabled? Check `openclaw sandbox explain`
- [ ] Can the sandbox reach Ollama? Test network configuration
- [ ] Is the timeout too short? Check agent timeout settings
- [ ] Is the model too large for available VRAM?

### 9.3 Tool Calling Not Working

- [ ] Does the model support tools? Check Ollama documentation
- [ ] Is streaming disabled? Some models require `streaming: false`
- [ ] Is the model large enough? < 8B models often fail at tool calling

---

## 10. References

### Official Documentation
- [OpenClaw Sandboxing](https://docs.openclaw.ai/gateway/sandboxing)
- [OpenClaw Local Models](https://docs.openclaw.ai/gateway/local-models)
- [Ollama Provider Setup](https://open-claw.bot/docs/providers/ollama/)

### GitHub Issues
- [#5769](https://github.com/openclaw/openclaw/issues/5769) - Tool calling streaming bug
- [#31399](https://github.com/openclaw/openclaw/issues/31399) - Local Ollama timeout
- [#41871](https://github.com/openclaw/openclaw/issues/41871) - Retest of timeout issue

### Community Resources
- [BetterClaw Local Model Guide](https://www.betterclaw.io/blog/openclaw-local-model-not-working)
- [Clawctl Local LLM Complete Guide](https://www.clawctl.com/blog/openclaw-local-llm-complete-guide)
- [AMD Ollama Setup Guide](https://www.amd.com/en/developer/resources/technical-articles/running-llms-locally-on-amd-gpus-with-ollama.html)

---

## Conclusion

The integration of local LLMs (Ollama) with OpenClaw subagents is currently limited by the sandboxing architecture. The most reliable solution today is using `agent:main` for Ollama-dependent tasks, accepting the trade-off of reduced isolation.

For users requiring both sandboxing and local LLMs, the Docker network workarounds provide a path forward but require careful security consideration. The community and OpenClaw maintainers are aware of these limitations, and improvements are expected in future releases.

**Bottom line:** Local LLMs work well with OpenClaw for interactive use via `agent:main`. For automated subagents, cloud providers remain the most reliable option until sandboxing improvements are implemented.

---

*Report compiled from official OpenClaw documentation, GitHub issues, community guides, and technical analysis.*
