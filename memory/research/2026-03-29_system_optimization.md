# OpenClaw System Optimization Research
**Date:** 2026-03-29
**System:** Windows 11 with 24GB RAM, OpenClaw + Ollama hybrid setup
**Goal:** Reduce API costs while maintaining functionality

---

## Executive Summary

Based on research from multiple sources, users can reduce OpenClaw API costs by **80-97%** through strategic model routing, local LLM integration, and context optimization. For a Windows 11 system with 24GB RAM and Ollama, the following optimizations are most impactful:

---

## 1. OpenClaw Performance Tuning on Windows

### Key Findings

**Session Initialization Optimization (80% reduction in startup costs):**
```
SESSION INITIALIZATION:
On session start, load ONLY:
- SOUL.md
- USER.md
- IDENTITY.md
- memory/[TODAY].md

DO NOT auto-load:
- MEMORY.md
- Session history
- Previous outputs
```

**Context File Management:**
- Keep SOUL.md under 500-1000 words (currently may be bloated)
- Trim MEMORY.md regularly - archive old memories
- Load only today + yesterday's daily notes, not full week
- Move task-specific instructions to individual skills

**Impact:** Reducing context from 8,000 tokens to 3,000 tokens saves ~5,000 input tokens per call. At 48 heartbeats/day with Sonnet pricing: **$21.60/month saved** just from trimming files.

### Windows-Specific Considerations
- Ollama on Windows includes built-in GPU acceleration
- Native Windows experience available since February 2024
- Full model library access on Windows

---

## 2. Ollama Optimization for 24GB RAM Systems

### Model Size Guidelines for 24GB RAM

| Model Size | RAM Required | Suitable For |
|------------|--------------|--------------|
| 3B (Llama 3.2 3B) | ~2-3GB | Heartbeats, simple classification, routing |
| 7B (Qwen 2.5 7B) | ~4-5GB | General tasks, code-adjacent work |
| 8B (Llama 3.1 8B) | ~5-6GB | Better quality general tasks |
| 14B (Qwen 2.5 14B) | ~9-10GB | Currently installed - good balance |
| 70B | ~40GB | NOT suitable for 24GB system |

**Recommendation for 24GB RAM:**
- Keep qwen2.5:14b (9GB) as primary local model
- Add llama3.2:3b for ultra-fast heartbeats
- Can run multiple smaller models concurrently

### Ollama Configuration Best Practices

**For Heartbeats (Free):**
```json
{
  "heartbeat": {
    "every": "30m",
    "model": "ollama/llama3.2:3b",
    "session": "main",
    "prompt": "Status check: any updates needed?"
  }
}
```

**Impact:** 100% elimination of heartbeat costs (~$40-60/month)

### Quantization Strategy
- Use 4-bit quantization for larger models
- Qwen 2.5 Coder 7B in 4-bit = ~4-5GB RAM
- Mistral 7B = reasonable general-purpose option

---

## 3. Reducing API Costs While Maintaining Functionality

### Model Tiering Strategy (The Biggest Cost Saver)

**Cost Comparison (per 1M tokens):**
| Model | Input Cost | Output Cost | Use Case |
|-------|------------|-------------|----------|
| Claude Opus | $15.00 | $75.00 | Complex architecture only |
| Claude Sonnet | $3.00 | $15.00 | Complex analysis, writing |
| GPT-4o | $2.50 | $10.00 | General reasoning |
| DeepSeek V3 | $0.27 | ~$1.10 | Good middle ground |
| Gemini Flash | $0.075 | $0.30 | Heartbeats, simple tasks |
| Claude Haiku | $0.25 | $1.25 | Simple tasks, drafts |
| Ollama (local) | FREE | FREE | Heartbeats, routine tasks |

**Price ratio:** Opus is 60x more expensive than Haiku for input tokens.

