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

## System State (2026-02-23)
- **Phase 1:** 15/15 tasks COMPLETE
- **Phase 2:** 3/3 tasks COMPLETE (OneDrive ✅, Memory search ✅, Email ✅)
- **Phase 3:** VNC operational, remote access working
- **Current Focus:** 24/7 memory system, personality preservation

## Memory System (2026-02-23)
**CRITICAL FIX:** Hourly memory logging implemented after data loss scare.
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
