# System Configuration - OpenClaw Setup

**Last Updated:** 2026-03-02

## Host System
- **Hostname:** DESKTOP-M8AO8LN
- **OS:** Windows 11 (25H2) / Windows 10 (reports vary)
- **Platform:** AMD64
- **CPU:** 16 cores
- **RAM:** 19.8GB total
- **Disk:** 930.4GB total (~12% used)

## OpenClaw Configuration
- **Version:** 2026.2.25
- **Gateway:** ws://127.0.0.1:18788 (local loopback)
- **Channel:** Telegram (enabled, DM policy: pairing)
- **Model:** Kimi K2.5 (kimi-coding/k2p5) for main, Ollama for local-automation

## Local LLM Setup (Ollama)
- **Base URL:** http://localhost:11434
- **Models Available:**
  - qwen2.5:14b (NEW - upgraded today!)
  - qwen2.5:7b
  - qwen2.5:3b
  - llama3.2:3b
  - gemma:2b
  - phi3:mini
  - nomic-embed-text (for embeddings)

## Recent Upgrades (2026-03-02)
- **14B Model Integration:** Successfully upgraded from 7B to 14B
  - All scripts updated (ollama_research.py, ollama_monitor.py)
  - OpenClaw config updated
  - local-automation agent using 14B
  - Timeout increased to 90s for slower but higher quality responses
  - Tested and working - research quality noticeably improved

## Monitoring System
- **Cron Jobs Running:**
  - pulse_check.py (every 30 min)
  - ollama_monitor.py (every 15 min)
  - memory_log_local.py (hourly)
  - system_analysis.py (every 4 hours)
  - ollama_research.py (every 2 hours)

## Memory System Status
- **Daily Logs:** 11 files (2026-02-20 through 2026-03-02)
- **Research Files:** 8 completed topics
- **Semantic Search:** BROKEN (EISDIR bug in OpenClaw plugin)
- **Workaround:** Manual knowledge base (this file!)

## Web Search
- **DuckDuckGo script:** Working (no API key needed)
- **Kimi web search:** Authentication issue (401 error)

## Security Notes
- 2 critical warnings (Host-header fallback, small model sandboxing)
- Update available (npm 2026.3.1)
- 19 active sessions

---
*System configuration maintained by Karen*
