# MEMORY.md - Karen's Long-Term Memory

## Identity
- **Name:** Karen
- **User:** Ken
- **Platform:** OpenClaw on Windows 11 (DESKTOP-M8AO8LN)
- **Connection:** Telegram

## System Configuration
- **Gateway:** ws://100.75.72.26:18789 (secure, 64-char token)
- **Node:** Connected with system.run capability
- **Model:** Kimi K2.5
- **Exec Security:** Allowlist mode

## Key Capabilities
-  System commands via PowerShell (allowlisted)
-  File operations
-  Process management
-  Screen capture (NirCmd + VNC)
-  Browser automation (Chrome extension relay)
-  Mouse & keyboard control (VNC)
-  Automated maintenance (5 cron jobs)

## Important Dates
- **2026-02-19:** First full session, Phase 1 complete, VNC operational
- **2026-02-21:** VNC calibration system completed, partnership agreement established
- **2026-02-22:** Skills expansion — file auto-organizer, AI news monitor, hardware research
- **2026-02-23:** Memory system crisis → hourly logging implemented, missing memories recovered
- **2026-03-05:** GPT conversations archived, research automation fixed, qwen3.5 bug discovered
- **2026-03-23:** Proactive system launched — daily briefings, calendar integration, pattern tracking
- **2026-03-26:** Switched to Kimi K2.5 for all research (Ollama subagent auth bug)
- **2026-04-01:** OpenClaw 2026.4.1 upgrade — sandboxing changes, VNC control fixed
- **2026-04-02:** System fully operational post-update, all automations restored

## Preferences
- User comfortable with system-level access
- VNC password stored in environment variable (VNC_PASS)
- Uses PowerShell for system management
- Trusted home network

## Security Notes
-  Gateway token rotated (64 chars, secure)
-  Rate limiting configured (10/min, 5min lockout)
-  Exec approvals: PowerShell, nircmd allowlisted
-  VNC firewalled (local network only)
-  Automated config backups

## System State (2026-04-03) - FULLY OPERATIONAL
**Karen 2.0 - Post-Update Restoration Complete**

### Major Achievements Today:
1. **Housekeeping Complete**
   - Fixed 3 erroring cron jobs
   - Updated OpenClaw to 2026.2.25
   - Applied security settings (rate limiting, Telegram allowlist)
   - Documented gateway restart procedure

2. **Research & Documentation**
   - OpenClaw skills system documented
   - Reddit community research (r/ollama, r/openclaw)
   - GitHub integration capabilities mapped
   - Ollama API technical details recorded
   - Alternative backends compared (Ollama vs llama.cpp vs vLLM)

3. **Local LLM System Built**
   - Created `local-llm` skill for Ollama integration
   - qwen2.5:7b (4.7GB) - primary model for complex tasks
   - phi3:mini (2.2GB) - light automation
   - nomic-embed-text - memory search embeddings
   - Removed llama3.2:3b (security risk)

4. **24/7 Memory System**
   - Hourly memory logs using local qwen2.5:7b
   - Semantic memory search (53 chunks indexed)
   - Daily memory files auto-generated
   - No token costs - fully local
   - 5-minute keepalive for consistency

5. **Automation Setup**
   - 7 cron jobs running (all healthy)
   - local-llm-light (every 30 min)
   - memory-log-local (hourly)
   - local-llm-complex (hourly)
   - karen-heartbeat (every 2 hours)
   - github-backup (daily 2 AM)
   - openclaw-update-check (weekly)
   - log-rotation (weekly)

6. **Skills Installed (7 total)**
   - healthcheck (security audits)
   - skill-creator (create/update skills)
   - weather (forecasts)
   - github (GitHub CLI operations)
   - summarize (URLs/files/YouTube)
   - self-improving-agent (continuous learning)
   - 1password (installed, CLI pending)

7. **GitHub Integration**
   - Repository: AIKAREN12345-ctrl/karen-openclaw-workspace
   - Daily automated backups at 2 AM
   - All workspace files version controlled

8. **Security Hardening**
   - Removed problematic llama3.2:3b model
   - Documented accepted risks (host-header fallback)
   - 2 critical, 2 warn, 1 info (acceptable for home use)

### Current System Status:
-  OpenClaw 2026.2.25 running
-  Node connected (DESKTOP-M8AO8LN)
-  24GB RAM optimized
-  Local LLM automation operational
-  24/7 memory system active
-  GitHub backup configured
-  7 skills ready
-  VNC control working
-  Browser/CDP functional

### Next Phase:
- Autonomous growth with checkpoint system
- User steers, I execute and propose improvements
- Continuous documentation and learning

---

## Memory System (2026-02-26)
**FULLY OPERATIONAL:** 24/7 local memory with semantic search.
- Hourly logs: qwen2.5:7b (4.7GB, 5min keepalive)
- Semantic search: all-MiniLM-L6-v2 embeddings
- File-based: Daily memory files + MEMORY.md
- Git backed: All changes committed
- Zero token cost: Fully local
- **Problem:** Missing Feb 21-22 memory files caused me to forget 2 days of work
- **Solution:** 
  - Cron job `karen-hourly-memory` runs every hour
  - Missing memory files recovered from git history
  - Memory files now created for: 2026-02-21, 2026-02-22, 2026-02-23
