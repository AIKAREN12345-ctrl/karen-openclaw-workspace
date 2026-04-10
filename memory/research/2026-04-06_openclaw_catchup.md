# OpenClaw Updates Catch-Up Report
**Date:** April 6, 2026  
**Research Period:** March 27 - April 6, 2026  
**Current Version:** 2026.4.5 (latest stable)

---

## Executive Summary

OpenClaw has seen significant releases in the 2026.4.x series, with major architectural changes including **Task Flows** (durable background orchestration), **massive security hardening**, **new AI providers**, and **media generation tools**. The current system is running 2026.2.24, which is approximately 6 weeks behind the latest release.

---

## Version Timeline

| Version | Release Date | Type |
|---------|--------------|------|
| 2026.3.22 | March 23, 2026 | Maintenance |
| 2026.3.31 | March 31, 2026 | **Major** - Breaking changes |
| 2026.4.1 | April 1, 2026 | Feature release |
| 2026.4.2 | April 2, 2026 | **Major** - Task Flows, Security |
| 2026.4.5 | April 3-5, 2026 | **Latest** - Config cleanup, providers, dreaming |

---

## 2026.4.5 Release Highlights

### Breaking Changes
- **Legacy config aliases removed**: Old public config paths like `talk.voiceId`, `talk.apiKey`, `agents.*.sandbox.perSession`, `browser.ssrfPolicy.allowPrivateNetwork`, and channel/group/room `allow` toggles have been removed in favor of canonical paths and `enabled` flags.
- **Migration**: Use `openclaw doctor --fix` to migrate existing configs automatically.

### Major New Features

#### 1. Media Generation Tools
- **`video_generate`** - Built-in tool for AI video generation through configured providers
- **`music_generate`** - Built-in tool for AI music/audio generation with Google Lyria, MiniMax, and ComfyUI workflow support
- **ComfyUI Plugin** - Bundled workflow media plugin supporting `image_generate`, `video_generate`, and `music_generate` with prompt injection and reference-image upload

#### 2. New AI Providers
- **Qwen** (Alibaba) - Chat and embeddings
- **Fireworks AI** - Chat and inference
- **StepFun** - Chat provider
- **MiniMax** - TTS, search, and chat
- **Ollama Web Search** - Local search integration
- **Amazon Bedrock Mantle** - Inference-profile discovery with automatic request-region injection
- **xAI Video** - `grok-imagine-video` support
- **Alibaba Model Studio Wan** - Video generation
- **Runway** - Video generation

#### 3. Memory/Dreaming (Experimental)
- **Weighted short-term recall promotion** - Background memory promotion
- **`/dreaming` command** - Trigger memory consolidation
- **Dreams UI** - Visual interface for memory dreams
- **Three cooperative phases**: Light, Deep, and REM with independent schedules
- **Configurable aging controls**: `recencyHalfLifeDays`, `maxAgeDays`
- **Dream Diary** - Surface in Dreams UI with lobster animation

#### 4. Prompt Caching Improvements
- More reusable prompt prefixes across transport fallback
- Deterministic MCP tool ordering
- Normalized system-prompt fingerprints
- Cache diagnostics in `openclaw status --verbose`
- Removed duplicate in-band tool inventories

#### 5. Claude CLI Integration
- OpenClaw tools exposed to Claude CLI via loopback MCP bridge
- Bundled runs use stdin + `stream-json` partial-message streaming
- Persisted session bindings with rotation on `/new` and `/reset`

---

## 2026.4.2 Release Highlights

### Breaking Changes
1. **xAI Search Config Migration**
   - Old: `tools.web.x_search.*`
   - New: `plugins.entries.xai.config.xSearch.*`
   - Auth: `plugins.entries.xai.config.webSearch.apiKey` / `XAI_API_KEY`

2. **Firecrawl Web Fetch Migration**
   - Old: `tools.web.fetch.firecrawl.*`
   - New: `plugins.entries.firecrawl.config.webFetch.*`

**Fix**: Run `openclaw doctor --fix` to auto-migrate both.

### Major Features

#### Task Flows (Background Orchestration)
- **Durable state management** - Flows survive gateway restarts
- **Managed vs mirrored sync modes** - Choose persistence strategy
- **Revision tracking** - Full history of flow changes
- **`openclaw tasks flow`** - Inspection and recovery commands
- **Managed child task spawning** - Cancel parent → children finish gracefully
- **Plugin API access** - `api.runtime.taskFlow` seam for plugin authors

