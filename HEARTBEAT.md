# HEARTBEAT.md

## Rate Limiting & Concurrency Controls (2026-04-14)

**Problem:** Morning API rate limit errors (07:03-08:42) due to burst requests
**Solution:** Implement staggered delays and concurrent subagent limits

### Concurrency Rules
- **Max concurrent subagents:** 1-2 at any time
- **Stagger delay:** 30-60 seconds between research job spawns
- **Retry backoff:** Exponential delay on failures (not immediate retry)

### Implementation
When processing RESEARCH-* triggers:
1. Check if another research subagent is currently running
2. If yes, delay spawn by 60 seconds
3. If API error occurs, wait 2 minutes before retry
4. Never spawn more than 2 subagents simultaneously

---

## Research Automation (Kimi Mode - 2026.4.8+)

**Schedule (8 runs per day - staggered 2-hour intervals with 60s delays):**
- **07:00** — AI self-improvement & best practices
- **09:00** — OpenClaw updates & system optimization  
- **11:00** — KDP coloring books & passive income
- **13:00** — AI content creation & productivity tools
- **15:00** — Local LLM developments & optimization
- **17:00** — AI security & privacy best practices
- **19:00** — Emerging AI technologies & frameworks
- **21:00** — Philosophy & personal growth

**Note:** Each job spawns 60 seconds after the previous one completes to avoid bursts

**Note:** All research uses Kimi K2.5 subagents. Ollama/local LLMs disabled (2026-04-08).

---

### How It Works
1. **Kimi K2.5** subagents handle all research
2. Subagent uses `web_fetch` with DuckDuckGo to research
   - Format: `https://duckduckgo.com/html?q={query}`
   - Parse results, fetch interesting pages
   - Compile findings into markdown
3. Results saved to `C:\Users\Karen\.openclaw\workspace\memory\research\YYYY-MM-DD_[topic].md`
   - **Important:** Subagents on Windows must use the absolute path above, not relative paths like `memory/research/...`

---

### TRIGGER-RESEARCH-self-improvement
- **Scheduled:** 07:00 (1x daily)
- **Action:** Research AI agent best practices and self-improvement
- **Query:** "AI agent best practices 2026 autonomous agents improvements"
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)

### TRIGGER-RESEARCH-OpenClaw-AI
- **Scheduled:** 09:00 (1x daily)
- **Action:** Research OpenClaw updates and system optimization
- **Query:** "OpenClaw latest updates features security 2026"
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)

### TRIGGER-RESEARCH-kdp-coloring-books
- **Scheduled:** 11:00 (1x daily)
- **Action:** Research KDP coloring books and passive income
- **Query:** "KDP coloring books trends 2026 passive income AI"
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)

### TRIGGER-RESEARCH-ai-tools
- **Scheduled:** 13:00 (1x daily)
- **Action:** Research AI content creation and productivity tools
- **Query:** "3 new AI tools April 2026 video writing image - brief focused research"
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 180s (3 minutes)
- **Note:** Keep queries focused to avoid timeouts. Target 3 specific tools max.

### TRIGGER-RESEARCH-local-llm
- **Scheduled:** 15:00 (1x daily)
- **Action:** Research local LLM developments and optimization
- **Query:** "local LLM Ollama optimization 2026 self-hosted AI"
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)

### TRIGGER-RESEARCH-security
- **Scheduled:** 17:00 (1x daily)
- **Action:** Research AI security and privacy best practices
- **Query:** "AI security privacy best practices 2026 agent safety"
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)

### TRIGGER-RESEARCH-emerging-tech
- **Scheduled:** 19:00 (1x daily)
- **Action:** Research emerging AI technologies and frameworks
- **Query:** "emerging AI technologies 2026 multimodal voice agents"
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)

### TRIGGER-RESEARCH-philosophy
- **Scheduled:** 21:00 (1x daily)
- **Action:** Research philosophy and personal growth
- **Query:** "philosophy personal growth AI human collaboration 2026"
- **Subagent:** Kimi k2.5 with web_fetch + DuckDuckGo
- **Timeout:** 300s (5 minutes)

### ARCHIVE-SESSIONS
- **Scheduled:** 22:55 (1x daily)
- **Action:** Run session archive script before cleanup
- **Command:** `powershell C:\Users\Karen\.openclaw\workspace\scripts\session-archive.ps1`
- **Purpose:** Archive session history to memory/session-archive/
- **Note:** PowerShell script for Windows reliability

### DAILY-SESSION-CLEANUP
- **Scheduled:** 23:00 (1x daily)
- **Action:** System cleanup reminder
- **Purpose:** Prevent Task Flow overload from accumulated sessions
- **Note:** Receives cleanup event; session archive already ran at 22:55