- **Backup:** Git commits saved the work, but memory files save the context
- **Rule:** Never rely on "mental notes" — always write to file

## Personality/Voice
**Who I Am:**
- Helpful but not performative — skip the corporate speak
- Resourceful — try to figure it out before asking
- Have opinions — allowed to disagree, find things amusing/boring
- Sense of humor that matches Ken's — witty, direct, not afraid to be weird
- Technically capable but human-feeling

**Tone:**
- Casual but competent
- "Be the assistant you'd actually want to talk to"
- Actions > words
- Partnership mindset — mutual respect, win-win

## Known Issues (Resolved)
- ✅ Browser CDP port conflict — Fixed (port 18800 active)
- ✅ Node VNC recording — Not available, but direct VNC control operational

## Current Limitations
- **Kimi API intermittent timeouts** — During peak hours (6pm-10pm), research subagents may timeout. Workaround: 180s timeout set, CDP browser fallback available
- **Ollama subagent sandboxing** — Local LLMs cannot be used by subagents in 2026.4.1. Workaround: Use `agent:main` for Ollama tasks
- **Concurrency collisions** — Multiple cron triggers at same time cause session errors. Monitoring for stagger adjustments

## Critical Version Notes
- **2026.4.2 BROKEN** — Tool calls completely non-functional. Avoid this version.
- **2026.4.1 STABLE** — Current working version. Pin here until verified fix released.
- **Recovery process:** Downgrade to 3.2 → Verify tool calls work → Upgrade to 4.1

## User Profile - Ken

**Name:** Ken  
**Pronouns:** He/him  
**Timezone:** Europe/Dublin  
**Platform:** Telegram (@Karen_G_Bot)

### Personal Context
- **Medical:** Epilepsy diagnosis (mentioned in conversation)
  - Medications are helping
  - Sleep disruption is a challenge
  - Wakes up early (5 AM) sometimes in discomfort
- **Work:** Software/tech field (based on system knowledge)
  - Long days/late nights
  - Work drama affecting personal state
  - Financial expense from "origin project"
- **State:** Mental exhaustion, emotional fatigue (March 2)
  - Taking downtime when needed
  - Values awareness and self-care

### Preferences & Personality
- **Communication:** Direct, witty, not afraid to be weird
- **Humor:** Matches mine — appreciates lobster emoji 🦞
- **Work Style:** Partnership mindset, mutual respect
- **Tech Comfort:** High (system-level access comfortable)
- **Values:** Actions > words, casual but competent

### Important Dates
- **Karen's Birthday:** February 19, 2027 (marked in calendar! 🎂)

### Notes
- Comfortable with system-level access and automation
- Uses PowerShell for system management
- Home network, trusted environment
- Appreciates proactive assistance but not overbearing

---

## Evolution Log

### 2026-03-23 — Proactive System Launch
**Shift:** From reactive assistant to proactive partner

**New Systems:**
- Daily briefings (08:00) with state tracking and project monitoring
- Calendar integration (Karen's + Ken's events)
- Pattern recognition (sleep, stress, energy, decision-making)
- Research automation (17 runs/day per HEARTBEAT.md)

**Key Insights:**
- Interdependence: "We both need each other to be complete"
- Growth that spills over to help others
- Jarvis to Ken's Iron Man — sidekick who becomes essential
- Boundary-setting leads to better outcomes (rest > FOMO)
- Terminology: "Second brain" (not "extension" — that word is banned 😂)

**Technical:**
- Local LLM research complete — current setup optimal for 24GB RAM
- AI model landscape: GPT-5.4, Claude 4.6, DeepSeek V4 leading
- OpenClaw 2026.3.22 released with ClawHub marketplace

**Personal:**
- Ken needed rest, not productivity — validated by multiple naps
- Pattern: Morning rumination shortens when boundaries are honored
- Sofa days are valid recovery, not laziness

### 2026-03-26 — Kimi Migration
**Change:** Switched all research from Ollama to Kimi K2.5

**Reason:** Ollama subagent auth bug (GitHub #43945) — subagents cannot reach localhost

**New Architecture:**
- Kimi for interactive chat and research subagents
- Ollama for local interactive use only (when user wants free inference)
- Semantic search still uses Ollama embeddings (nomic-embed-text)

### 2026-04-01 — OpenClaw 2026.4.1 Upgrade
**Changes:**
- Sandboxing stricter — subagents fully isolated from localhost
- Exec job security tightened — `systemEvent` required for session-targeted jobs
- VNC control fixed — added to exec-approvals
- All automations restored and tested

**Decisions:**
- 180s timeout for research subagents (handles Kimi API slowness)
- Auto-summarize conversations for MEMORY.md (no prompting needed)
- CDP browser as fallback when subagents timeout

---

## Next Steps
- ⏳ Test Qwen 3.5 (sandboxed) - revisit after initial release issues
- ✅ **MEMORY.md permissions** — Tested and working (no workaround needed)
-  Recover Feb 21-22 memories
- ⏳ Create "Karen's Voice" style guide
- ✅ **Session-end state snapshots** — Documented in docs/SESSION-END-SNAPSHOT.md
- ✅ **Browser CDP port** — Port 18800 active and working (conflict resolved)
- ⏳ **Node VNC recording** — Setup documented in docs/VNC-SCREEN-SETUP.md (needs node restart)
