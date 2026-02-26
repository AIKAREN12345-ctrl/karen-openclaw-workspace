# FILE-INDEX.md - Complete System Documentation

**Last Updated:** 2026-02-26
**System:** OpenClaw 2026.2.25 on Windows 11 (DESKTOP-M8AO8LN)

---

## 📁 Core Configuration Files (Outside Workspace)

| File | Purpose | Location |
|------|---------|----------|
| `~/.openclaw/openclaw.json` | Main OpenClaw configuration | C:\Users\Karen\.openclaw\ |
| `~/.openclaw/node.json` | Node connection settings | C:\Users\Karen\.openclaw\ |
| `~/.openclaw/cron/jobs.json` | Cron job definitions | C:\Users\Karen\.openclaw\cron\ |

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
| `FILE-INDEX.md` | This file - complete file inventory | 2026-02-26 |
| `START-HERE.md` | System entry point for every session | 2026-02-26 |

---

## 🤝 Partnership & Working Relationship

| File | Purpose | Created |
|------|---------|---------|
| `PARTNERSHIP-RHYTHM.md` | How Ken and I work together | 2026-02-25 |
| `KAREN-VOICE.md` | Personality guide | 2026-02-23 |
| `KAREN-PLAYBOOK.md` | Operational guide | 2026-02-23 |

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
| `memory/2026-02-25.md` | Feb 25 | ❌ Missing |
| `memory/2026-02-26.md` | Feb 26 | ✅ Created |

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
| `vnc-control.py` | Mouse/keyboard control | ✅ Working |
| `setup-memory-search.py` | Memory search configuration | ⚠️ Incomplete |

**VNC Configuration:**
- **Port:** 5900
- **Password:** Karen1234$ (from VNC_PASS env var)
- **Server:** localhost
- **Status:** Screenshot ✅, Recording ✅, Control ✅

---

## 📧 Email System Files

| File | Purpose | Status | Location |
|------|---------|--------|----------|
| `email-config.ps1` | Email configuration | ✅ Configured | C:\Users\Karen\ |
| `send-email.ps1` | Email sending script | ✅ Fixed | C:\Users\Karen\ |

**Status:** Script fixed, needs Microsoft SMTP auth enabled in account settings.

---

## 📊 Research & Documentation

| File | Purpose | Date |
|------|---------|------|
| `RESEARCH-FINDINGS-2026-02-23.md` | Research compilation | 2026-02-23 |
| `OLLAMA-ISSUE-SUMMARY.md` | Ollama problems research archive | 2026-02-25 |
| `POST-UPDATE-2026.2.24.md` | Update log & lessons learned | 2026-02-25 |
| `SKILLS-REVIEW.md` | Skills assessment | 2026-02-25 |

---

## 🔧 System Fix Documentation

| File | Purpose | Date |
|------|---------|------|
| `PENDING-TASKS.md` | Outstanding work items | 2026-02-24 |
| `CDP-INVESTIGATION-LESSONS.md` | Browser CDP lessons | 2026-02-23 |
| `OPENCLAW-BUG-REPORT.md` | Bug reports | 2026-02-23 |
| `SESSION-REPORT-2026-02-23.md` | Session summary | 2026-02-23 |
| `WEEKLY-ACHIEVEMENT-REPORT-FEB-17-24-2026.md` | Weekly report | 2026-02-24 |

---

## ⚠️ Known Issues Documentation

### Critical Issues (Documented in TOOLS.md)
1. **Ollama + local-automation agent:** Timeout due to sandbox isolation
2. **llama3.2:3b tool calling:** Outputs in wrong format
3. **Email system:** Needs Microsoft SMTP auth enabled
4. **Memory search:** Deferred until local LLM setup

---

## 🗂️ Directory Structure

```
~/.openclaw/
├── workspace/           # Working directory
│   ├── *.md            # Documentation files
│   ├── *.py            # Python scripts
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

## 🔍 How to Use This Index

**Looking for a specific capability?**
→ Check `TOOLS.md` first

**Looking for what happened on a specific date?**
→ Check `memory/YYYY-MM-DD.md`

**Looking for VNC details?**
→ This file (VNC section)

**Looking for system configuration?**
→ `~/.openclaw/openclaw.json`

**Looking for what's broken?**
→ `TOOLS.md` (Known Issues) + `PENDING-TASKS.md`

---

## 📋 File Maintenance Checklist

**Weekly:**
- [ ] Review and archive old memory files (>30 days)
- [ ] Update FILE-INDEX.md if new files added

**Monthly:**
- [ ] Review TOOLS.md for accuracy
- [ ] Update known issues section

**As Needed:**
- [ ] Document new tools/capabilities immediately
- [ ] Update when fixes are applied
- [ ] Add new files to this index

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

**Last Verified:** 2026-02-26
**Git Status:** Clean working tree

---

*"An accurate index is more valuable than a comprehensive one."* 🦞
