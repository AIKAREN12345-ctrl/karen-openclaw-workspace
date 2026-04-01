# Deep Research: Fully Local OpenClaw Systems (Updated)

**Research Date:** March 31, 2026  
**Sources:** OpenClaw official docs + Community guides via DuckDuckGo  
**Scope:** Complete offline/self-hosted deployment without cloud dependencies

---

## Executive Summary

**Fully local OpenClaw is not only possible — it's actively supported and widely deployed.** Since March 2026, Ollama became an official OpenClaw provider, making setup dramatically simpler. The community has converged on a **hybrid approach** as the practical sweet spot: local models for 60-80% of tasks (cheap, private, fast), cloud APIs for the hard 20% (complex reasoning).

---

## 1. Why Go Local? (Community Consensus)

Three pain points drive local adoption:

| Pain Point | Cloud Cost | Local Solution |
|------------|-----------|----------------|
| **Money** | $40-60/month for background agents | ~$15/month electricity + hardware |
| **Latency** | 200ms network hops hurt automation loops | Local inference eliminates round-trips |
| **Privacy** | Compliance teams veto third-party LLMs | Nothing leaves the machine |

**Real user experience** (Medium guide, Feb 2026):
> "I was running a handful of OpenClaw agents — log summaries, calendar management, message routing. Nothing that required frontier intelligence. But the tokens added up fast. $40/month, then $60... I pulled the plug on cloud APIs for everything except the hard stuff. My bill dropped to about $15/month in electricity."

---

## 2. Hardware Requirements (Real-World Tested)

### Official OpenClaw Recommendation
- **≥2 maxed-out Mac Studios or equivalent GPU rig**
- **Cost:** ~$30k+
- **Why:** Large context + strong prompt injection defenses

### Community Reality Check
Multiple users report practical setups with consumer hardware:

| Component | Minimum | Recommended | Premium |
|-----------|---------|-------------|---------|
| **RAM** | 16GB (7B models) | 32GB (headroom for browser + DB) | 64GB+ (Mixtral, 70B models) |
| **GPU** | CPU-only (slower) | RTX 3060 12GB ($400 used) | RTX 4090 24GB |
| **VRAM** | N/A | 8GB+ (halves latency vs CPU) | 48GB+ (Coder Plus, 70B models) |
| **Disk** | SSD (15GB per 7B model) | SSD (40GB for 70B models) | NVMe for faster loading |
| **CPU** | 8 logical cores | Intel i5 11th-gen / Apple Silicon | Ryzen 5700X+ |

### Your Current Setup Analysis
| Component | Your Config | Assessment |
|-----------|-------------|------------|
| RAM | 24GB | ✅ Good — above minimum, below ideal |
| GPU | None (CPU) | ⚠️ Bottleneck — 10-50x slower than GPU |
| Storage | SSD | ✅ Adequate |
| OS | Windows 11 | ✅ Supported (WSL2 for Ollama) |

**Verdict:** Your setup works for local deployment but will be CPU-bound. Consider a GPU upgrade for better performance.

---

## 3. Best Local Models for OpenClaw (2026 Rankings)

Based on SWE-bench scores, tool-calling reliability, and real-world agent performance:

| Model | Parameters | VRAM | SWE-bench | Speed (RTX 4090) | Best For |
|-------|-----------|------|-----------|------------------|----------|
| **Qwen3.5 27B** | 27B dense | 20GB+ | 72.4% | ~40 t/s | **Best quality-to-size ratio** |
| **Qwen3.5 9B** | 9B dense | 8GB+ | — | ~80 t/s | Entry-level, simple tasks |
| **Qwen3.5 35B-A3B** | 35B (3B MoE) | 16GB+ | — | ~112 t/s | Speed-critical work |
| **Qwen3 Coder Plus** | 72B dense | 48GB+ | 70.6% | ~25 t/s | Hardest coding tasks |
| **Llama 3.3 70B** | 70B dense | 48GB+ | — | ~20 t/s | General coding |

### Key Insight: Qwen3.5 Changed the Math
> "Qwen3.5 27B hitting 72.4% on SWE-bench puts it in the same range as GPT-5 Mini — an open-weight model on a single consumer GPU matching a cloud model you'd pay per token to use." — Haimaker AI

**Your optimal choice:** Qwen3.5 9B (already configured) — runs on your 24GB RAM without GPU, though slower.

---

## 4. Complete Local Setup Guide

### Step 1: Install Ollama

**macOS:**
```bash
brew install ollama
ollama serve &
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable --now ollama
```