### Recommended Configuration

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-haiku-4-5"
      },
      "models": {
        "anthropic/claude-sonnet-4-5": {
          "alias": "sonnet"
        },
        "anthropic/claude-haiku-4-5": {
          "alias": "haiku"
        }
      }
    }
  }
}
```

### Task Classification for Model Selection

**Tier 1 - Cheap/Local (Haiku/Gemini Flash/Ollama):**
- Heartbeats and status checks
- Summarizing text
- Formatting and reformatting
- Filing and categorizing
- Simple drafts and templates
- Data extraction from structured text
- Yes/no decisions and classifications

**Tier 2 - Mid-range (Sonnet/GPT-4o):**
- Writing that needs to be good
- Multi-step analysis
- Research synthesis
- Code review and debugging
- Complex document editing

**Tier 3 - Premium (Opus/o1):**
- Deep research requiring nuanced reasoning
- Complex architectural decisions
- Tasks where errors have real consequences
- Creative work where quality is paramount

**Reality check:** 70-80% of tasks fall into Tier 1.

### Real-World Cost Examples

| Setup | Monthly Cost | Tasks/Day |
|-------|--------------|-----------|
| Claude Opus for everything | $80-150 | 50-100 |
| Claude Sonnet for everything | $15-30 | 50-100 |
| Haiku default + Sonnet for writing | $5-12 | 50-100 |
| Ollama + Sonnet for complex tasks | $3-8 | 50-100 |
| Ollama only | $0 | Unlimited |

### Before vs After Optimization

**Before (common beginner setup):**
- Heartbeats (every 15 min, Claude Sonnet): $17.28/month
- Messages (~30/day, Sonnet): $8.10/month
- Complex tasks (~5/day, Sonnet): $13.50/month
- Cron jobs (~10/day, Sonnet): $5.40/month
- **Total: $44.28/month**

**After optimization:**
- Heartbeats (every 30 min, DeepSeek V3): $0.39/month
- Messages (~30/day, DeepSeek V3): $0.81/month
- Complex tasks (~5/day, Claude Sonnet cached): $4.05/month
- Cron jobs (~10/day, DeepSeek V3): $0.54/month
- **Total: $5.79/month**

**Result: 87% reduction** — from $44 to under $6/month.

---

## 4. Subagent Sandbox Workarounds or Alternatives

### The Problem (Confirmed)
- `local-automation` agent cannot use Ollama due to sandbox isolation
- Cron jobs with `local-automation` + Ollama fail with timeout
- OpenClaw 2026.2.24 did not fix this issue

### Workarounds

**1. Use `agent:main` for Ollama Tasks**
- Switch heartbeat to `agent:main` instead of `local-automation`
- Main agent can reach localhost services (Ollama)
- Trade-off: Less isolation, but functional

**2. Disable Default Heartbeat, Use Explicit Cron Jobs**
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "0"
      }
    }
  }
}
```

Then add explicit cron jobs with controlled model selection:
```bash
openclaw cron add --schedule "0 * * * *" \
  --model ollama/qwen2.5:14b \
  --task "Check email via himalaya, summarize urgent unread"
```

**3. Use Isolated Sessions for Cron Jobs**
```json
{
  "name": "daily-status-check",
  "schedule": "0 9 * * *",
  "model": "ollama/llama3.2:3b",
  "session": "isolated"
}
```

Isolated sessions start clean with no history, run the task, and terminate - cheaper and cleaner.

**4. LiteLLM Proxy as Middleware**
- Set up LiteLLM proxy for caching and fallback handling
- Can route to Ollama for local models
- Adds caching layer for repeated prompts

```yaml
services:
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    command: "--detailed_debug --cache yes"
```

---

## 5. Memory/Embedding Optimization Strategies

### Prompt Caching

**Anthropic's prompt caching:**
- Cached input tokens: $0.30/1M (vs $3.00 for Sonnet regular input)
- **90% discount** on cached portions
- OpenClaw's system prompts (SOUL.md, AGENTS.md) are largely static

**Configuration:**
```json
{
  "agents": {
    "defaults": {
      "cache": {
        "enabled": true,
        "ttl": "5m",
        "priority": "high"
      }
    }
  }
}
```

**Cache Strategy:**
- ✅ Cache: SOUL.md, USER.md, reference docs (stable content)
- ❌ Don't cache: Daily notes, recent messages, tool outputs (dynamic)
- 🔄 Batch similar tasks within 5-minute windows

### Retrieval-First Architecture (MemoryLake Approach)

Instead of loading full files into context:
1. Process and store large documents once in a memory layer
2. Retrieve only relevant chunks (often just 5% of original file)
3. Inject only what's needed into the prompt

**Impact:** Up to 90% reduction in file-heavy workflows.

### Context Compaction

**Problem:** Long sessions are expensive because token costs compound with history length. A 40-turn session sends early messages as input tokens on every subsequent turn.

**Solutions:**
1. **Aggressive compaction:** Prune history while preserving summary
2. **Session resets:** End session, write important info to MEMORY.md, start fresh
3. **Use `--session isolated` for cron jobs:** No accumulated history

