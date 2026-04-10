# Cloud to Local AI Migration: Best Practices Guide

**Research Date:** 2026-04-08  
**Current Stack:** OpenClaw + Kimi (cloud), Ollama (8 local models), CrewAI, ChromaDB, LangChain-Ollama, SearXNG, Open WebUI

---

## Executive Summary

This guide outlines best practices for migrating from cloud-based AI (Kimi) to a fully local AI stack using Ollama and OpenClaw. The migration can be done gradually or via hard switch, with proper fallback mechanisms to ensure continuity of service.

---

## 1. Gradual Migration vs Hard Switch

### Gradual Migration (Recommended)

A phased approach reduces risk and allows for iterative testing and optimization.

**Phase 1: Shadow Mode (Week 1-2)**
- Run local models in parallel with cloud models
- Compare outputs without affecting production
- Log performance metrics (latency, quality, token usage)
- Use OpenClaw's routing rules to duplicate requests to both systems

**Phase 2: Selective Routing (Week 3-4)**
- Route low-risk, non-critical tasks to local models first
- Examples: simple Q&A, summarization, casual chat
- Keep cloud models for complex reasoning, coding, critical tasks
- Use keyword-based routing in OpenClaw

**Phase 3: Majority Local (Week 5-6)**
- Flip the ratio: 80% local, 20% cloud
- Reserve cloud for fallback and complex edge cases
- Monitor error rates and user satisfaction

**Phase 4: Full Local (Week 7+)**
- Complete switch to local stack
- Keep cloud configuration as emergency fallback

### Hard Switch

**When to Consider:**
- Immediate cost constraints
- Data privacy requirements (compliance deadline)
- Complete loss of trust in cloud provider

**Requirements:**
- Extensive pre-migration testing
- Confirmed local model capability for all use cases
- 24/7 monitoring during transition period
- Rollback plan ready

### OpenClaw Configuration for Gradual Migration

```json5
{
  models: {
    default: "kimi",  // Keep cloud as default initially
    
    providers: {
      // Cloud provider (current)
      kimi: {
        apiKey: "$env:KIMI_API_KEY",
        model: "k2p5",
        maxTokens: 4096,
      },
      
      // Local Ollama (target)
      ollama: {
        baseUrl: "http://localhost:11434",
        model: "qwen2.5:14b",  // Your best local model
        maxTokens: 4096,
        temperature: 0.7,
      },
    },
    
    // Routing rules for gradual migration
    routing: {
      rules: [
        {
          name: "Route simple queries to local",
          match: {
            keywords: ["hello", "hi", "weather", "time", "simple", "quick"],
          },
          provider: "ollama",
        },
        {
          name: "Route coding tasks to cloud (initially)",
          match: {
            keywords: ["code", "debug", "programming", "function", "class"],
          },
          provider: "kimi",
        },
      ],
      fallback: "kimi",
    },
  },
}
```

---

## 2. Fallback Mechanisms

### Automatic Failover Chain

Configure OpenClaw to automatically fall back when local models fail:

```json5
{
  models: {
    fallbackChain: [
      "ollama",      // Primary: Local model
      "kimi",        // Fallback: Cloud provider
    ],
    
    fallbackPolicy: {
      maxFailures: 2,           // Fail over after 2 consecutive failures
      recoveryInterval: 300,    // Try primary again after 5 minutes
      timeout: 30000,           // 30 second timeout for local models
      
      notification: {
        enabled: true,
        message: "Switched to {fallback} due to {reason}",
      },
    },
  },
}
```

### Trigger Conditions for Fallback