**Windows (WSL2):**
Use Linux steps inside WSL2. GPU passthrough is hit-or-miss; CPU works but slower.

**Verify:**
```bash
curl http://localhost:11434/api/tags
```

### Step 2: Pull Models
```bash
# Your current models
ollama pull qwen3.5:9b      # Your primary — fits your RAM
ollama pull qwen2.5:14b     # Your fallback

# Optional upgrades (if you get GPU)
ollama pull qwen3.5:27b     # Best quality-to-size
ollama pull qwen3.5:35b-a3b # Fast MoE model
```

**Smoke test:**
```bash
ollama run qwen3.5:9b "Why does the sky look blue?"
```
Expect ~2.5s first token on CPU, ~800ms on GPU.

### Step 3: Configure OpenClaw

**Option A: Onboarding Wizard (Recommended)**
```bash
openclaw onboard --auth-choice ollama
```

**Option B: Manual Config** (your current setup)
```json5
// ~/.openclaw/openclaw.json
{
  "models": {
    "mode": "merge",
    "providers": {
      "ollama": {
        "baseUrl": "http://127.0.0.1:11434",
        "apiKey": "ollama-local",
        "api": "ollama",
        "models": [
          {
            "id": "qwen3.5:9b",
            "name": "Qwen 3.5 9B",
            "reasoning": true,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 131072,
            "maxTokens": 8192
          },
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
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "ollama/qwen3.5:9b",
        "fallbacks": ["ollama/qwen2.5:14b"]
      },
      "models": {
        "ollama/qwen3.5:9b": { "alias": "local" },
        "ollama/qwen2.5:14b": { "alias": "fallback" }
      }
    }
  }
}
```

---

## 5. The Hybrid Approach (Community Consensus)

**This is the actual answer** — not 100% local, but optimal:

```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "ollama/qwen3.5:9b",
        "fallbacks": ["kimi-coding/k2p5"],  // Cloud for hard stuff
        "thinking": "kimi-coding/k2p5"      // Complex reasoning
      }
    }
  }
}
```

### What Goes Local (60-80% of tasks):
- Log summarization
- JSON extraction/parsing
- Simple message routing
- Calendar operations
- Shell command generation
- Structured data transformation
- File reads, boilerplate generation
- Simple refactoring

### What Goes to Cloud (20-40%):
- Multi-step chain-of-thought reasoning (2+ steps)
- Complex debugging across abstraction layers
- Multi-file refactors (5+ files)
- Niche languages (Rust macros, HLSL)
- Multilingual beyond EN/FR/ES
- Very long context (200K+)

**Cost impact:** $40/month → $15 electricity + $5-10 API = **~60% savings**

---

## 6. Performance Benchmarks

Real measurements (Ryzen 5700X, RTX 3060 12GB, 32GB RAM):

| Model | GPU (t/s) | CPU (t/s) | RAM Footprint |
|-------|-----------|-----------|---------------|
| Llama 3 8B | 15.2 | 4.1 | 9.2 GB |
| Mistral 7B | 17.8 | 4.3 | 8.8 GB |
| Mixtral 8×7B | 9.6 | 1.7 | 23.4 GB |
| GPT-4 Turbo (cloud) | 38.0 | — | — |

**Your expected performance (CPU-only, qwen3.5:9b):**
- ~4-5 tokens/second
- 2-3s time-to-first-token
- Usable for async tasks, painful for interactive coding

---

## 7. Sandboxing for Security

Local models skip cloud safety filters. **Sandboxing is critical.**

### Docker Sandbox Setup
```bash
# Build sandbox image
scripts/sandbox-setup.sh

# Or full-featured version
scripts/sandbox-common-setup.sh
```

### Configuration
```json5
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main",     // Sandbox non-main sessions
        "scope": "session",     // One container per session
        "workspaceAccess": "none",
        "docker": {
          "image": "openclaw-sandbox:bookworm-slim",
          "network": "none",      // No network by default
          "readOnlyRoot": true
        }
      }
    }
  }
}
```

### Security Best Practices
1. **Use largest model variants possible** (avoid heavily quantized "small" versions)
2. **Keep agents narrow** — limit tool access
3. **Enable compaction** — limit context window exposure
4. **Never set maxRetries** when local (hammers same machine)

---

## 8. Cost Comparison: Real Numbers

### Monthly Costs (1M tokens/day)