### Rate Limiting & Budget Controls

**Add to system prompt:**
```
RATE LIMITS:
- Min 5s between API calls
- Min 10s between web searches
- Max 5 searches/batch, then 2min break
- Batch similar operations
- On 429 error: stop, wait 5min, retry

BUDGETS:
- Daily: $5 max (warn at $4)
- Monthly: $180 max (warn at $140)
```

**Set spending caps at API provider:**
- Anthropic: Console → Settings → Usage Limits
- OpenAI: Platform → Settings → Limits

---

## 6. Consolidated Automation Strategy

**Problem:** 10 automations running hourly = 240 API calls/day even if most return "nothing to report"

**Solution - Batch Instead of Poll:**

Instead of:
- Check email every hour (24 calls/day)
- Monitor website every 2 hours (12 calls/day)
- Check social mentions every hour (24 calls/day)
- Summarize news every 4 hours (6 calls/day)
- **Total: 66 API calls/day**

Do this:
- Single "morning briefing" at 8 AM (1 call/day)
- "Afternoon check" at 2 PM (1 call/day)
- One real-time alert for urgent items (2-3 calls/day)
- **Total: 4-5 API calls/day**

**Result: 92% reduction** - same information, batched instead of polled.

---

## 7. Actionable Implementation Plan

### Week 1: Quick Wins (30 minutes)
1. ✅ Switch default model to Haiku or Gemini Flash
2. ✅ Add session initialization rules to system prompt (load only essential files)
3. ✅ Increase heartbeat interval to 30+ minutes
4. ✅ Trim SOUL.md to under 1000 words

### Week 2: Local LLM Setup (15 minutes)
1. ✅ Ensure Ollama is running with appropriate models
2. ✅ Configure heartbeat to use Ollama (llama3.2:3b for heartbeats)
3. ✅ Update cron jobs to use local models where possible
4. ✅ Switch from `local-automation` to `agent:main` for Ollama tasks

### Week 3: Monitoring & Limits (10 minutes)
1. ✅ Add rate limits to system prompt
2. ✅ Set budget alerts at provider dashboards
3. ✅ Set monthly cap at $15-20

### Week 4: Advanced Optimization (20 minutes)
1. ✅ Enable prompt caching in config
2. ✅ Reorganize workspace files (stable vs dynamic)
3. ✅ Consolidate automations into 2-3 daily batches
4. ✅ Review and archive old MEMORY.md entries

---

## 8. Expected Results

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Session loading | $70-90/mo | $5-10/mo | 90% |
| Model usage | $700-900/mo | $80-100/mo | 90% |
| Heartbeat | $40-60/mo | $0 | 100% |
| Prompt caching | Full price | 90% off | Variable |
| **Total** | **$1,200+/mo** | **~$50/mo** | **96%** |

**Realistic target for current setup:** $15-30/month (down from potential $50-100+)

---

## 9. Key Takeaways

1. **Cheap model for routine, smart model for complexity** - This one rule saves more than everything else combined
2. **Heartbeats are the biggest expense** - Optimize frequency and model choice there first
3. **Local models are free** - Use Ollama for heartbeats and simple tasks
4. **Cache-friendly context** - Keep system files stable and concise
5. **Batch similar tasks** - Consolidate automations, reduce polling frequency
6. **Monitor spending** - Check API dashboard weekly, set hard caps

---

## Sources

- [How to Reduce Your OpenClaw API Costs by 80%](https://openclawai.io/blog/reduce-openclaw-api-costs/)
- [OpenClaw Cost Optimization Guide](https://docs.bswen.com/blog/2026-03-21-openclaw-cost-optimization-guide/)
- [OpenClaw Token Optimization GitHub](https://github.com/wassupjay/OpenClaw-Token-Optimization)
- [Managing OpenClaw API Costs: Under $15/Month](https://openclawdesktop.com/blog/managing-openclaw-api-costs.html)
- [Reduce OpenClaw LLM Costs by 90%](https://www.powerdrill.ai/blog/how-to-reduce-openclaw-llm-costs)
- [OpenClaw Cost Optimization & Budgeting](https://lumadock.com/tutorials/openclaw-cost-optimization-budgeting)
- [Ollama Blog](https://ollama.com/blog)

---

*Research compiled for Windows 11 + 24GB RAM + Ollama hybrid setup*