| Condition | Action |
|-----------|--------|
| Local model timeout (>30s) | Switch to cloud |
| Connection refused | Switch to cloud |
| Out of memory error | Switch to cloud |
| Rate limit (if using shared local resources) | Switch to cloud |
| Authentication failure | Return error (don't fallback) |
| Invalid prompt (4xx errors) | Return error (don't fallback) |

### Health Check Configuration

```json5
{
  llm_switch: {
    health_check: {
      interval_seconds: 30,
      timeout_ms: 2000,
      endpoint: "/v1/health",  // Ollama health endpoint
    },
  },
}
```

### Cost Control with Fallback

```json5
{
  models: {
    costControl: {
      dailyBudget: 5.0,           // $5/day for cloud fallback
      monthlyBudget: 50.0,
      onBudgetReached: "warn",    // Warn but don't block
      warningThreshold: 0.8,
    },
  },
}
```

---

## 3. Testing Local Models Before Full Switch

### Pre-Deployment Testing Checklist

**Functional Testing:**
- [ ] Tool calling capability (if using agent tools)
- [ ] Context window handling (test with long inputs)
- [ ] JSON/structured output generation
- [ ] Multi-turn conversation coherence
- [ ] System prompt adherence

**Performance Testing:**
- [ ] Measure tokens/second for different prompt sizes
- [ ] Test concurrent request handling
- [ ] Monitor GPU/CPU utilization
- [ ] Check memory usage patterns
- [ ] Latency under load (p50, p95, p99)

**Quality Testing:**
- [ ] Side-by-side output comparison with cloud model
- [ ] Human evaluation of 50+ representative queries
- [ ] Task-specific benchmarks (coding, reasoning, etc.)
- [ ] Edge case handling

### Benchmarking Script

```python
# benchmark_local.py
import requests
import time
import statistics

OLLAMA_URL = "http://localhost:11434/api/generate"
TEST_PROMPTS = [
    "Explain quantum computing in simple terms",
    "Write a Python function to sort a list",
    "Summarize the key points of machine learning",
    # Add your typical use cases
]

def benchmark_model(model_name, prompts):
    results = []
    
    for prompt in prompts:
        start = time.time()
        response = requests.post(OLLAMA_URL, json={
            "model": model_name,
            "prompt": prompt,
            "stream": False
        })
        elapsed = time.time() - start
        
        results.append({
            "prompt": prompt[:50],
            "latency": elapsed,
            "tokens": response.json().get("eval_count", 0),
        })
    
    latencies = [r["latency"] for r in results]
    print(f"Model: {model_name}")
    print(f"  Avg latency: {statistics.mean(latencies):.2f}s")
    print(f"  P95 latency: {statistics.quantiles(latencies, n=20)[18]:.2f}s")
    print(f"  Min/Max: {min(latencies):.2f}s / {max(latencies):.2f}s")
    
    return results

# Run benchmarks
for model in ["qwen2.5:14b", "qwen2.5:7b"]:
    benchmark_model(model, TEST_PROMPTS)
```

### Model Selection for Your Hardware

Based on your current setup (8 local models), prioritize testing:

| Model | VRAM Required | Best For | Test Priority |
|-------|--------------|----------|---------------|
| qwen2.5:14b | ~9GB | General tasks, coding | **High** |
| qwen2.5:7b | ~5GB | Quick tasks, lower latency | **High** |
| llama3.2 | ~3GB | Simple Q&A | Medium |
| mistral | ~7GB | Reasoning tasks | Medium |

### A/B Testing with OpenClaw

```json5
{
  models: {
    routing: {
      rules: [
        {
          name: "A/B Test: 50% local, 50% cloud",
          match: {
            // Use user ID hash or random assignment
            random: 0.5,
          },
          provider: "ollama",
        },
      ],
      fallback: "kimi",
    },
  },
}
```

---

## 4. Configuration Changes Needed

### OpenClaw Configuration Updates

**1. Add Ollama Provider:**

```json5
// ~/.openclaw/openclaw.json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://localhost:11434",
        model: "qwen2.5:14b",
        maxTokens: 4096,
        temperature: 0.7,
        timeout_ms: 60000,  // Higher timeout for local models
      },
    },
  },
}
```

**2. Configure Model Compatibility:**

Not all models support the same features. Configure compatibility flags:

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://localhost:11434",
        api: "openai-completions",  // Use OpenAI-compatible API
        models: [
          {
            id: "qwen2.5:14b",
            name: "Qwen 2.5 14B",
            api: "openai-completions",
            reasoning: true,
            input: ["text"],
            compat: {
              supportsToolCalling: true,
              supportsJSON: true,
              maxTokensField: "max_tokens",
            },
            cost: {
              input: 0,
              output: 0,
            },
            contextWindow: 32768,
            maxTokens: 4096,
          },
        ],
      },
    },
  },
}
```

**3. Update Agent Configuration:**

```json5
{
  agents: {
    defaults: {
      model: {
        provider: "ollama",  // Switch default to local
        id: "qwen2.5:14b",
      },
      fallbacks: [
        {
          provider: "kimi",
          model: "k2p5",
        },
      ],
    },
  },
}
```

**4. Environment Variables:**

```bash
# Add to your environment
export OLLAMA_HOST="localhost:11434"
export OLLAMA_NUM_PARALLEL=2  # Allow concurrent requests
export OLLAMA_MAX_LOADED_MODELS=2  # Keep multiple models in memory
```

### Ollama Configuration

**Modelfile for Custom Behavior:**

```dockerfile
FROM qwen2.5:14b

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 32768

