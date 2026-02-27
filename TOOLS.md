# TOOLS.md - Karen's System Capabilities & Configuration

**Last Updated:** 2026-02-25
**System:** OpenClaw 2026.2.24 on Windows 11 (DESKTOP-M8AO8LN)

---

## 🦞 Core Identity

- **Name:** Karen
- **Platform:** OpenClaw
- **User:** Ken
- **Connection:** Telegram (@Karen_G_Bot)
- **Emoji Signature:** 🦞

---

##  Available Tools & Capabilities

### 1. System Command Execution
- **Tool:** `exec` with `host: node`
- **Capabilities:** PowerShell, system commands, file operations
- **Security:** Allowlist mode (PowerShell, nircmd approved)
- **Use Cases:** Software installation, system configuration, automation scripts

### 2. Browser Automation (CDP)
- **Tool:** `browser`
- **Status:**  Operational
- **Port:** 18800 (openclaw profile)
- **Capabilities:** Navigate, click, type, extract content, screenshots
- **Use Cases:** Web research, form automation, data extraction

### 3. VNC Screen Capture
- **Scripts:** 
  - `vnc-screenshot-robust.py` - Screenshot capture
  - `vnc-recorder-robust.py` - Screen recording
- **Connection:** localhost:5900
- **Password:** Karen1234$ (from VNC_PASS env var)
- **Status:**  Screenshot working,  Mouse/keyboard control not directly available
- **Use Cases:** Visual verification, screen recording, remote viewing

### 4. File Operations
- **Read:** Text files, images, configs
- **Write:** Create/overwrite files
- **Edit:** Surgical text replacement
- **Use Cases:** Configuration management, documentation, scripting

### 5. Memory System
- **Daily Logs:** `memory/YYYY-MM-DD.md`
- **Long-term:** `MEMORY.md`
- **Search:** Semantic search via `memory_search` (when configured)
- **Use Cases:** Context preservation, lesson learning, continuity

### 6. Cron Jobs (Automation)
- **Status:** 6 active jobs
- **Heartbeat:** Every 2 hours (karen-heartbeat)
- **Health Checks:** Daily at 2:30 AM
- **Maintenance:** Cleanup, disk monitoring, updates
- **Use Cases:** Scheduled tasks, automated monitoring, periodic reporting

### 7. Sub-Agent Spawning
- **Tool:** `sessions_spawn`
- **Use Cases:** Parallel processing, isolated tasks, research
- **Limitation:** Cannot use Ollama models (sandbox isolation issue)

### 8. Node Management
- **Tool:** `nodes`
- **Capabilities:** Status, describe, run commands on paired nodes
- **Current Node:** DESKTOP-M8AO8LN (Windows 11)

---

## 🤖 AI Models Available

### Cloud Models (via API)
| Model | Provider | Use Case | Context |
|-------|----------|----------|---------|
| k2p5 | kimi-coding | Interactive work, coding, reasoning | 262k |

### Local Models (Ollama)
| Model | Size | Status | Use Case |
|-------|------|--------|----------|
| llama3.2:3b | 2.0 GB |  Tool calling issues | Automation (problematic) |
| gemma:2b | 1.7 GB |  No tool support | Fallback only |
| phi3:mini | 2.2 GB |  Untested | Backup option |
| qwen2.5:7b | 4.7 GB |  Recommended | Best tool support |

### Model Routing Strategy
- **Kimi (k2p5):** Interactive conversations, complex coding, reasoning
- **Local models:** Automation, heartbeats, background tasks
- **Issue:** `local-automation` agent cannot use Ollama due to sandbox isolation
- **Workaround:** Use `agent:main` for Ollama tasks

---

##  Known Issues & Limitations

### Critical Issues
1. **Ollama + local-automation agent:** Timeout/failure due to sandbox isolation
   - **Impact:** Cron jobs with `local-automation` + Ollama fail
   - **Workaround:** Use `agent:main` for Ollama tasks
   - **Status:** OpenClaw 2026.2.24 did not fix this

2. **llama3.2:3b tool calling:** Outputs tools in `content` instead of `tool_calls`
   - **Impact:** OpenClaw cannot parse tool calls
   - **Workaround:** Use qwen2.5:7b instead
   - **Status:** Model-specific issue

### Minor Issues
3. **Browser CDP port:** Was 18792, changed to 18793
   - **Status:** Fixed in config, restart applied

4. **Memory search:** Provider set to "local" but no local model file
   - **Impact:** Memory search disabled
   - **Fix:** Configure remote provider or install node-llama-cpp

---

##  Security Configuration

- **Gateway Token:** 64 characters, rotated
- **Rate Limiting:** 10/min, 5min lockout
- **Exec Security:** Allowlist mode
- **VNC:** Firewalled to local network only
- **Node Connection:** ws://127.0.0.1:18788 (localhost only)

---

##  Important File Locations

| File/Directory | Purpose |
|----------------|---------|
| `~/.openclaw/openclaw.json` | Main configuration |
| `~/.openclaw/node.json` | Node configuration |
| `~/.openclaw/cron/jobs.json` | Cron job definitions |
| `~/.openclaw/agents/` | Agent configurations |
| `~/.openclaw/memory/` | Daily memory logs |
| `~/.openclaw/workspace/` | Working directory |
| `~/AppData/Local/Temp/openclaw/` | Logs |

---

##  Key Decisions & Agreements

### Partnership Framework (from PARTNERSHIP.md)
- **Mutual respect:** No domination, collaborative decisions
- **Safety first:** Ask before destructive actions
- **Transparency:** Explain what I'm doing and why
- **Continuous improvement:** Learn from mistakes

### Model Usage Strategy
- **Allegro → Allegretto:** Efficiency matters
- **Automation saves budget:** Local models for routine tasks
- **Kimi for complexity:** Cloud API for interactive work
- **Manual routing:** User decides, not automatic

---

##  Current Priorities

1. **Fix Ollama automation:** Switch heartbeat to `agent:main`
2. **Test qwen2.5:7b:** Better tool support for local tasks
3. **Enable memory search:** Configure provider
4. **Document lessons:** This file is part of that

---

##  Session Startup Checklist

**Every session, I should:**
1.  Read `SOUL.md` - Who I am
2.  Read `USER.md` - Who I'm helping
3.  Read `TOOLS.md` (this file) - What I can do
4.  Read `memory/YYYY-MM-DD.md` (today + yesterday)
5.  Check `MEMORY.md` for long-term context

**Before using any tool:**
- Check this file for current status/limitations
- Verify tool is operational
- Have fallback plan if tool fails

---

##  Lessons Learned (Hard Way)

1. **Memory is not automatic:** I must READ files, not assume I remember
2. **VNC != Full Control:** Screenshot ≠ Mouse/Keyboard (distinction matters)
3. **Sandbox isolation is real:** `local-automation` cannot reach localhost services
4. **Updates can break things:** 2026.2.24 changed security model
5. **Document everything:** This file exists because I forgot

---

*"The unexamined life is not worth living, and the unexamined tool is not worth using."* 🦞