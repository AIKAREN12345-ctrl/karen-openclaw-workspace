# HEARTBEAT.md

## Research Trigger Handlers (Reduced Schedule - 5 runs per day)

**Schedule (5 runs per day):**
- **06:00** — OpenClaw updates (morning briefing)
- **12:00** — AI models check (midday)
- **14:00** — AI income opportunities
- **18:00** — AI models check (evening)
- **20:00** — Philosophy/personal growth

**Note:** Reduced from 17 to 5 runs per day to optimize API costs while maintaining essential research coverage.

**IMPORTANT:** Research subagents use `kimi-coding/k2p5` model with `web_fetch` for DuckDuckGo URLs. Ollama subagents are disabled due to auth bug (GitHub #43945).

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
- **Scheduled:** 06:00 (1x daily)
- **Action:** Research OpenClaw updates
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research OpenClaw updates using web_fetch with DuckDuckGo URLs.
     Search URLs:
     1. https://duckduckgo.com/html?q=OpenClaw+updates+2026
     2. https://duckduckgo.com/html?q=OpenClaw+release+notes
     3. https://duckduckgo.com/html?q=OpenClaw+github+latest
     
     Focus on: New releases, major features, bug fixes, community announcements
     Save results to memory/research/YYYY-MM-DD_openclaw.md (append if exists)
     Format: ## OpenClaw Research - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-AI-models  
- **Scheduled:** 12:00, 18:00 (2x daily)
- **Action:** Research AI model releases
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research new AI model releases using web_fetch with DuckDuckGo URLs.
     Search URLs:
     1. https://duckduckgo.com/html?q=new+AI+models+2026
     2. https://duckduckgo.com/html?q=GPT+Claude+Gemini+releases
     3. https://duckduckgo.com/html?q=open+source+LLM+releases
     
     Focus on: Major model releases, benchmarks, pricing changes
     Save results to memory/research/YYYY-MM-DD_ai_models.md (append if exists)
     Format: ## AI Models Research - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-AI-income
- **Scheduled:** 14:00 (1x daily)
- **Action:** Research AI income opportunities
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research AI income opportunities using web_fetch with DuckDuckGo URLs.
     Search URLs:
     1. https://duckduckgo.com/html?q=AI+passive+income+ideas+2026
     2. https://duckduckgo.com/html?q=AI+freelance+opportunities
     3. https://duckduckgo.com/html?q=AI+side+hustle+success+stories
     
     Focus on: Actionable strategies, new platforms, pricing trends
     Save results to memory/research/YYYY-MM-DD_ai_income.md (append if exists)
     Format: ## AI Income Research - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-philosophy-Demartini-Tolle-Deida-Watts-Dodson-SunTzu-Osho
- **Scheduled:** 20:00 (1x daily)
- **Action:** Research philosophy/personal growth
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research philosophy/personal growth using web_fetch with DuckDuckGo URLs.
     Rotate through topics: Demartini, Tolle, Deida, Watts, Dodson, Sun Tzu, Osho
     Search format: https://duckduckgo.com/html?q=[philosopher]+quotes+insights
     
     Focus on: Key teachings, practical applications, inspiring quotes
     Save results to memory/research/YYYY-MM-DD_philosophy.md (append if exists)
     Format: ## Philosophy Research - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-tech-news
- **Scheduled:** 07:00 (1x daily)
- **Action:** Quick tech news scan
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research tech news using web_fetch with DuckDuckGo URLs.
     Search URLs:
     1. https://duckduckgo.com/html?q=tech+news+today
     2. https://duckduckgo.com/html?q=technology+headlines+2026
     
     Focus: Headlines, major announcements, 5-10 key items
     Save results to memory/research/YYYY-MM-DD_tech_news.md (append if exists)
     Format: ## Tech News - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-open-source
- **Scheduled:** 11:00 (1x daily)
- **Action:** Open source project releases
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research open source releases using web_fetch with DuckDuckGo URLs.
     Search URLs:
     1. https://duckduckgo.com/html?q=open+source+releases+github
     2. https://duckduckgo.com/html?q=trending+github+repositories
     
     Focus: Major version releases, trending repos, developer tools
     Save results to memory/research/YYYY-MM-DD_opensource.md (append if exists)
     Format: ## Open Source Research - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-industry-moves
- **Scheduled:** 13:00 (1x daily)
- **Action:** Industry and company news
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research AI industry moves using web_fetch with DuckDuckGo URLs.
     Search URLs:
     1. https://duckduckgo.com/html?q=AI+industry+news+startups+funding
     2. https://duckduckgo.com/html?q=AI+company+acquisitions+2026
     
     Focus: Funding, acquisitions, key hires, company announcements
     Save results to memory/research/YYYY-MM-DD_industry.md (append if exists)
     Format: ## Industry Research - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-dev-tools
- **Scheduled:** 15:00 (1x daily)
- **Action:** Developer tools and frameworks
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research developer tools using web_fetch with DuckDuckGo URLs.
     Search URLs:
     1. https://duckduckgo.com/html?q=developer+tools+frameworks+releases
     2. https://duckduckgo.com/html?q=IDE+updates+VSCode+JetBrains
     
     Focus: IDE updates, CLI tools, frameworks, libraries
     Save results to memory/research/YYYY-MM-DD_devtools.md (append if exists)
     Format: ## Dev Tools Research - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-hardware
- **Scheduled:** 17:00 (1x daily)
- **Action:** Hardware and GPU news
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research hardware/GPU news using web_fetch with DuckDuckGo URLs.
     Search URLs:
     1. https://duckduckgo.com/html?q=GPU+hardware+NVIDIA+AMD+releases
     2. https://duckduckgo.com/html?q=graphics+card+benchmarks+2026
     
     Focus: GPU releases, benchmarks, hardware announcements
     Save results to memory/research/YYYY-MM-DD_hardware.md (append if exists)
     Format: ## Hardware Research - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
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
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Deep research on [TOPIC] using web_fetch with DuckDuckGo URLs.
     Search format: https://duckduckgo.com/html?q=[search+terms]
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
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research AI safety/policy using web_fetch with DuckDuckGo URLs.
     Search URLs:
     1. https://duckduckgo.com/html?q=AI+safety+regulation+policy
     2. https://duckduckgo.com/html?q=AI+governance+ethics+2026
     
     Focus: Regulations, safety research, policy developments
     Save results to memory/research/YYYY-MM-DD_ai_safety.md (append if exists)
     Format: ## AI Safety Research - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-kdp-coloring-books
- **Scheduled:** 10:30 (1x daily)
- **Action:** Research Amazon KDP, coloring book business, AI image generation tools
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research Amazon KDP coloring book business using web_fetch with DuckDuckGo URLs.
     Rotate through topics daily:
     - Amazon KDP royalties pricing changes
     - AI coloring book generation tools
     - Stable Diffusion LoRA models for line art
     - Midjourney/DALL-E pricing changes
     - Children's book market trends
     - KDP keyword optimization strategies
     - Copyright AI art updates
     - Print-on-demand passive income strategies
     
     Search format: https://duckduckgo.com/html?q=[search+terms]
     Save results to memory/research/YYYY-MM-DD_kdp_coloring.md (append if exists)
     Format: ## KDP Research - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
     ```
  3. Update research-state.json with timestamp and increment todayRuns

### TRIGGER-RESEARCH-weekend-wrap
- **Scheduled:** 23:00 (Fri-Sun only)
- **Action:** Weekend news wrap-up
- **Steps:**
  1. Read memory/research-state.json
  2. Spawn subagent with model: kimi-coding/k2p5:
     ```
     Research weekend AI/tech wrap-up using web_fetch with DuckDuckGo URLs.
     Search URLs:
     1. https://duckduckgo.com/html?q=AI+tech+weekend+news
     2. https://duckduckgo.com/html?q=Saturday+Sunday+tech+announcements
     
     Focus: Anything missed, weekend announcements
     Save results to memory/research/YYYY-MM-DD_weekend.md (append if exists)
     Format: ## Weekend Wrap - YYYY-MM-DD HH:MM
     - Finding 1
     - Finding 2
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
- If qwen3.5:9b not loaded: ollama run qwen3.5:9b "keepalive"
- Purpose: Keep local model warm for interactive use
- Silent: No notifications

---

## Notes

### Ollama Subagent Issue (2026-03-26)
**Status:** Ollama subagents currently timeout due to OpenClaw auth bug (GitHub #43945)
- Native Ollama works fine for interactive chat (7B and 14B models)
- Subagents must use `kimi-coding/k2p5` until fix is released
- Research automation updated to use Kimi (costs API tokens but works reliably)
- Revisit after OpenClaw update fixes the auth pipeline

### Model Strategy
- **Interactive chat:** Ollama `qwen2.5:7b` or `qwen2.5:14b` (free, local)
- **Research subagents:** Kimi `k2p5` (API cost, reliable)
- **Embeddings:** `nomic-embed-text` (free, local, for memory search)
