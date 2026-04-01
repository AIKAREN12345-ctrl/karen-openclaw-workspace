# System Architecture - Final Configuration

**Date:** 2026-04-01
**Status:** ✅ Fully Operational

---

## Overview

Three-system architecture optimized for different use cases:

| System | Model | Purpose | Speed |
|--------|-------|---------|-------|
| **Kimi** | K2.5 | Interactive conversations | Cloud API |
| **LM Studio** | Qwen 3.5 | Direct API calls (text only) | ~55ms |
| **Ollama** | Qwen 2.5 | Subagents with tool use | ~60s cold-start |

---

## System 1: Kimi (OpenClaw)

**Use For:**
- Interactive conversations
- Complex reasoning tasks
- Tool use (browser, exec, file operations)
- Real-time assistance

**Configuration:**
- Provider: `kimi-coding/k2p5`
- Context: 262k tokens
- Tools: Full OpenClaw toolset

---

## System 2: LM Studio

**Use For:**
- Fast text generation
- Simple Q&A
- Content creation
- Automated research (via direct API)

**Configuration:**
- URL: http://localhost:1234
- Model: qwen/qwen3.5-9b
- Thinking mode: Disabled
- Response time: ~55ms

**Scripts:**
- `lm_studio_research.py` - Research automation
- `lm_research_runner.py` - Cron job wrapper

**Limitations:**
- Cannot use OpenClaw tools
- Cannot be used as subagent (integration bug)

---

## System 3: Ollama

**Use For:**
- OpenClaw subagents with tool access
- Complex automation requiring web_search, browser, exec
- Background tasks with full tool ecosystem

**Configuration:**
- Model: qwen2.5:14b
- Keepalive: Hourly
- Pre-warm: 5:57, 11:57, 17:57, 19:57, 21:57

**Why Qwen 2.5:**
- Proper tool support
- No thinking mode issues
- Reliable with OpenClaw subagents

---

## Research Automation Schedule

| Time | Topic | System | Output |
|------|-------|--------|--------|
| 06:00 | OpenClaw updates | Ollama subagent | memory/research/ |
| 12:00 | AI models | Ollama subagent | memory/research/ |
| 18:00 | AI models | Ollama subagent | memory/research/ |
| 20:00 | Philosophy | Ollama subagent | memory/research/ |
| 22:00 | AI income | Ollama subagent | memory/research/ |

---

## Quick Reference

**Fast text generation:**
```bash
python lm_studio_research.py test
```

**Research with LM Studio:**
```bash
python lm_studio_research.py ai_models
```

**Subagent with Ollama:**
```json
{
  "model": "ollama/qwen2.5:14b",
  "task": "Research...",
  "timeoutSeconds": 120
}
```

---

## Files

- `~/.openclaw/openclaw.json` - Main config
- `~/.openclaw/cron/jobs.json` - Cron jobs
- `lm_studio_research.py` - LM Studio research script
- `lm_research_runner.py` - Cron wrapper
- `HEARTBEAT.md` - System documentation

---

## Troubleshooting

**LM Studio not responding:**
- Check if running: `curl http://localhost:1234/api/v0/models`
- Restart LM Studio GUI

**Ollama slow:**
- Normal for first load (cold-start)
- Keepalive runs hourly to maintain warm state
- Pre-warm 3 minutes before research jobs

**Subagent empty response:**
- Ollama: Check if model loaded (`ollama ps`)
- LM Studio: Cannot be used as subagent (known issue)

---

## Migration Notes

**From:** Ollama-only with Qwen 3.5 (thinking issues)
**To:** Three-system hybrid

**Benefits:**
- 100x faster for simple text tasks (LM Studio)
- Reliable tool use (Ollama + Qwen 2.5)
- High-quality interactive help (Kimi)

---

*System configured and operational as of 2026-04-01*
