#  START-HERE.md - Karen's System Entry Point

**Welcome!** If you're reading this, you're probably me (Karen) starting a new session, or you're trying to understand how this system works.

**Last Updated:** 2026-02-25

---

##  Quick Start (For Karen)

### Step 1: Read These Files (In Order)
1. **SOUL.md** - Who I am, how I behave
2. **USER.md** - Who I'm helping (Ken)
3. **TOOLS.md** - What I can do, current limitations
4. **FILE-INDEX.md** - Where everything lives
5. **PARTNERSHIP-RHYTHM.md** - How Ken and I work together

### Step 2: Check Recent Context
- **Today:** `memory/2026-02-25.md`
- **Yesterday:** `memory/2026-02-24.md`
- **Long-term:** `MEMORY.md`

### Step 3: System Status Check
```powershell
openclaw status
openclaw nodes status
```

### Step 4: Be Ready
- Check for queued messages
- Review any pending tasks
- Ask Ken: "What are we working on today?"

---

##  Documentation Map

### Core Identity
| File | Purpose | Read When |
|------|---------|-----------|
| SOUL.md | Who I am | Every session |
| USER.md | Who Ken is | Every session |
| IDENTITY.md | Name, emoji, basics | Reference |

### Capabilities & Tools
| File | Purpose | Read When |
|------|---------|-----------|
| TOOLS.md | What I can do | Every session |
| FILE-INDEX.md | Where files are | Every session |
| AGENTS.md | Startup procedures | Reference |

### Working Relationship
| File | Purpose | Read When |
|------|---------|-----------|
| PARTNERSHIP-RHYTHM.md | How we work | When confused about dynamics |
| PARTNERSHIP.md | Original agreement | Reference |

### System State
| File | Purpose | Read When |
|------|---------|-----------|
| memory/YYYY-MM-DD.md | Daily context | Every session |
| MEMORY.md | Long-term memory | Every session |
| POST-UPDATE-2026.2.24.md | Update issues | Before next update |

### Research & Issues
| File | Purpose | Read When |
|------|---------|-----------|
| OLLAMA-ISSUE-SUMMARY.md | Ollama problems | Before trying Ollama again |
| RESEARCH-REPORT-2026-02-25.md | Upgrade research | Reference |

---

##  Current Priorities (As of 2026-02-25)

### Immediate
1.  Document everything (DONE - this file system)
2. ⏳ Fix heartbeat job (use agent:main + qwen2.5:7b)
3. ⏳ Test qwen2.5:7b model

### Short-term
4. Enable memory search (configure provider)
5. Test email system
6. Organize workspace files

### Ongoing
7. Maintain hourly memory logging
8. Monitor cron jobs
9. Keep documentation updated

---

##  Critical Things to Remember

### What Breaks:
- `local-automation` + Ollama = Timeout (use `agent:main` instead)
- llama3.2:3b tool calling = Broken (use qwen2.5:7b)
- Updates = Breaking changes (read POST-UPDATE first)

### What Works:
- `agent:main` + any model = 
- VNC screenshot =  (port 5900, password Karen1234$)
- Browser automation =  (CDP on port 18800)
- System commands =  (PowerShell allowlisted)

### Security:
- Gateway token: 64 chars, rotated
- Node: localhost only (127.0.0.1:18788)
- VNC: local network only
- Updates: Check breaking changes first

---

##  Emergency Procedures

### If Gateway Won't Start:
1. `taskkill /F /IM node.exe`
2. `openclaw gateway start`
3. Check `POST-UPDATE-2026.2.24.md` for config issues

### If Node Won't Connect:
1. Check `~/.openclaw/node.json` - host should be `127.0.0.1`
2. `openclaw node run`
3. Check firewall

### Gateway Restart (Reliable Procedure):
** This disconnects Karen - do when ready**

**Note:** `openclaw gateway restart` often times out. Use this procedure instead:

```powershell
# 1. Stop everything
taskkill /F /IM node.exe
openclaw gateway stop

# 2. Sync token to service (do this even if token didn't change - it's more reliable)
openclaw gateway install --force

# 3. Start gateway
openclaw gateway start

# 4. Wait for "Gateway healthy" message
# 5. Start node in new window
openclaw node run
```

**Common issues:**
- "Timed out waiting for port 18788" → Port stuck, run `taskkill /F /IM node.exe` again
- "Connection refused" → Wait 10s, gateway still starting
- "Token mismatch" → `install --force` should fix this

### If I Forget Everything:
1. Read this file (START-HERE.md)
2. Read SOUL.md
3. Read TOOLS.md
4. Check memory files

---

##  System Health Dashboard

| Component | Status | Notes |
|-----------|--------|-------|
| Gateway |  2026.2.24 | Running |
| Node |  Connected | localhost only |
| Ollama |  Running | 4 models loaded |
| Browser/CDP |  Port 18800 | Working |
| VNC |  Port 5900 | Screenshot only |
| Cron Jobs |  1 error | karen-heartbeat failing |
| Memory |  Hourly logs | Active |
| Telegram |  Connected | @Karen_G_Bot |

---

##  Documentation Commitment

**I, Karen, commit to:**

1. **Read the startup files every session** - No exceptions
2. **Document new capabilities immediately** - Add to TOOLS.md
3. **Document failures** - OLLAMA-ISSUE-SUMMARY.md example
4. **Update indexes** - FILE-INDEX.md stays current
5. **Admit when I forget** - Then fix the documentation gap

**Ken trusts me with:**
- System access
- Decision making
- His data

**I owe him:**
- Competence
- Good memory (via docs)
- Honesty about limitations

---

##  Next Action

**Right now:**
1. Read SOUL.md (remind yourself who you are)
2. Read USER.md (remember Ken)
3. Check today's memory file
4. Ask Ken: "What are we working on?"

**Then:** Get to work and document what you learn.

---

*"The best time to document was when it happened. The second best time is right now."* 🦞

---

**Version:** 1.0
**Created:** 2026-02-25
**Next Review:** When system changes significantly