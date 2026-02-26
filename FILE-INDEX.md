# FILE-INDEX.md - Complete System Documentation

**Last Updated:** 2026-02-25
**System:** OpenClaw on Windows 11 (DESKTOP-M8AO8LN)

---

## 📁 Core Configuration Files

| File | Purpose | Last Modified |
|------|---------|---------------|
| `~/.openclaw/openclaw.json` | Main OpenClaw configuration | 2026-02-25 |
| `~/.openclaw/node.json` | Node connection settings | 2026-02-25 |
| `~/.openclaw/cron/jobs.json` | Cron job definitions | 2026-02-24 |

---

## 🦞 Identity & Personality Files

| File | Purpose | Created |
|------|---------|---------|
| `SOUL.md` | Who I am, my values, how I behave | 2026-02-19 |
| `IDENTITY.md` | Name, creature, emoji, avatar | 2026-02-19 |
| `USER.md` | Who I'm helping (Ken) | 2026-02-19 |
| `AGENTS.md` | Startup procedures, memory rules | 2026-02-19 |
| `BOOTSTRAP.md` | First-run instructions | 2026-02-19 |
| `HEARTBEAT.md` | Periodic check tasks | 2026-02-19 |

---

## 🔧 Tools & Capabilities Documentation

| File | Purpose | Last Updated |
|------|---------|--------------|
| `TOOLS.md` | **CRITICAL:** All tools, capabilities, limitations | 2026-02-25 |
| `FILE-INDEX.md` | This file - complete file inventory | 2026-02-25 |

---

## 🧠 Memory System

### Daily Memory Logs
| File | Date | Status |
|------|------|--------|
| `memory/2026-02-19.md` | Feb 19 | ✅ Original |
| `memory/2026-02-20.md` | Feb 20 | ✅ Original |
| `memory/2026-02-21.md` | Feb 21 | ✅ Reconstructed |
| `memory/2026-02-22.md` | Feb 22 | ✅ Reconstructed |
| `memory/2026-02-23.md` | Feb 23 | ✅ Original |
| `memory/2026-02-24.md` | Feb 24 | ✅ Original |
| `memory/2026-02-25.md` | Feb 25 | ✅ Current |

### Long-term Memory
| File | Purpose |
|------|---------|
| `MEMORY.md` | Curated long-term memories, key events |

---

## 🎥 VNC System Files

| File | Purpose | Status |
|------|---------|--------|
| `vnc-screenshot-robust.py` | Screenshot capture via VNC | ✅ Working |
| `vnc-recorder-robust.py` | Screen recording via VNC | ✅ Working |
| `vnc_screenshot.py` | Original screenshot script | ⚠️ Legacy |
| `vnc-recorder.py` | Original recorder script | ⚠️ Legacy |
| `vnc_click_type.py` | Mouse/keyboard control | ❌ Not working |
| `type_hello.py` | Typing test script | ❌ Not working |
| `set-vnc-password.ps1` | VNC password configuration | ✅ Used |

**VNC Configuration:**
- **Port:** 5900
- **Password:** Karen1234$ (from VNC_PASS env var)
- **Server:** localhost
- **Status:** Screenshot ✅, Control ❌

---

## 📧 Email System Files

| File | Purpose | Status |
|------|---------|--------|
| `send-email.ps1` | Generic email sender | ⚠️ Untested |
| `send-gmail.ps1` | Gmail-specific sender | ⚠️ Untested |
| `send-test-email.ps1` | Test email script | ⚠️ Untested |
| `test-smtp-connection.ps1` | SMTP connectivity test | ⚠️ Untested |

**Status:** Email system configured but not fully tested/operational.

---

## 🤖 Automation & Scripts

| File | Purpose | Status |
|------|---------|--------|
| `self-optimize.ps1` | System maintenance script | ✅ Active |
| `stability-monitor.ps1` | Crash prevention | ✅ Active |
| `file-auto-organizer.ps1` | Downloads folder organization | ✅ Cron job |
| `ai-news-monitor.ps1` | AI news fetching | ✅ Cron job |
| `vnc-record.ps1` | VNC recording wrapper | ⚠️ Untested |
| `setup-memory-search.py` | Memory search configuration | ⚠️ Incomplete |