#### Android Google Assistant Integration
- "Hey Google, ask OpenClaw..." voice commands
- Hands-free prompt delivery to chat composer
- Works with node pairing for remote server control

#### Security Hardening (Massive)
- Centralized request auth, proxy, TLS, and header handling
- **Blocked insecure TLS overrides** - No more disabling TLS verification
- Native-vs-proxy endpoint classification for OpenAI, Anthropic, Copilot
- Exec routing respects boundaries - `host=auto` routes correctly
- Provider routing hardened - spoofed hosts can't inherit defaults

#### Plugin Hooks
- **`before_agent_reply`** - Plugins can short-circuit LLM with synthetic replies
- Use cases: FAQ bots, inline actions, rate limiting

#### Slack Improvements
- Built-in `mrkdwn` formatting guidance
- Proper bold, code blocks, links, lists rendering

---

## 2026.4.1 Release Highlights

### Features
- **macOS Voice Wake** - Trigger Talk Mode with voice
- **`/tasks` chat command** - Background task board in chat
- **SearXNG Web Search** - Bundled provider for self-hosted search
- **Amazon Bedrock Guardrails** - Content filtering support
- **Z.AI GLM-5.1 & GLM-5v-turbo** - New models
- **Global default provider params** - `agents.defaults.params`
- **Cron tool allowlists** - `openclaw cron --tools`

---

## 2026.3.31 Release Highlights

### Breaking Changes
1. **Node exec unified** - `nodes.run` shell wrapper removed; use `exec host=node`
2. **Plugin SDK deprecation** - Legacy provider compat subpaths deprecated
3. **Dangerous code scanning** - Now fails closed by default; requires `--dangerously-force-unsafe-install` override
4. **Trusted-proxy auth** - Rejects mixed shared-token configs
5. **Node commands** - Disabled until pairing is approved

### Major Features
- **Background Tasks Control Plane** - SQLite-backed ledger unifying ACP, subagent, cron, and CLI execution
- **QQ Bot Channel** - Multi-account setup, slash commands, reminders
- **LINE Outbound Media** - Images, video, audio sends
- **Matrix Streaming** - Draft streaming for partial replies
- **MCP Remote HTTP/SSE** - Remote server support with auth headers
- **WhatsApp Reactions** - Emoji reactions on incoming messages

---

## Migration Checklist for 2026.2.24 → 2026.4.5

### Before Upgrade
1. Backup current config: `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup`
2. Review custom xAI/Firecrawl configs if present
3. Check for legacy config paths (talk.voiceId, talk.apiKey, etc.)
4. Review any `--dangerously-*` install overrides you depend on

### After Upgrade
1. Run `openclaw doctor --fix` (handles all config migrations)
2. Run `openclaw doctor` to verify health
3. Test Task Flows: `openclaw tasks list`
4. Verify exec approvals still work as expected
5. Check memory backend settings if using QMD

### Known Issues to Watch
- **Ollama + local-automation agent** - Still has sandbox isolation timeout issues (workaround: use `agent:main`)
- **llama3.2:3b tool calling** - Still outputs tools in `content` instead of `tool_calls` (use qwen2.5 instead)

---

## Sources

1. **Official Changelog**: https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md
2. **GitHub Releases**: https://github.com/openclaw/openclaw/releases
3. **OpenClaw Playbook Blog**: https://www.openclawplaybook.ai/blog/openclaw-2026-4-2-release-task-flows-android-assistant/
4. **The Stack Observer**: https://thestackobserver.com/openclaw-2026-4-2-task-flow-returns-with-durable-state-management/
5. **Blink Blog (2026.4.1)**: https://blink.new/blog/openclaw-2026-4-1-whats-new-update-guide
6. **NewReleases Tracker**: https://newreleases.io/project/github/openclaw/openclaw

---

## Recommendations

1. **Upgrade Priority**: HIGH - The security hardening alone justifies the upgrade
2. **Test Task Flows** - This is a game-changer for automation reliability
3. **Try video/music generation** - New creative capabilities available
4. **Review memory/dreaming** - Experimental but promising for long-term context
5. **Keep using qwen2.5:14b** - Still the recommended local model

---

*Report generated by Karen (OpenClaw subagent) on April 6, 2026*
