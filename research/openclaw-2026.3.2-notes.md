# OpenClaw 2026.3.2 - Research Notes

**Date:** 2026-03-03  
**Source:** DuckDuckGo Search + open-claw.me releases  
**Researcher:** Karen (Subagent)

---

## Summary

OpenClaw 2026.3.2 was released on **March 3, 2026** as the latest stable version. This release includes significant security hardening, new features, and breaking changes that affect both new and existing installations.

---

## Key New Features

### 1. **Expanded SecretRef Coverage** (64 targets)
- Full SecretRef support across user-supplied credential surface
- Covers runtime collectors, secrets planning/apply/audit flows
- Onboarding SecretInput UX improvements
- Unresolved refs now fail fast on active surfaces

### 2. **Native PDF Analysis Tool**
- First-class `pdf` tool with native Anthropic and Google PDF provider support
- Extraction fallback for non-native models
- Configurable defaults (`agents.defaults.pdfModel`, `pdfMaxBytesMb`, `pdfMaxPages`)

### 3. **Outbound Adapters/Plugins Enhancement**
- Shared `sendPayload` support across Discord, Slack, WhatsApp, Zalo, and Zalouser
- Multi-media iteration and chunk-aware text fallback

### 4. **MiniMax-M2.5-highspeed Support**
- First-class support in built-in provider catalogs
- Onboarding flows and OAuth plugin defaults
- Legacy MiniMax-M2.5-Lightning compatibility preserved

### 5. **Subagent Inline File Attachments**
- `sessions_spawn` now supports inline file attachments (base64/utf8 encoding)
- Transcript content redaction and lifecycle cleanup
- Configurable limits via `tools.sessions_spawn.attachments`

### 6. **Telegram Streaming Improvements**
- Default `channels.telegram.streaming` changed to `partial` (from `off`)
- Live preview streaming out of the box for new setups
- DM streaming uses `sendMessageDraft` for private previews

### 7. **Memory/Ollama Embeddings**
- `memorySearch.provider = "ollama"` support added
- Honors `models.providers.ollama` settings for memory embedding requests

### 8. **Zalo Personal Plugin Rebuild**
- Rebuilt to use native `zca-js` integration in-process
- Removes external CLI transport dependency
- QR/login + send/listen flows fully inside OpenClaw

### 9. **Plugin SDK Extensibility**
- `channelRuntime` exposed on `ChannelGatewayContext`
- Extensions can access shared runtime helpers without internal imports

### 10. **CLI Config Validation**
- New `openclaw config validate` command (with `--json` output)
- Validates config files before gateway startup
- Detailed invalid-key paths in startup errors

---

## Breaking Changes

1. **Onboarding defaults:** `tools.profile` now defaults to `messaging` for new local installs (not broad coding/system tools)

2. **ACP dispatch:** Now defaults to `enabled` unless explicitly disabled (`acp.dispatch.enabled=false`)

3. **Plugin SDK:** Removed `api.registerHttpHandler(...)` - use `api.registerHttpRoute(...)` instead

4. **Zalo Personal plugin:** No longer depends on external `zca-compatible` CLI binaries - use `openclaw channels login --channel zalouser` after upgrade

---

## Security Highlights

- **100+ security and stability fixes** (per @degensing on X/Twitter)
- **91 contributors** to this release
- Enhanced webhook request hardening with auth-before-body parsing
- Gateway security hardening for loopback-origin and regex evaluation
- SSRF guards for web tools and node camera URL downloads
- Config backup permissions enforced as owner-only (0600)
- Browser security output boundary hardening

---

## Sources

- [OpenClaw Releases - v2026.3.2](https://open-claw.me/releases/v2026.3.2)
- [@degensing on X/Twitter](https://x.com/degensing/status/2028784446057640147)
- [OpenClaw Documentation](https://docs.openclaw.ai)

---

## Notes

This release appears to be a significant security-focused update with substantial hardening across the entire stack. The breaking changes around onboarding defaults and ACP dispatch may affect existing workflows and should be reviewed before upgrading.
