# Proactive Research Report - March 3, 2026

## Topics Researched
1. OpenClaw Releases & Features (Daily, High Priority)
2. Security Alerts & Patches (Daily, High Priority)

---

## 1. OpenClaw 2026.3.1 Release - Major Update

**Release Date:** March 2, 2026  
**Previous Version:** 2026.2.26  
**Status:** ✅ New version available

### Key New Features

#### 🔐 Secrets Management Overhaul
- **Full SecretRef coverage** across 64 targets including runtime collectors, secrets planning/apply/audit flows
- Unresolved refs now fail fast on active surfaces
- Non-blocking diagnostics for inactive surfaces
- PR #29580 by @joshavant

#### 📄 Native PDF Analysis Tool
- First-class PDF tool with native Anthropic and Google PDF provider support
- Extraction fallback for non-native models
- Configurable defaults: `agents.defaults.pdfModel`, `pdfMaxBytesMb`, `pdfMaxPages`
- PR #31319 by @tyler6204

#### 🔌 Plugin SDK Improvements
- **Zalo Personal plugin rebuilt** - now uses native zca-js integration in-process (no external CLI needed)
- **STT API** - Extensions can now transcribe local audio files via `api.runtime.stt.transcribeAudioFile()`
- **Session lifecycle hooks** - sessionKey now included in session_start/session_end events
- **Message hooks** - New `message:transcribed` and `message:preprocessed` events

#### 💬 Telegram Enhancements
- **Streaming defaults** - channels.telegram.streaming now defaults to `partial` (live preview out of the box)
- **DM streaming** - Uses sendMessageDraft for private preview streaming
- **Voice mention gating** - Optional `disableAudioPreflight` to skip mention-detection for voice notes

#### 🧠 Memory & Embeddings
- **Ollama embeddings support** - `memorySearch.provider = "ollama"` now available
- Honors `models.providers.ollama` settings for memory embedding requests

#### ⚙️ CLI & Configuration
- **Config validation** - New `openclaw config validate` command with `--json` output
- **Banner taglines** - New `cli.banner.taglineMode` setting (random | default | off)

### Breaking Changes ⚠️

1. **Onboarding defaults** - New local installs now default `tools.profile` to `messaging` (not broad coding/system tools)
2. **ACP dispatch** - Now defaults to `enabled` unless explicitly disabled with `acp.dispatch.enabled=false`
3. **Plugin SDK** - Removed `api.registerHttpHandler()` - use `api.registerHttpRoute()` instead
4. **Zalo Personal** - No longer depends on external zca-compatible CLI binaries

### Action Items for Ken
- [ ] Review if ACP dispatch changes affect current setup
- [ ] Consider enabling PDF analysis for document processing tasks
- [ ] Update Zalo Personal plugin if using (requires re-login via `openclaw channels login --channel zalouser`)

---

## 2. Security Alerts - February 2026 Patch Tuesday

**Patch Date:** February 10, 2026  
**Next Patch Tuesday:** March 10, 2026 (expected)  
**Status:** ⚠️ Critical updates available

### Summary
Microsoft patched **59 vulnerabilities** including **6 actively exploited zero-days**.

| Severity | Count |
|----------|-------|
| Critical | 5 |
| Important | 52 |
| Moderate | 2 |

### Actively Exploited Zero-Days (Patch Immediately!)

| CVE | CVSS | Component | Impact |
|-----|------|-----------|--------|
| CVE-2026-21510 | 8.8 | Windows Shell | Security feature bypass |
| CVE-2026-21513 | 8.8 | MSHTML Framework | Security feature bypass |
| CVE-2026-21514 | 7.8 | Microsoft Office Word | Security feature bypass |
| CVE-2026-21519 | 7.8 | Desktop Window Manager | Privilege escalation |
| CVE-2026-21525 | 6.2 | Windows Remote Access Connection Manager | DoS |
| CVE-2026-21533 | 7.8 | Windows Remote Desktop | Privilege escalation |

### Key Details

**CVE-2026-21510, CVE-2026-21513, CVE-2026-21514**
- Protection mechanism failures allowing security feature bypass
- Can be exploited via crafted files (HTML or Office documents)
- Discovered by Microsoft security teams and Google Threat Intelligence Group

**CVE-2026-21533 (Remote Desktop)**
- Exploit binary modifies service configuration key
- Enables privilege escalation to add users to Administrator group
- Reported by CrowdStrike

**CVE-2026-21519 (Desktop Window Manager)**
- Type confusion vulnerability
- Allows local privilege escalation to SYSTEM

### CISA KEV Catalog
All six vulnerabilities have been added to CISA's Known Exploited Vulnerabilities catalog. Federal agencies were required to patch by **March 3, 2026** (today).

### Secure Boot Certificate Update
Microsoft is rolling out updated Secure Boot certificates to replace the original 2011 certificates expiring in June 2026. These install automatically through Windows Update.

### Action Items for Ken
- [ ] **URGENT:** Ensure Windows is updated to latest patch (KB5077181) - OS Builds 26200.7840 / 26100.7840
- [ ] Verify all 6 zero-days are patched on your system
- [ ] Check if Remote Desktop is enabled (disable if not needed)

---

## Sources

### OpenClaw
- https://github.com/openclaw/openclaw/releases
- https://newreleases.io/project/github/openclaw/openclaw/release/v2026.3.1

### Security
- https://thehackernews.com/2026/02/microsoft-patches-59-vulnerabilities.html
- https://msrc.microsoft.com/update-guide/releaseNote/2026-feb
- https://support.microsoft.com/en-us/topic/february-10-2026-kb5077181-os-builds-26200-7840-and-26100-7840

---

*Research completed: March 3, 2026*  
*Next research due: March 4, 2026 (OpenClaw & Security)*
