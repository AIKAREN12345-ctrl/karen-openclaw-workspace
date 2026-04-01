# HEARTBEAT.md

## Research Automation (Ollama Mode)

**Schedule (5 runs per day):**
- **06:00** — OpenClaw updates (morning briefing)
- **12:00** — AI models check (midday)
- **18:00** — AI models check (evening)
- **20:00** — Philosophy/personal growth
- **22:00** — AI income opportunities

**Note:** Research uses Ollama with Qwen 3.5 via OpenClaw subagents.

---

### How It Works
1. **Ollama** runs with Qwen 3.5 model
2. **Pre-warm** cron jobs load model 3 minutes before research
3. **Research cron job** spawns subagent with tools
4. Subagent uses `web_search`, `web_fetch`, etc. to research
5. Results saved to `memory/research/YYYY-MM-DD_[topic].md`

---

### Ollama Model Management

**Keepalive:** Hourly (keeps model warm)
**Pre-warm:** 3 minutes before each research job
- 05:57 → 06:00 research
- 11:57 → 12:00 research
- 17:57 → 18:00 research
- 19:57 → 20:00 research
- 21:57 → 22:00 research

---

### TRIGGER-RESEARCH-OpenClaw-AI
- **Scheduled:** 06:00 (1x daily)
- **Action:** Research OpenClaw updates
- **Subagent:** Uses web_search, web_fetch
- **Timeout:** 180s

### TRIGGER-RESEARCH-AI-models  
- **Scheduled:** 12:00, 18:00 (2x daily)
- **Action:** Research AI model releases
- **Subagent:** Uses web_search
- **Timeout:** 180s

### TRIGGER-RESEARCH-AI-income
- **Scheduled:** 22:00 (1x daily)
- **Action:** Research AI income opportunities
- **Subagent:** Uses web_search
- **Timeout:** 180s

### TRIGGER-RESEARCH-philosophy
- **Scheduled:** 20:00 (1x daily)
- **Action:** Research philosophy/personal growth
- **Subagent:** Uses web_search
- **Timeout:** 180s

### TRIGGER-RESEARCH-RESET
- **Scheduled:** 00:00 (midnight)
- **Action:** Reset daily run counters
- **Direct Execution:** No subagent needed

---

## Morning Memory Load (Daily at 08:00)
- Run: python C:\Users\Karen\.openclaw\workspace\skills\local-llm\morning_memory_loader.py
- Purpose: Auto-load yesterday's conversations and system status
- No user prompt needed - runs automatically

---

## System Architecture

**Two-System Setup:**

| System | Model | Use Case |
|--------|-------|----------|
| **Kimi** | K2.5 | Interactive conversations, complex tasks |
| **Ollama** | Qwen 3.5 | Automated research subagents |

**Why Qwen 3.5:**
- Proven working with OpenClaw subagents
- Full tool support (web_search, browser, exec)
- Reliable (was working yesterday!)

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

## Troubleshooting

**Subagent timeout:**
- Normal for first run (cold-start ~60-90s)
- Pre-warm jobs should prevent this
- Check if Ollama is running: `ollama ps`

**Empty research output:**
- Check if model is loaded: `ollama ps`
- Try running keepalive manually
- Check OpenClaw logs

**Model not found:**
- Ensure Qwen 3.5 is pulled: `ollama pull qwen3.5:9b`

---

## History

**2026-04-01:** Reverted to working setup
- Ollama + Qwen 3.5 (was working yesterday)
- Removed LM Studio from automation
- Simplified to two-system architecture

**Yesterday (2026-03-31):** System was working perfectly
- Generated full philosophy research
- All subagents completed successfully

---

*Last updated: 2026-04-01*
