# OpenClaw Research - March 9, 2026

**Date:** 2026-03-09  
**Topic:** OpenClaw Updates and Changelog  
**Source:** GitHub Releases, DuckDuckGo Search

---

## Latest Release: OpenClaw v2026.3.8 (March 9, 2026)

### Major New Features

#### 1. **CLI Backup System** ⭐
- New commands: `openclaw backup create` and `openclaw backup verify`
- Local state archives with manifest/payload validation
- Options: `--only-config`, `--no-include-workspace`
- Backup guidance in destructive flows
- Improved archive naming for date sorting

#### 2. **Context Engine Plugin Interface** ⭐
- Full lifecycle hooks: bootstrap, ingest, assemble, compact, afterTurn
- Slot-based registry with config-driven resolution
- Enables alternative context management strategies
- Zero behavior change when no plugin configured
- Plugin example: lossless-claw for alternative compaction

#### 3. **ACP Persistent Channel Bindings** ⭐
- Durable Discord channel and Telegram topic binding storage
- Routing resolution survives restarts
- CLI and documentation support
- Telegram topic thread binding (--thread here|auto)

#### 4. **Talk Mode Improvements**
- New config: `talk.silenceTimeoutMs`
- Configurable silence wait before auto-sending
- Preserves platform-specific defaults when unset

#### 5. **Web Search Enhancements**
- Brave LLM Context endpoint support (`tools.web.search.brave.mode: "llm-context"`)
- Extracted grounding snippets with source metadata
- Perplexity Search API with structured results
- Language/region/time filters
- Alphabetized provider ordering

### Security & Authentication

#### Gateway Auth Changes (BREAKING)
- **Required:** Explicit `gateway.auth.mode` when both token and password configured
- Options: `token` or `password`
- Set before upgrade to avoid startup failures
- SecretRef support for `gateway.auth.token`

#### ACP Provenance
- Optional ingress provenance metadata
- Visible receipt injection
- Config: `openclaw acp --provenance off|meta|meta+receipt`
- Session trace IDs for ACP-origin context

### Platform Improvements

#### macOS
- Remote gateway token field for remote mode
- Browser proxy through local node browser service
- Plain-text paste semantics preserved
- LaunchAgent restart recovery
- Universal binaries by default
- Light terminal background detection

#### Browser/CDP
- `browser.relayBindHost` for WSL2/non-loopback setups
- Normalized loopback WebSocket CDP URLs
- Wildcard URL rewriting for container endpoints
- Reconnect flake reduction

#### Android
- Removed: self-update, background location, screen.record
- Narrowed foreground service to dataSync only
- Play Store compliance improvements

### Bug Fixes

#### Telegram
- DM deduplication per agent
- Cron announce delivery routing
- Partial streaming fixes

#### Matrix
- Safer m.direct fallback detection
- Explicit room binding honor

#### Memory & Context
- Clear stale cached contextTokens on model switch
- Session:compact:before/after events
- Post-compaction section configurability

### Developer Experience

#### Docker
- Multi-stage builds for minimal runtime image
- `OPENCLAW_EXTENSIONS` for preinstalling dependencies
- `OPENCLAW_VARIANT=slim` for bookworm-slim

#### CLI
- Git commit hash in `openclaw --version`
- Read-only SecretRef status flows

#### TUI
- Agent inference from workspace
- Light/dark theme auto-detection

---

## Previous Release: v2026.3.7 (March 8, 2026)

### Highlights
- Context Engine Plugin Interface
- ACP Persistent Channel Bindings
- Spanish locale support (Web UI)
- Google/Gemini 3.1 Flash-Lite support
- MiniMax-M2.5-highspeed (replaced Lightning)

### Breaking Changes
- Gateway auth mode requirement (same as 3.8)
- Default tools.profile changed to `coding` (from `messaging`)

---

## Summary

**OpenClaw is actively developed** with frequent releases (3.7 and 3.8 within 2 days). Key themes:

1. **Reliability** - Backup system, persistent bindings
2. **Extensibility** - Plugin interfaces, context engines
3. **Security** - Auth hardening, provenance tracking
4. **Cross-platform** - macOS, Android, Docker improvements
5. **Developer experience** - CLI enhancements, multi-stage builds

**For our setup:**
- The backup system is relevant for our Docker deployment
- Context engine plugins could enhance our agent swarm
- Gateway auth changes don't affect our current local setup

---

*Research conducted manually - Docker swarm file saving to be implemented tomorrow*