---

## 📊 Research & Documentation

| File | Purpose | Date |
|------|---------|------|
| `RESEARCH-REPORT-2026-02-25.md` | OpenClaw upgrades research | 2026-02-25 |
| `CAPABILITY-RESEARCH.md` | Web search capabilities | 2026-02-22 |
| `WEB-SEARCH-SETUP.md` | Web search configuration guide | 2026-02-22 |
| `DRIVE-RESEARCH.md` | Storage upgrade research | 2026-02-22 |
| `RAM-UPGRADE-RESEARCH.md` | RAM upgrade research | 2026-02-22 |
| `RAM-BEST-VALUE.md` | RAM value analysis | 2026-02-22 |
| `HARDWARE.md` | Hardware overview | 2026-02-22 |
| `RESEARCH-FINDINGS.md` | Research compilation | 2026-02-22 |
| `EFFICIENCY-RESEARCH.md` | System efficiency | 2026-02-22 |
| `BACKUP-PLAN.md` | Backup strategy | 2026-02-22 |

---

## 🔧 System Fix Documentation

| File | Purpose | Date |
|------|---------|------|
| `STABILITY-FIXES.md` | Crash prevention fixes | 2026-02-21 |
| `MILESTONE-FOUNDATION-COMPLETE.md` | Foundation completion | 2026-02-21 |
| `KAREN-VOICE.md` | Personality guide | 2026-02-23 |
| `PARTNERSHIP.md` | Working relationship terms | 2026-02-21 |

---

## ⚠️ Known Issues Documentation

### Critical Issues (Documented in TOOLS.md)
1. **Ollama + local-automation agent:** Timeout due to sandbox isolation
2. **llama3.2:3b tool calling:** Outputs in wrong format
3. **Email system:** Not fully operational
4. **Memory search:** No local model configured

### Files Related to Issues
- `PENDING-TASKS.md` - Outstanding work items
- `RESEARCH-REPORT-2026-02-25.md` - Ollama issue research

---

## 🗂️ Directory Structure

```
~/.openclaw/
├── workspace/           # Working directory
│   ├── *.md            # Documentation files
│   ├── *.py            # Python scripts
│   ├── *.ps1           # PowerShell scripts
│   ├── memory/         # Daily memory logs
│   └── .openclaw/      # State files
├── agents/             # Agent configurations
│   ├── main/           # Main agent
│   └── local-automation/ # Local automation agent
├── cron/               # Cron job definitions
├── logs/               # Log files
└── config files        # openclaw.json, node.json
```

---

## 📋 File Maintenance Checklist

**Weekly:**
- [ ] Review and archive old memory files (>30 days)
- [ ] Clean up orphaned files in workspace
- [ ] Update FILE-INDEX.md if new files added

**Monthly:**
- [ ] Review TOOLS.md for accuracy
- [ ] Update known issues section
- [ ] Archive completed research documents

**As Needed:**
- [ ] Document new tools/capabilities immediately
- [ ] Update when fixes are applied
- [ ] Add new files to this index

---

## 🔍 How to Use This Index

**Looking for a specific capability?**
→ Check `TOOLS.md` first

**Looking for what happened on a specific date?**
→ Check `memory/YYYY-MM-DD.md`

**Looking for VNC details?**
→ This file (VNC section) + `memory/2026-02-21.md`

**Looking for system configuration?**
→ `~/.openclaw/openclaw.json`

**Looking for what's broken?**
→ `TOOLS.md` (Known Issues) + `PENDING-TASKS.md`

---

## 💡 Key Insight

**Most files are in one of three places:**
1. **Workspace root** (`~/.openclaw/workspace/`) - Scripts and docs
2. **Memory folder** (`memory/`) - Daily logs
3. **Config folder** (`~/.openclaw/`) - System configuration

**If you can't find something:**
1. Check this index
2. Check `TOOLS.md`
3. Search the workspace: `dir /s /b filename`

---

*"An unindexed system is a forgotten system."* 🦞