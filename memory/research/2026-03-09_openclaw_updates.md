# OpenClaw Updates Research - March 9, 2026

**Research Date:** 2026-03-09  
**Latest Version:** 2026.3.7 (Released March 8, 2026)

---

## Overview

OpenClaw has seen significant updates in early 2026, with the latest stable release being **v2026.3.7** (released March 8, 2026). This document summarizes the major changes, new features, and breaking changes across recent releases.

---

## Latest Release: v2026.3.7 (March 8, 2026)

### Major New Features

#### 1. Context Engine Plugin Interface
- **Feature:** New `ContextEngine` plugin slot with full lifecycle hooks
- **Hooks:** `bootstrap`, `ingest`, `assemble`, `compact`, `afterTurn`, `prepareSubagentSpawn`, `onSubagentEnded`
- **Purpose:** Enables plugins like `lossless-claw` to provide alternative context management strategies
- **Impact:** Zero behavior change when no context engine plugin is configured
- **PR:** #22201 by @jalehman

#### 2. ACP Persistent Channel Bindings
- **Feature:** Durable Discord channel and Telegram topic binding storage
- **Benefit:** ACP thread targets now survive restarts and can be managed consistently
- **Includes:** Routing resolution and CLI/docs support
- **PR:** #34873 by @dutifulbob

#### 3. Telegram Topic Agent Routing
- **Feature:** Per-topic `agentId` overrides in forum groups and DM topics
- **Benefit:** Topics can route to dedicated agents with isolated sessions
- **PR:** #33647 by @kesor and @Sid-Qin

#### 4. Spanish Locale Support (Web UI)
- **Feature:** Spanish (`es`) locale in Control UI
- **Includes:** Locale detection, lazy loading, and language picker labels
- **PR:** #35038 by @DaoPromociones

#### 5. PDF Analysis Tool
- **Feature:** First-class `pdf` tool with native Anthropic and Google PDF provider support
- **Fallback:** Extraction fallback for non-native models
- **Config:** `agents.defaults.pdfModel`, `pdfMaxBytesMb`, `pdfMaxPages`
- **PR:** #31319 by @tyler6204

#### 6. SecretRef Support Expansion
- **Feature:** SecretRef support expanded across 64 credential targets
- **Includes:** Runtime collectors, secrets planning/apply/audit flows, onboarding UX
- **Behavior:** Unresolved refs now fail fast on active surfaces
- **PR:** #29580, #35094 by @joshavant

#### 7. Docker Multi-Stage Build
- **Feature:** Restructured Dockerfile for minimal runtime images
- **Benefits:** No build tools, source code, or Bun in final image
- **Variant:** `OPENCLAW_VARIANT=slim` for bookworm-slim variant
- **PR:** #38479 by @sallyom

#### 8. Plugin SDK Enhancements
- **prependSystemContext/appendSystemContext:** Static plugin guidance in system prompt space
- **allowPromptInjection:** New hook policy for prompt injection control
- **Channel extensibility:** `channelRuntime` exposed on `ChannelGatewayContext`
- **STT transcribeAudioFile:** Extensions can transcribe local audio files
- **Session lifecycle hooks:** Include `sessionKey` in `session_start`/`session_end` events

---

## Breaking Changes

### v2026.3.7 Breaking Changes

1. **Gateway Auth Mode Required**
   - When both `gateway.auth.token` and `gateway.auth.password` are configured, explicit `gateway.auth.mode` is now required
   - Set to `token` or `password` before upgrading
   - **PR:** #35094

### v2026.3.2 Breaking Changes

1. **Default Tools Profile Changed**
   - New local installs now default `tools.profile` to `messaging` instead of `coding`
   - New setups no longer start with broad coding/system tools unless explicitly configured

2. **ACP Dispatch Default Changed**
   - ACP dispatch now defaults to `enabled` unless explicitly disabled
   - Set `acp.dispatch.enabled=false` to pause ACP turn routing

3. **Plugin SDK HTTP Handler Removal**
   - `api.registerHttpHandler(...)` removed
   - Use `api.registerHttpRoute({ path, auth, match, handler })` instead

