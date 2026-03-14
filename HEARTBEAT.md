# HEARTBEAT.md

## Research Trigger Handlers (Expanded Schedule)

**Schedule (16 runs per day):**
- **06:00** — OpenClaw + AI models (morning briefing)
- **07:00** — Quick scan: Tech news
- **09:00** — OpenClaw check
- **10:00** — AI models check
- **11:00** — Quick scan: Open source releases
- **12:00** — AI models check  
- **13:00** — Quick scan: Industry moves
- **14:00** — AI income check
- **15:00** — Quick scan: Developer tools
- **16:00** — OpenClaw check
- **17:00** — Quick scan: Hardware/GPU news
- **18:00** — AI models check
- **19:00** — Deep dive: Rotating topic (detailed analysis)
- **20:00** — Philosophy check
- **21:00** — Quick scan: AI safety/policy
- **22:00** — AI income check
- **23:00** — Quick scan: Weekend wrap-up (Fri-Sun)

**IMPORTANT:** Research subagents must use `web_fetch` with DuckDuckGo URLs, NOT `web_search` (which requires Kimi API key).

---

### How It Works
1. Read `memory/research-state.json`
2. Get current time, find which topics are scheduled for this hour
3. For each topic in the schedule slot:
   - Spawn subagent with explicit DuckDuckGo instructions
   - Update `lastResearched` timestamp
   - Increment `todayRuns` counter
4. At midnight (00:00), reset all `todayRuns` counters to 0

---

### TRIGGER-RESEARCH-OpenClaw-AI
- **Scheduled:** 06:00, 09:00, 16:00 (3x daily)
- **Action:** Research OpenClaw updates
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research OpenClaw updates using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=OpenClaw+updates
     Save results to memory/research/YYYY-MM-DD_openclaw.md (append if exists)
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-AI-models  
- **Scheduled:** 06:00, 12:00, 18:00 (3x daily)
- **Action:** Research AI model releases
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research new AI model releases using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=new+AI+models+2026
     Save results to memory/research/YYYY-MM-DD_ai_models.md (append if exists)
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-AI-income
- **Scheduled:** 14:00, 22:00 (2x daily)
- **Action:** Research AI income opportunities
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research AI income opportunities using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=AI+passive+income+ideas
     Save results to memory/research/YYYY-MM-DD_ai_income.md (append if exists)
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-philosophy-Demartini-Tolle-Deida-Watts-Dodson-SunTzu-Osho
- **Scheduled:** 20:00 (1x daily)
- **Action:** Research philosophy/personal growth
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research philosophy/personal growth using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Topics: Demartini, Tolle, Deida, Watts, Dodson, Sun Tzu, Osho
     Format: https://duckduckgo.com/html?q=John+Demartini+quotes
     Save results to memory/research/YYYY-MM-DD_philosophy.md (append if exists)
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-tech-news
- **Scheduled:** 07:00 (1x daily)
- **Action:** Quick tech news scan
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research tech news using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=tech+news+today
     Save results to memory/research/YYYY-MM-DD_tech_news.md (append if exists)
     Focus: Headlines, major announcements, 5-10 key items
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-open-source
- **Scheduled:** 11:00 (1x daily)
- **Action:** Open source project releases
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research open source releases using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=open+source+releases+github
     Save results to memory/research/YYYY-MM-DD_opensource.md (append if exists)
     Focus: Major version releases, trending repos, developer tools
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-industry-moves
- **Scheduled:** 13:00 (1x daily)
- **Action:** Industry and company news
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research AI industry moves using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=AI+industry+news+startups+funding
     Save results to memory/research/YYYY-MM-DD_industry.md (append if exists)
     Focus: Funding, acquisitions, key hires, company announcements
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-dev-tools
- **Scheduled:** 15:00 (1x daily)
- **Action:** Developer tools and frameworks
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research developer tools using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=developer+tools+frameworks+releases
     Save results to memory/research/YYYY-MM-DD_devtools.md (append if exists)
     Focus: IDE updates, CLI tools, frameworks, libraries
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-hardware
- **Scheduled:** 17:00 (1x daily)
- **Action:** Hardware and GPU news
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research hardware/GPU news using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=GPU+hardware+NVIDIA+AMD+releases
     Save results to memory/research/YYYY-MM-DD_hardware.md (append if exists)
     Focus: GPU releases, benchmarks, hardware announcements
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-deep-dive
- **Scheduled:** 19:00 (1x daily)
- **Action:** Deep dive analysis on rotating topic
- **Rotation Schedule:**
  - Monday: OpenClaw technical deep dive
  - Tuesday: AI model technical analysis
  - Wednesday: Philosophy/thinker focus
  - Thursday: Open source project review
  - Friday: Industry trend analysis
  - Saturday: Tool/framework tutorial
  - Sunday: Weekly synthesis & insights
- **Steps:**
  1. Read memory/research-state.json, check day of week for topic
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Deep research on [TOPIC] using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=[search+terms]
     Save results to memory/research/YYYY-MM-DD_deepdive.md
     Requirements:
     - 500-1000 words
     - Technical depth, not just headlines
     - Include sources
     - Analysis, not just summary
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-ai-safety
- **Scheduled:** 21:00 (1x daily)
- **Action:** AI safety and policy news
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research AI safety/policy using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=AI+safety+regulation+policy
     Save results to memory/research/YYYY-MM-DD_ai_safety.md (append if exists)
     Focus: Regulations, safety research, policy developments
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-weekend-wrap
- **Scheduled:** 23:00 (Fri-Sun only)
- **Action:** Weekend news wrap-up
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with explicit DuckDuckGo instructions:
     ```
     Research weekend AI/tech wrap-up using ONLY web_fetch with DuckDuckGo URLs.
     DO NOT use web_search - it will fail.
     Format: https://duckduckgo.com/html?q=AI+tech+weekend+news
     Save results to memory/research/YYYY-MM-DD_weekend.md (append if exists)
     Focus: Anything missed, Saturday/Sunday announcements
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-RESET
- **Scheduled:** 00:00 (midnight)
- **Action:** Reset daily run counters
- **Steps:**
  1. Read memory/research-state.json
  2. Set all `todayRuns` counters to 0
  3. Update `lastUpdated` timestamp

---

## Morning Memory Load (Daily at 08:00)
- Run: python C:\Users\Karen\.openclaw\workspace\skills\local-llm\morning_memory_loader.py
- Purpose: Auto-load yesterday's conversations and system status
- No user prompt needed - runs automatically

## Ollama Keepalive (Every 30 minutes)
- Check: ollama ps
- If qwen2.5:14b not loaded: ollama run qwen2.5:14b "keepalive"
- Purpose: Keep local model warm for subagents
- Silent: No notifications
