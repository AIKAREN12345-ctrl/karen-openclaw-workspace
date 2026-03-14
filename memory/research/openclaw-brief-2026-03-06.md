# OpenClaw Updates - March 2026 Brief

**Date:** 2026-03-06  
**Source:** GitHub Releases, Web3Wire, DuckDuckGo Search

## Key Updates (Last Week)

- **OpenClaw 2026.3.2 Released (March 3)** — Major stable release with new PDF analysis tool (native Anthropic/Google support), expanded SecretRef credential management across 64 integration targets, and first-class MiniMax-M2.5-highspeed model support.

- **Zalo Personal Plugin Rebuilt** — Now uses native zca-js integration in-process, removing external CLI dependencies. Users need to re-authenticate with `openclaw channels login --channel zalouser` after upgrading.

- **New Subagent File Attachments** — `sessions_spawn` now supports inline file attachments with base64/utf8 encoding for subagent runtime, enabling richer task delegation workflows.

- **Ollama Embeddings for Memory Search** — Added `memorySearch.provider = "ollama"` support, allowing local embedding models for memory search without cloud dependencies.

- **Security & Breaking Changes** — New installs now default to `tools.profile: messaging` (narrower tool access). ACP dispatch now defaults to enabled. Plugin SDK removed `registerHttpHandler` in favor of explicit `registerHttpRoute`.

## Notable Milestone

OpenClaw surpassed **250,000 GitHub stars** (March 4), overtaking React's star count — achieved in roughly 60 days since its November 2025 launch as Clawdbot.

---
*Research compiled via DuckDuckGo search and GitHub release notes.*
