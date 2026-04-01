# HEARTBEAT.md

## Research Trigger Handlers (LM Studio Mode)

**Schedule (5 runs per day):**
- **06:00** — OpenClaw updates (morning briefing)
- **12:00** — AI models check (midday)
- **18:00** — AI models check (evening)
- **20:00** — Philosophy/personal growth
- **22:00** — AI income opportunities

**Note:** Research now uses LM Studio with subagents. No pre-warm needed - model stays loaded in LM Studio!

---

### How It Works
1. **LM Studio** runs continuously with model loaded
2. **Research cron job**: Spawns subagent with 60s timeout (no pre-warm needed!)
3. Subagent executes research using `web_fetch`
4. Results saved to `memory/research/YYYY-MM-DD_[topic].md`
5. `research-state.json` updated with timestamp

---

### TRIGGER-RESEARCH-OpenClaw-AI
- **Scheduled:** 06:00 (1x daily)
- **Action:** Research OpenClaw updates
- **Subagent Spawn:**
  ```
  sessions_spawn {
    task: "Research OpenClaw updates using web_fetch...",
    model: "lmstudio/qwen2.5-14b-instruct",
    timeoutSeconds: 60
  }
  ```

### TRIGGER-RESEARCH-AI-models  
- **Scheduled:** 12:00, 18:00 (2x daily)
- **Action:** Research AI model releases
- **Subagent Spawn:** 60s timeout, LM Studio model

### TRIGGER-RESEARCH-AI-income
- **Scheduled:** 22:00 (1x daily)
- **Action:** Research AI income opportunities
- **Subagent Spawn:** 60s timeout, LM Studio model

### TRIGGER-RESEARCH-philosophy
- **Scheduled:** 20:00 (1x daily)
- **Action:** Research philosophy/personal growth
- **Subagent Spawn:** 60s timeout, LM Studio model

### TRIGGER-RESEARCH-RESET
- **Scheduled:** 00:00 (midnight)
- **Action:** Reset daily run counters
- **Direct Execution:** No subagent needed

---

## Morning Memory Load (Daily at 08:00)
- Run: python C:\Users\Karen\.openclaw\workspace\skills\local-llm\morning_memory_loader.py
- Purpose: Auto-load yesterday's conversations and system status
- No user prompt needed - runs automatically

## Ollama Keepalive (DISABLED)
- **Status:** Disabled as of 2026-04-01
- **Reason:** Now using LM Studio which keeps models loaded automatically
- **Ollama still available:** Can cold-start if needed for specific tasks

---

## Research Output Format

All research files use this format:
```markdown
## [Topic] Research - YYYY-MM-DD HH:MM

- Finding 1 (with source if available)
- Finding 2 (with source if available)
- Finding 3 (with source if available)
```

---

## Notes

### LM Studio Configuration (2026-04-01)
**Status:** ✅ Fully operational

**Setup:**
- LM Studio v0.4.8 installed
- Local Server running on port 1234
- Qwen 2.5 14B loaded (8.99 GB)
- OpenAI-compatible API enabled

**Performance:**
- Subagent response time: 14-51ms (vs 60-90s Ollama cold-start)
- No pre-warm needed - model stays loaded
- No auth issues - uses standard OpenAI API format
- Tool use capability confirmed

**OpenClaw Config:**
- Provider: `lmstudio` with `openai-completions` API
- Model: `qwen2.5-14b-instruct`
- Fallback chain: lmstudio → ollama

### Research Schedule
| Time | Action |
|------|--------|
| 06:00 | Research: OpenClaw |
| 12:00 | Research: AI Models |
| 18:00 | Research: AI Models |
| 20:00 | Research: Philosophy |
| 22:00 | Research: AI Income |

### Model Strategy
- **Interactive chat:** LM Studio `qwen2.5-14b-instruct` (free, local, always loaded)
- **Research subagents:** LM Studio with 60s timeout (no pre-warm!)
- **Embeddings:** `nomic-embed-text` (free, local, for memory search)
- **Backup:** Ollama available for cold-start if needed

### Migration from Ollama
**Old system:**
- Ollama with 60-90s cold-start
- Pre-warm cron jobs every 3 hours
- 180s timeout for subagents
- Complex auth workarounds

**New system:**
- LM Studio with model always loaded
- No pre-warm needed
- 60s timeout sufficient
- Standard OpenAI API

**Result:** Faster, simpler, more reliable! 🚀