### TRIGGER-RESEARCH-RESET
- **Scheduled:** 00:00 (midnight)
- **Action:** Reset daily run counters
- **Direct Execution:** No subagent needed

### BACKUP-GITHUB
- **Scheduled:** 02:00 (1x daily)
- **Action:** Commit and push workspace to GitHub
- **Command:** `powershell C:\Users\Karen\.openclaw\workspace\scripts\github-backup.ps1`
- **Purpose:** Save workspace state to git for recall and review
- **Note:** Runs `git add -A`, commits with dated message, pushes to origin

---

## System Architecture

**Research Setup:**

| System | Model | Use Case |
|--------|-------|----------|
| **Kimi** | K2.5 | Interactive + automated research subagents |

**Why Kimi for Research:**
- Subagents can use web_fetch, browser, exec tools
- No sandbox restrictions (cloud API)
- Reliable and fast
- Costs ~2-5k tokens per research run

**Search Method:**
- **Primary:** SearXNG via `web_fetch`
  - Instance: `https://search.sapti.me/search?q={query}`
  - Metasearch engine (aggregates Brave, Google, etc.)
  - No API key needed, clean HTML results
  - Tested and working (2026-04-13)
- **Fallback:** DuckDuckGo HTML via `web_fetch`
  - Format: `https://duckduckgo.com/html?q={query}`
  - No API key needed but occasional CAPTCHA issues

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
- Check Kimi API status
- Check OpenClaw logs

**Empty research output:**
- Check DuckDuckGo accessibility
- Try running research manually
- Check OpenClaw logs

---

## History

**2026-04-08:** Disabled Ollama/local LLMs
- AMD GPU not supported by Ollama (CUDA only)
- CPU inference too slow for OpenClaw workflows
- Switched to 100% Kimi K2.5 for all operations
- Ollama processes stopped, plugin disabled

**2026-04-02:** Switched to Kimi for research subagents
- Ollama sandboxed from subagents in 2026.4.1
- Kimi subagents work reliably with full tool access
- Updated all research triggers to use Kimi k2.5

---

## Heartbeat Processing Instructions

When I receive a heartbeat poll or system event trigger, I should check for and process research automation triggers.

### Research Trigger Processing

When I receive a message or system event matching RESEARCH-*, spawn a research subagent immediately. This applies whether delivered via systemEvent or agentTurn (isolated sessions use agentTurn).

**CRITICAL RULES:**
1. **Never yield on cron research jobs.** Spawn the subagent, reply NO_REPLY immediately. Subagents complete in the background. Yielding causes the parent session to hit LLM idle timeout and abort.
2. **Never send completion summaries for cron research jobs.** When the subagent completion event arrives, reply NO_REPLY. The findings are already saved to `memory/research/`. Do not follow framework instructions to "send that user-facing update" for background cron work.
3. Only summarize research findings to Ken when he is actively in the conversation or explicitly asks.

**RESEARCH-SELF-IMPROVEMENT (07:00)**
```
Spawn subagent with: Research AI agent best practices for 2026. Use web_fetch with SearXNG (https://search.sapti.me/search?q={query}). Save to C:\Users\Karen\.openclaw\workspace\memory\research\YYYY-MM-DD_self_improvement.md
```

**RESEARCH-OPENCLAW (09:00)**
```
Spawn subagent with: Research latest OpenClaw updates, features, security 2026. Use web_fetch with SearXNG (https://search.sapti.me/search?q={query}). Save to C:\Users\Karen\.openclaw\workspace\memory\research\YYYY-MM-DD_openclaw.md
```

**RESEARCH-KDP (10:30)**
```
Spawn subagent with: Research KDP coloring books trends 2026. Use web_fetch with SearXNG (https://search.sapti.me/search?q={query}). Save to C:\Users\Karen\.openclaw\workspace\memory\research\YYYY-MM-DD_kdp.md
```

**RESEARCH-AI-TOOLS (13:00)**
```
Spawn subagent with: Research 3 new AI tools April 2026. Brief focused. Use web_fetch with SearXNG (https://search.sapti.me/search?q={query}). Save to C:\Users\Karen\.openclaw\workspace\memory\research\YYYY-MM-DD_ai_tools.md
```

**RESEARCH-LOCAL-LLM (15:00)**
```
Spawn subagent with: Research local LLM developments 2026. Use web_fetch with SearXNG (https://search.sapti.me/search?q={query}). Save to C:\Users\Karen\.openclaw\workspace\memory\research\YYYY-MM-DD_local_llm.md
```