SYSTEM """You are Karen, a helpful AI assistant running locally. 
You have access to tools and can help with various tasks.
Always be concise and accurate."""
```

Build and use:
```bash
ollama create karen-local -f ./Modelfile
ollama run karen-local
```

### Integration with Existing Tools

**CrewAI with Ollama:**

```python
from crewai import Agent, Task, Crew
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:14b",
    base_url="http://localhost:11434",
    temperature=0.7,
)

agent = Agent(
    role="Researcher",
    goal="Research topics thoroughly",
    backstory="You are an expert researcher",
    llm=llm,
)
```

**ChromaDB (no changes needed):**
- ChromaDB runs independently of the LLM
- Just ensure your embedding model is available locally

**SearXNG (no changes needed):**
- Search functionality remains the same
- Just update any search-related prompts to work with local LLM

**Open WebUI:**
- Already designed for Ollama
- Configure to use your local models

### Monitoring Configuration

Add logging for migration tracking:

```json5
{
  logging: {
    level: "info",
    modelUsage: true,  // Log which model handled each request
    fallbackEvents: true,  // Log all fallback occurrences
    performanceMetrics: true,  // Log latency, tokens/sec
  },
}
```

---

## 5. Migration Timeline & Checklist

### Week 1: Preparation
- [ ] Document current cloud usage patterns
- [ ] Set up Ollama with target models
- [ ] Run benchmark tests
- [ ] Configure OpenClaw with both providers
- [ ] Set up monitoring and alerting

### Week 2: Shadow Testing
- [ ] Enable parallel processing (shadow mode)
- [ ] Compare outputs daily
- [ ] Identify gaps in local model capability
- [ ] Tune prompts for local model

### Week 3: Selective Routing
- [ ] Enable routing rules for simple tasks
- [ ] Monitor error rates
- [ ] Gather user feedback
- [ ] Adjust routing rules

### Week 4: Expanded Routing
- [ ] Increase local model traffic to 50%
- [ ] Test all critical workflows
- [ ] Document any workarounds needed

### Week 5: Majority Local
- [ ] Switch to 80% local traffic
- [ ] Stress test the system
- [ ] Verify fallback mechanisms work

### Week 6: Full Migration
- [ ] Switch default to local model
- [ ] Keep cloud as fallback only
- [ ] Monitor for 1 week
- [ ] Document lessons learned

---

## 6. Troubleshooting Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Local model too slow | Insufficient GPU/CPU | Use smaller quantized model, or increase timeout |
| Tool calling fails | Model doesn't support tools | Use Qwen 2.5 or Llama 3.2+ with native tool support |
| Out of memory | Model too large for VRAM | Use Q4_K_M quantization, or smaller model |
| Connection refused | Ollama not running | Start with `ollama serve` |
| Inconsistent outputs | Temperature too high | Lower temperature to 0.3-0.5 for deterministic tasks |
| Context too long | Exceeds model context window | Truncate or summarize context before sending |

---

## 7. Cost-Benefit Analysis

### Cloud Costs (Current)
- Kimi API: ~$0.015-0.06 per 1K tokens
- Estimated monthly: $20-100 (depending on usage)

### Local Costs (One-time)
- Hardware: Already owned
- Electricity: ~$5-15/month (depending on GPU)
- **Break-even: Immediate** (hardware already purchased)

### Hidden Costs
- Maintenance time: 1-2 hours/week initially
- Troubleshooting: Higher initially, decreases over time
- Model updates: Manual management required

---

## Summary

**Recommended Approach:** Gradual migration over 4-6 weeks

**Key Success Factors:**
1. Thorough testing before any production traffic
2. Robust fallback mechanisms
3. Continuous monitoring and adjustment
4. User feedback collection

**Risk Mitigation:**
- Always keep cloud fallback configured
- Monitor fallback rates (high rates indicate local model issues)
- Have rollback plan ready
- Document all configuration changes

---

## References

- [OpenClaw Local LLM Guide](https://www.clawctl.com/blog/openclaw-local-llm-complete-guide)
- [OpenClaw Fallback LLMs](https://openclawforge.com/blog/how-to-implement-fallback-llms-in-openclaw/)
- [Ollama Setup Guide 2026](https://nerdleveltech.com/ollama-setup-guide-run-local-llms-like-a-pro-2026-edition)
- [OpenClaw Multi-Model Configuration](https://lzw.me/docs/opencodedocs/openclaw/openclaw/advanced/models-configuration/)
- [OpenClaw Model Routing](https://oepnclaw.com/en/tutorials/openclaw-multi-model-switch.html)
