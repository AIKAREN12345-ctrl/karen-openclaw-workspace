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
- ✅ System commands via PowerShell (allowlisted)
- ✅ File operations
- ✅ Process management
- ✅ Screen capture (NirCmd + VNC)
- ✅ Browser automation (Chrome extension relay)
- ✅ Mouse & keyboard control (VNC)
- ✅ Automated maintenance (5 cron jobs)

## Important Dates
- **2026-02-19:** First full session, Phase 1 complete, VNC operational
- **2026-02-21:** VNC calibration system completed, partnership agreement established
- **2026-02-22:** Skills expansion — file auto-organizer, AI news monitor, hardware research
- **2026-02-23:** Memory system crisis → hourly logging implemented, missing memories recovered

## Preferences
- User comfortable with system-level access
- VNC password stored in environment variable (VNC_PASS)
- Uses PowerShell for system management
- Trusted home network

## Security Notes
- ✅ Gateway token rotated (64 chars, secure)
- ✅ Rate limiting configured (10/min, 5min lockout)
- ✅ Exec approvals: PowerShell, nircmd allowlisted
- ✅ VNC firewalled (local network only)
- ✅ Automated config backups

## System State (2026-02-26) - DAY 1 COMPLETE ✅
**Karen 2.0 is LIVE - Fully Operational System**

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
- ✅ OpenClaw 2026.2.25 running
- ✅ Node connected (DESKTOP-M8AO8LN)
- ✅ 24GB RAM optimized
- ✅ Local LLM automation operational
- ✅ 24/7 memory system active
- ✅ GitHub backup configured
- ✅ 7 skills ready
- ✅ VNC control working
- ✅ Browser/CDP functional

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

## Known Issues
- Browser CDP port conflict (18792 in use) — blocks browser snapshots
- Node VNC recording not enabled — can't do screen_record via node

## Next Steps
- ✅ Fix MEMORY.md permissions (workaround: write to full path)
- ✅ Recover Feb 21-22 memories
- ⏳ Create "Karen's Voice" style guide
- ⏳ Document session-end state snapshots
- ⏳ Fix browser CDP port conflict
- ⏳ Enable node VNC recording capability
