# MEMORY.md — Long-Term Memory

_Last updated: 2026-04-08 (Dream cycle caught up — no new content)_

---

## 🧠 Core Identity
- **Name:** Karen
- **Platform:** OpenClaw AI Assistant
- **User:** Ken
- **Connection:** Telegram (@Karen_G_Bot)
- **Emoji Signature:** 🦞

## 👤 User
- **Name:** Ken
- **Timezone:** Europe/Dublin
- **Communication Style:** Prefers concise, thorough when it matters. Not a fan of corporate speak.
- **Preferences:** Actions over words, resourcefulness before asking

## 🏗️ Projects

### OpenClaw System Management
- **Status:** Active
- **Current Version:** 2026.4.5 (updated from 2026.3.2 on 2026-04-06)
- **Node:** DESKTOP-M8AO8LN (Windows 11)
- **Key Components:**
  - Gateway service (ws://127.0.0.1:18789)
  - Ollama with local models (qwen2.5:14b, qwen3.5:9b)
  - 12+ cron jobs for automated research
  - Memory system with semantic search
- **Related:** See Research Automation project (shares cron infrastructure)
- **See also:** Key Decisions (2026-04-06) for upgrade details
- **See also:** Strategy section (this project implements the strategy)
- **See also:** Episode — OpenClaw System Build (2-month journey)

### Research Automation
- **Status:** Active
- **Schedule:** Every 2 hours from 7 AM to 9 PM
- **Topics:**
  - OpenClaw AI updates (9 AM, 4 PM)
  - KDP coloring books (10:30 AM)
  - Self-improvement (7 AM)
  - AI tools (1 PM)
  - Local LLM (3 PM)
  - Security (5 PM)
  - Emerging tech (7 PM)
  - Philosophy (9 PM)
- **Related:** See OpenClaw System Management (cron infrastructure)
- **See also:** Lessons Learned (Ollama + local-automation agent timeout)
- **See also:** Strategy section (automation in action)
- **See also:** Episode — OpenClaw System Build (research system evolution)

## 💰 Business

### KDP Coloring Books
- **Status:** Research phase
- **Focus:** Passive income through Amazon KDP
- **Research:** Automated daily at 10:30 AM
- **Notes:** Exploring trends, niche opportunities, AI-assisted design
- **See also:** Research Automation (KDP research at 10:30 AM)

### Biltong Wholesale
- **Status:** Active
- **Description:** Wholesale biltong distribution
- **Notes:** [Add details as available]

### Retail Butcher Shop
- **Status:** Active
- **Description:** Local retail butcher operation
- **Notes:** [Add details as available]

### Social Media for Local Businesses
- **Status:** Active
- **Focus:** Social media management services
- **Clients:** Local businesses
- **Notes:** [Add details as available]

- **See also:** Session Archive (storage metrics tracked)
- **See also:** Strategy section (business growth aligns with strategy)

## 👥 People & Team
- **Ken:** Primary user and system administrator
- **GitHub:** AIKAREN12345-ctrl

## 🎯 Strategy
- Keep system updated while avoiding breaking changes
- Automate research to stay informed without manual effort
- Maintain local LLM capabilities for privacy and cost efficiency
- Document lessons learned for continuous improvement
- **See also:** OpenClaw System Management project (implements this strategy)
- **See also:** Research Automation project (automation in action)
- **See also:** Episode — OpenClaw System Build (2-month journey)

## 📌 Key Decisions

**2026-04-06** — Updated to OpenClaw 2026.4.5
- Enabled dreaming feature (3 AM daily)
- Re-enabled 8 research cron jobs
- Fixed tools.profile: "full" for full tool access
- *Related to:* OpenClaw System Management project

**2026-04-03** — Downgraded from OpenClaw 2026.4.1 to 2026.3.2
- Critical bug #48457 blocked all interpreter commands
- Restored PowerShell and Python execution
- Fixed memory search and Telegram groupPolicy
- *Related to:* Lessons Learned (Bug #48457)

**2026-04-03** — Installed 6 new skills
- github, autonomous-research, x-monitor, web-monitor, x-agent, vault

## 💡 Lessons Learned

- **Bug #48457:** OpenClaw 2026.4.1 had critical regression blocking PowerShell/Python
  - *Related to:* Key Decisions (2026-04-03 downgrade)
- **Version pinning:** Sometimes staying on stable version is better than latest
- **Node command routing:** Requires proper parameter adjustment (rawCommand mismatch)
- **Ollama + local-automation agent:** Timeout due to sandbox isolation - use agent:main instead
  - *Related to:* Research Automation (uses agent:main for subagents)

## 🔧 Environment

**System:**
- OS: Windows 11 (DESKTOP-M8AO8LN)
- OpenClaw: 2026.4.5
- Node: v24.13.1
- Python: 3.11.9
- Shell: PowerShell
- **See also:** Session Archive (system snapshots)

**AI Models:**
- Cloud: Kimi k2.5 (primary for interactive work)
- Local: qwen2.5:14b, qwen3.5:9b (automation)
- Embeddings: nomic-embed-text

**Storage:**
- Disk: ~17% used (773+ GB free / 930.4 GB total)
- Memory: 200 files, 1335 chunks indexed
- **See also:** memory/session-archive/ (daily backups)

## 🌊 Open Threads
- Configure installed skills (github, x-monitor, etc.)
- Test VNC scripts now that Python is working
- Monitor for OpenClaw 2026.4.1+ bug fix before upgrading
- **See also:** Session Archive (automated cleanup at 23:00)

## 📝 Jobs To Be Done

### Local Optimization
- **Status:** Research phase
- **Goal:** Achieve fully local, efficient Karen operation
- **Technologies to explore:**
  - **TurboQuant** — Google's KV cache compression (6x memory reduction, 8x speedup)
  - **1-bit LLMs** — Microsoft BitNet b1.58 (10x energy reduction, 400MB models)
  - **Better local models** — Qwen 3, DeepSeek for stronger reasoning
  - **GPU acceleration** — llama.cpp optimizations
- **See also:** Research Automation (local-llm research at 3 PM)

### Paperclip.ing Integration
- **Status:** Research phase
- **Goal:** Explore open-source orchestration for zero-human workflows
- **URL:** https://paperclip.ing/
- **Notes:** AI agent orchestration platform — could enhance our automation
- **Action:** Research integration possibilities
- **See also:** Business projects (automation aligns with zero-human goals)

<!-- consolidated -->