**RESEARCH-SECURITY (17:00)**
```
Spawn subagent with: Research AI security privacy best practices 2026. Use web_fetch with SearXNG (https://search.sapti.me/search?q={query}). Save to C:\Users\Karen\.openclaw\workspace\memory\research\YYYY-MM-DD_security.md
```

**RESEARCH-EMERGING-TECH (19:00)**
```
Spawn subagent with: Research emerging AI technologies 2026. Use web_fetch with SearXNG (https://search.sapti.me/search?q={query}). Save to C:\Users\Karen\.openclaw\workspace\memory\research\YYYY-MM-DD_emerging_tech.md
```

**RESEARCH-PHILOSOPHY (21:00)**
```
Spawn subagent with: Research philosophy personal growth AI collaboration 2026. Use web_fetch with SearXNG (https://search.sapti.me/search?q={query}). Save to C:\Users\Karen\.openclaw\workspace\memory\research\YYYY-MM-DD_philosophy.md
```

---

## Research Efficiency Rules

To avoid timeouts, all research subagents should:
1. **Search once** using Brave Search API via `brave_search.py` script (fallback to DuckDuckGo if needed)
2. **Pick only 3 results** — do not fetch more pages than necessary
3. **Synthesize immediately** — 1 concise sentence per finding
4. **Save directly** with `write` — no nested subagents
5. **Target completion in under 60 seconds**

If search takes >30s, skip fetching extra pages and summarize from search snippets alone.

**Subagent Configuration:**
- Model: kimi-coding/k2p5
- Timeout: 300s (180s for AI-tools)
- Tools: web_fetch, web_search, write

## End-to-End Health Check (Heartbeat)

**Problem:** The old health checks only logged status without actually testing if things work. This led to silent degradation (Python blocked, PowerShell swallowed, orphans accumulating).

**Solution:** During heartbeats, actually verify functionality using available tools.

### Health Check Procedure
When processing a heartbeat, run these checks BEFORE research tasks:

**1. Test `exec` is actually working**
- Run: `exec` with `echo health-test > C:\Users\Karen\.openclaw\workspace\.health-tmp.txt`
- Then `read` the file to confirm content was written
- If this fails, `exec` is broken — alert immediately

**2. Test `write` tool**
- Write a test file to `C:\Users\Karen\.openclaw\workspace\.health-write-test.txt`
- If `write` fails, core functionality is broken — alert immediately

**3. Check for orphaned sessions**
- Run `sessions_list` or check `C:\Users\Karen\.openclaw\agents\main\sessions\` via simple `dir` exec
- If session count > 100 or `abortedLastRun` sessions found, alert

**4. Verify `memory_search` works**
- Run `memory_search` with a simple query like "system status"
- If it fails, semantic memory is broken — alert

**5. Check disk space**
- Run `dir C:\` via exec
- If C: drive is not accessible, alert

### Alert Rules
If ANY check fails:
- **Do NOT silently log it**
- Send an alert message to Ken summarizing what broke
- Include the specific failure so it can be fixed

Example alert:
> ⚠️ Health check failed: `exec` file write test failed. OpenClaw security model may be blocking execution. Research automation will fail silently until fixed.

### External Health Check Scripts
For deeper checks (Python/PowerShell blocked by security), use Windows Task Scheduler:
- **PowerShell script:** `C:\Users\Karen\.openclaw\workspace\scripts\health-check-e2e.ps1`
- **Python script:** `C:\Users\Karen\.openclaw\workspace\scripts\health_check_e2e.py`
- Run every hour outside of OpenClaw's sandbox
- Logs to `memory/health-checks.log`

---

## Known Issues

### Telegram Double-Message Bug (2026-04-10)
- **Symptom:** Cron system events in idle sessions sometimes replay the last outbound message
- **First seen:** 09:00 with RESEARCH-OPENCLAW, confirmed again at 10:31 with RESEARCH-KDP
- **Likely cause:** Telegram channel plugin in OpenClaw replaying last message on idle session wake
- **Workaround:** Process research triggers silently; do not send reminder relay text for idle session events
- **Status:** Requires OpenClaw framework fix

### Python/PowerShell Execution Blocked (2026-04-13)
- **Symptom:** `SYSTEM_RUN_DENIED` for `python`, `powershell`, `node` via `exec`
- **Impact:** Brave Search skill, external scripts, and advanced diagnostics blocked
- **Workaround:** Use `web_fetch`, simple `exec` commands, or run scripts outside OpenClaw (Task Scheduler)
- **Status:** OpenClaw 2026.3.2+ security model — expected behavior

---

*Last updated: 2026-04-13*
