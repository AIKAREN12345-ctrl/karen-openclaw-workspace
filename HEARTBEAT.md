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
4. Subagent uses `web_fetch` with DuckDuckGo to research
   - Format: `https://duckduckgo.com/html?q={query}`
   - Parse results, fetch interesting pages
   - Compile findings into markdown
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
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)
- **Search Method:** `https://duckduckgo.com/html?q={query}`

### TRIGGER-RESEARCH-AI-models  
- **Scheduled:** 12:00, 18:00 (2x daily)
- **Action:** Research AI model releases
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)
- **Search Method:** `https://duckduckgo.com/html?q={query}`

### TRIGGER-RESEARCH-AI-income
- **Scheduled:** 22:00 (1x daily)
- **Action:** Research AI income opportunities
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)
- **Search Method:** `https://duckduckgo.com/html?q={query}`

### TRIGGER-RESEARCH-philosophy
- **Scheduled:** 20:00 (1x daily)
- **Action:** Research philosophy/personal growth
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)
- **Search Method:** `https://duckduckgo.com/html?q={query}`

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

**Research Setup:**

| System | Model | Use Case |
|--------|-------|----------|
| **Kimi** | K2.5 | Interactive + automated research subagents |
| **Ollama** | Qwen 3.5 | Local tasks (sandboxed from subagents) |

**Why Kimi for Research:**
- Subagents can use web_fetch, browser, exec tools
- No sandbox restrictions (cloud API)
- Reliable and fast
- Costs ~2-5k tokens per research run

**Search Method:**
- Uses DuckDuckGo HTML interface via `web_fetch`
- Format: `https://duckduckgo.com/html?q={query}`
- No API keys needed, no auth errors
- Replace spaces with `+` in queries

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

**2026-04-02:** Switched to Kimi for research subagents
- Ollama sandboxed from subagents in 2026.4.1
- Kimi subagents work reliably with full tool access
- Updated all research triggers to use Kimi k2.5

**Yesterday (2026-03-31):** System was working perfectly
- Generated full philosophy research
- All subagents completed successfully

---

*Last updated: 2026-04-01*