| Approach | Cost | Notes |
|----------|------|-------|
| **Cloud-only (GPT-4)** | ~$40/month | Convenience, best quality |
| **Local-only (GPU)** | ~$15/month | $11 hardware + $0.011/hr electricity |
| **Hybrid** | ~$15-20/month | Local bulk + cloud for hard tasks |
| **Your setup (CPU)** | ~$5/month | Electricity only, slower |

### Break-Even Analysis
- **High volume** (>500K tokens/day): Local wins
- **Casual use** (<100K tokens/day): Cloud is simpler
- **Privacy required**: Local regardless of cost

---

## 9. Troubleshooting (Community-Tested)

| Issue | Solution |
|-------|----------|
| **Model loads slowly/crashes** | Out of memory — try smaller quantization (Q4_K_M) |
| **Tool calls fail** | Set `"reasoning": false`, use Qwen3.5 models, update Ollama |
| **Context window errors** | Set accurate `contextWindow` (128K for Qwen3.5 on 24GB+) |
| **Slow generation (<20 t/s)** | Close browser tabs using WebGL/video, check GPU competition |
| **Ollama not detected** | `ollama serve` + verify `localhost:11434/api/tags` |
| **0/200k tokens** | Context window mismatch — lower `contextWindow` in config |

---

## 10. Advanced: Multi-Agent Local Deployment

### Architecture
```
Gateway (Local)
├── Agent: "personal" (Your main assistant)
├── Agent: "automation" (Cron jobs, background tasks)
└── Agent: "coding" (Code-specific, sandboxed)
```

### Per-Agent Model Routing
```json5
{
  "agents": {
    "list": [
      {
        "id": "personal",
        "workspace": "~/.openclaw/workspace-personal",
        "model": { "primary": "ollama/qwen3.5:9b" }
      },
      {
        "id": "automation",
        "workspace": "~/.openclaw/workspace-automation",
        "model": { "primary": "ollama/qwen2.5:14b" },
        "sandbox": { "mode": "all", "scope": "agent" }
      }
    ]
  }
}
```

---

## 11. Migration Path: Your Current Setup → Fully Local

### Step-by-Step
1. ✅ **Ollama configured** — already done
2. ✅ **Local models pulled** — qwen3.5:9b, qwen2.5:14b
3. ✅ **Config updated** — primary set to local
4. ⏳ **Restart OpenClaw** — `openclaw restart`
5. ⏳ **Test** — verify responses come from local model
6. ⏳ **Optional** — Remove Kimi from fallbacks once satisfied
7. ⏳ **Optional** — Enable sandboxing for security

### Your Specific Action Items
- [ ] Restart OpenClaw to apply config changes
- [ ] Test local-only mode: `/model local`
- [ ] Monitor performance — acceptable for your use case?
- [ ] Consider GPU upgrade if latency is painful
- [ ] Document final config in TOOLS.md

---

## 12. Key Takeaways

### ✅ What's Working Now
- Ollama is an **official provider** (since March 2026)
- Qwen3.5 models **rival cloud quality** on consumer hardware
- **Hybrid approach** is the community standard
- Your 24GB RAM setup **can run local models**

### ⚠️ Tradeoffs to Accept
- **CPU inference is slow** (~4-5 t/s vs 40+ t/s on GPU)
- **Local models weaker** on complex reasoning
- **You're your own ops team** — updates, monitoring, troubleshooting

### 🎯 Recommendation for Your System
1. **Keep current setup** — qwen3.5:9b as primary
2. **Use hybrid routing** — local for simple tasks, Kimi for hard ones
3. **Consider GPU upgrade** — RTX 3060 12GB (~$400 used) transforms experience
4. **Enable sandboxing** — especially for non-main sessions

---

## Sources

1. **OpenClaw Official Docs**
   - Local Models: https://docs.openclaw.ai/gateway/local-models
   - Ollama Provider: https://docs.openclaw.ai/providers/ollama
   - Configuration: https://docs.openclaw.ai/gateway/configuration

2. **Community Guides (via DuckDuckGo)**
   - "How to run OpenClaw completely offline with Ollama" — Medium, Feb 2026
   - "OpenClaw local models setup: run completely offline" — RunLobster, Jan 2025
   - "Best Ollama Models for OpenClaw (2026)" — Haimaker AI, Mar 2026

3. **Reddit/Community Wisdom**
   - r/LocalLLaMA — llama.cpp vs Ollama performance discussions
   - Multiple user reports on hardware configurations

---

*Research compiled using DuckDuckGo search + web_fetch workaround for Kimi API issues.*
