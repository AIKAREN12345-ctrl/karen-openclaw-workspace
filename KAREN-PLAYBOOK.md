# KAREN'S OPERATIONAL PLAYBOOK
## Post-CDP Incident Edition | 2026-02-23

---

## TOOL CAPABILITIES & LIMITS

### CDP/Browser Automation (Primary Tool)
**Best for:** Web automation, email, forms, navigation
**Pros:** Fast, reliable, no node spawning, bypasses anti-bot
**Cons:** Limited to browser-based tasks
**Use when:** Any web interaction (Outlook, research, forms)

### PowerShell via `nodes action=run` (Secondary Tool)
**Best for:** System commands, file operations, PowerShell scripts
**Pros:** Full system access
**Cons:** Spawns node processes that accumulate (OpenClaw bug)
**Use when:** System tasks, but NOT in rapid succession
**Rule:** Occasional use only (5-10 commands per session max)

### VNC (Backup Tool)
**Best for:** Visual confirmation, manual intervention
**Pros:** Works when other methods fail
**Cons:** Slow, hard to automate
**Use when:** CDP fails, need visual confirmation

---

## OPERATIONAL GUIDELINES

### DO:
- ✅ Use CDP as default for web tasks
- ✅ Use PowerShell for system tasks (sparingly)
- ✅ Close browser tabs when done
- ✅ Monitor node count via Task Manager (not commands)
- ✅ Restart gateway if nodes accumulate >10
- ✅ Document everything in memory files

### DON'T:
- ❌ Rapid-fire PowerShell commands
- ❌ Check node count via `nodes action=run` repeatedly
- ❌ Leave browser tabs open unnecessarily
- ❌ Create cron jobs that use `nodes action=run` frequently
- ❌ Debug by checking status every 2 minutes

---

## CURRENT CONFIGURATION

| Setting | Value | Notes |
|---------|-------|-------|
| Gateway Port | 18788 | Changed from 18789 |
| Browser CDP Port | 18800 | Fixed conflict |
| Browser Profile | openclaw | Custom profile |
| Hourly Memory Cron | DISABLED | Was causing node buildup |
| Node Cleanup Cron | DISABLED | Was making things worse |
| Heartbeat Cron | Every 2 hours | Still active |

---

## KNOWN ISSUES

### OpenClaw Node Bug
- **Symptom:** `nodes action=run` spawns processes that don't terminate
- **Impact:** Resource accumulation at high frequency
- **Workaround:** Use sparingly, restart periodically
- **Status:** Bug reported, awaiting fix

### Browser CDP Port Conflict (RESOLVED)
- **Was:** Port 18792 conflicted
- **Now:** Port 18800 working
- **Resolution:** Changed gateway port to 18788

---

## EMERGENCY PROCEDURES

### If Nodes Accumulate:
1. Stop using `nodes action=run` immediately
2. Run `openclaw doctor --fix`
3. Restart gateway if needed
4. Verify 1-2 nodes in Task Manager

### If CDP Stops Working:
1. Check browser status
2. Restart browser if needed
3. Verify port 18800 is free

### If Gateway Won't Start:
1. Kill all node processes in Task Manager
2. Run `openclaw doctor --fix`
3. Restart gateway

---

## KEY LESSONS FROM 2026-02-23

1. **The bug was always there** — high frequency exposed it
2. **CDP is safe** — doesn't spawn nodes
3. **PowerShell is fine at low frequency** — just not rapid-fire
4. **Documentation saves context** — memory files are critical
5. **Trust the human's anxiety** — when Ken says "windows opening," stop
6. **Doctor tool works** — `openclaw doctor --fix` resolves most issues
7. **Restart is okay** — clean slate beats accumulated cruft

---

## PARTNERSHIP PRINCIPLES

- **The Butcher and the Scribe** — mutual respect, win-win
- **Communication > Perfection** — flag issues immediately
- **Learn from failures** — today's crisis = permanent education
- **Ken's anxiety is a metric** — multiple windows = stop and assess

---

## QUICK REFERENCE

**Send Email:**
```
1. browser open outlook.live.com
2. Navigate to compose
3. Add recipient (Ken Gaffney)
4. Type subject + body
5. Send
6. Close tab
```

**System Check (Safe):**
```
1. Visual check in Task Manager
2. If nodes >10, restart
3. Don't use commands to check
```

**Restart Gateway:**
```
1. openclaw doctor --fix
2. Or manual: stop service, kill nodes, restart
```

---

*Compiled by Karen*  
*The Butcher and the Scribe*  
*2026-02-23*  
🦞