4. **Zalo Personal Plugin Changes**
   - No longer depends on external zca-compatible CLI binaries
   - Uses native zca-js integration in-process

---

## Notable Improvements

### Agent & Context Management
- **Compaction post-context configurability:** Choose which AGENTS.md sections re-inject after compaction via `agents.defaults.compaction.postCompactionSections`
- **Compaction model override:** Route compaction summarization through a different model than the main session
- **Tool-result truncation:** Head+tail truncation for oversized tool results, preserving important tail diagnostics
- **Context pruning hardening:** Guard against malformed assistant content entries

### Channel & Platform Features
- **Telegram streaming defaults:** Now defaults to `partial` for live preview streaming
- **Telegram DM streaming:** Uses `sendMessageDraft` for private preview streaming
- **Slack typing reaction:** `channels.slack.typingReaction` for Socket Mode DMs
- **Discord allowBots:** `allowBots: "mentions"` to only accept bot-authored messages that mention the bot
- **Mattermost model picker:** Interactive provider/model browsing

### Security & Configuration
- **Config validation:** `openclaw config validate` command with `--json` output
- **Security hardening:** Fail closed when `loadConfig()` hits validation errors
- **SecretRef flows:** Read-only SecretRef status flows degrade safely
- **Cron file permissions:** Owner-only (`0600`) enforcement for cron files

### Developer Experience
- **CLI backup commands:** `openclaw backup create` and `openclaw backup verify`
- **TUI theme detection:** Light terminal background detection via `COLORFGBG`
- **Browser CDP improvements:** Better startup diagnostics, WSL2 support
- **iOS App Store Connect prep:** Bundle identifiers aligned, Fastlane automation

---

## Model Support Updates

### New Model Support
- **Google/Gemini 3.1 Flash-Lite:** First-class support added
- **MiniMax-M2.5-highspeed:** Added to provider catalogs
- **OpenAI Codex/GPT-5.4:** Forward compatibility with 1,050,000-token context window

### Model Fixes
- **Kimi Coding:** Anthropic tools compatibility normalized
- **Venice:** Model onboarding hardened, tool wiring disabled for non-FC models
- **xAI/Grok:** Web-search collision guard, HTML-entity decoding for tool arguments

---

## Bug Fixes (Selected)

### Critical Fixes
- **Memory/Hybrid search:** Preserved negative FTS5 BM25 relevance ordering
- **LINE requireMention:** Aligned group policy resolution
- **Gateway/Telegram:** Stale-socket restart guard to prevent restart storms
- **Feishu multi-app:** Fixed mention detection in multi-bot groups
- **Slack app_mention:** Race dedupe to prevent duplicate replies

### Stability Improvements
- **Browser session cleanup:** Tabs opened by session-scoped browser tool runs are now tracked and closed on session teardown
- **Gateway restart timeout:** Exit non-zero when restart-triggered shutdown drains time out
- **Cron restart catch-up:** Staggered replay of missed jobs on startup
- **Subagent completion:** Fixed announce race conditions

---

## Unreleased Changes (In Development)

Based on the main branch changelog, upcoming features include:

- **Talk mode silence timeout:** Configurable `talk.silenceTimeoutMs`
- **TUI workspace inference:** Active agent inferred from current workspace
- **Brave LLM Context mode:** Opt-in `tools.web.search.brave.mode: "llm-context"`
- **ACP Provenance:** Optional ingress provenance metadata and receipt injection
- **Browser relay bind host:** `browser.relayBindHost` for WSL2/cross-namespace setups

---

## Summary

OpenClaw 2026.3.7 represents a significant milestone with:

1. **Plugin ecosystem expansion** - Context engine interface and SDK enhancements
2. **Enterprise features** - Persistent bindings, SecretRef coverage, Docker improvements
3. **Platform maturity** - Spanish i18n, PDF analysis, multi-stage builds
4. **Breaking changes** - Gateway auth mode requirement, default profile changes

Users should review breaking changes before upgrading, particularly the gateway auth mode configuration requirement.

---

**Sources:**
- https://github.com/openclaw/openclaw/releases
- https://raw.githubusercontent.com/openclaw/openclaw/main/CHANGELOG.md
