# OpenClaw Research Report - April 6, 2026

**Compiled:** April 6, 2026  
**Focus:** Latest updates, security advisories, and community news

---

## 1. OpenClaw 2026.4.5 - Latest Release (April 6, 2026)

**Released:** April 6, 2026 at 03:04 UTC  
**GitHub Stars:** 349K+ | **Forks:** 70K+

### Breaking Changes
- **Config cleanup:** Removed legacy public config aliases (`talk.voiceId`, `talk.apiKey`, `agents.*.sandbox.perSession`, etc.) in favor of canonical paths. `openclaw doctor --fix` provides migration support.

### Major New Features

#### Media Generation
- **Video generation:** New built-in `video_generate` tool with support for xAI (grok-imagine-video), Alibaba Model Studio Wan, and Runway providers
- **Music generation:** New `music_generate` tool with Google Lyria, MiniMax, and ComfyUI workflow support
- **ComfyUI integration:** Bundled workflow media plugin for local ComfyUI and Comfy Cloud (image, video, music generation)

#### New Providers
- **Qwen, Fireworks AI, StepFun** - Full provider bundles added
- **MiniMax TTS and Search** integrations
- **Ollama Web Search** integration
- **Amazon Bedrock Mantle** support with inference-profile discovery

#### Memory & Dreaming (Experimental)
- Weighted short-term recall promotion
- `/dreaming` command with Dreams UI
- Three cooperative phases: light, deep, REM
- Configurable aging controls (`recencyHalfLifeDays`, `maxAgeDays`)
- Dream Diary surface in Dreams UI
- Content written to `dreams.md` instead of daily notes

#### Claude CLI Integration
- Expose OpenClaw tools to background Claude CLI runs via MCP bridge
- Persist session bindings and rotate on `/new` and `/reset`
- Multiple security hardenings for CLI backend isolation

#### Platform Improvements
- **Control UI:** Multilingual support (12 languages including Chinese, Portuguese, German, Spanish, Japanese, Korean, French, Turkish, Indonesian, Polish, Ukrainian)
- **iOS:** APNs exec approval notifications with in-app modal
- **Matrix:** Native exec approval prompts with room-thread aware resolution
- **Telegram:** Fixed model picker, HTML formatting, topic replies, reaction persistence

### Key Bug Fixes
- **Security:** 5 security fixes including plugin tool allowlist preservation, SSRF redirect blocking, browser origin auth throttling
- **Prompt caching:** Major improvements to cache reuse across transport fallback, tool ordering, and image history
- **Auto-reply:** Unified reply lifecycle ownership fixes
- **Cron:** Failure notifications now route through primary delivery channel
- **Gateway:** Windows/macOS restart reliability improvements

---

## 2. 2026.4.x Series Highlights

### 2026.4.2 (April 2, 2026)
- **Task Flows** - Background orchestration substrate with durable state management
- **Android Google Assistant** integration
- **Massive security tightening** across the platform
- xAI plugin config moved to `plugins.entries.xai.config.xSearch.*`

### 2026.4.1 (April 1, 2026)
- **Task Board** in chat interface
- **Voice wake** functionality
- **Bedrock Guardrails** support
- Smarter failover mechanisms

---

## 3. Security Advisories

### Critical

#### CVE-2026-28466 (CVSS 9.9)
- **Affected:** OpenClaw < 2026.2.14
- **Issue:** Broken access control in node.invoke parameters - authenticated clients could bypass exec approval gating
- **Impact:** Remote code execution on connected node hosts
- **Fix:** Update to 2026.2.14+
- **EPSS:** 9.3% probability of exploitation in next 30 days

### High

#### CVE-2026-32918 (CVSS 8.4)
- **Affected:** OpenClaw < 2026.3.11
- **Issue:** Session sandbox escape via session_status tool - sandboxed subagents could access parent/sibling session state
- **Impact:** Leak sensitive conversation/session data, manipulate model/session behavior
- **Fix:** Update to 2026.3.11+
- **CWE:** CWE-863 (Incorrect Authorization)

#### GHSA-56pc-6hvp-4gv4 (OC-06)
- **Affected:** OpenClaw <= 2026.2.15
- **Issue:** Arbitrary file read via `$include` directive - path traversal in config resolution
- **Impact:** Exposure of local secrets, API keys, private config material
- **Fix:** Update to 2026.2.17+
- **CWE:** CWE-22 (Path Traversal)

#### CVE-2026-28463
- **Issue:** Exec-approvals allowlist validation bypass - safe binaries could read arbitrary files via shell expansion

#### CVE-2026-28470 (CVSS 9.8)
- **Issue:** Command injection vulnerability

### Security Best Practices
- Run `openclaw doctor` after updates to check and fix config issues
- Review exec approval policies regularly
- Keep gateway and node versions synchronized
- Use `openclaw doctor --fix` for migration assistance

---

## 4. Community News & Discussions

### Major Platform Changes (April 2026)

#### Google & Anthropic Policy Changes
- **Google** is restricting Google AI Pro/Ultra subscribers using OpenClaw - users reporting account restrictions without warning
- **Anthropic** ended Claude subscription support for third-party tools including OpenClaw - users must now use pay-per-use or extra usage fees
- Community reaction: "Third-party Claude wrapper era is cooked"

### Community Stats
- **GitHub:** 349K+ stars, 70K+ forks, 1,568+ contributors
- **Open Issues:** 17,088
- **Sponsors:** 186 (including romainhuet, davemorin)
- **Daily Token Volume:** 822 billion tokens processed daily (3x nearest rival through OpenRouter)

### Hot Community Topics

1. **Kimi web_search 401 fix** [HOT - 72 engagement points]
   - Authentication errors resolved with proper baseURL configuration
   - Issue #44851

2. **PathGuard Filesystem Security** [PR #39764]
   - Major security overhaul introducing policy-driven filesystem access control

3. **SkyPilot Cloud Deployment Tutorial**
   - 208 engagement points for cloud VM deployment guide
   - Cost optimization tips for remote OpenClaw setups

4. **Qwen3.5-9b-Opus-OpenClaw-Distilled Model**
   - New fine-tuned model optimized for OpenClaw
   - 962+ downloads

### Recent Fixes from Community
- GitHub Copilot IDE authentication headers (PR #60641)
- macOS binary detection for Homebrew installs (Issue #17890)
- Telegram voice note transcription (PR #61008)

---

## 5. Action Items for Users

1. **Update to 2026.4.5** - Contains important security fixes and new features
2. **Run `openclaw doctor --fix`** - Migrate legacy config paths
3. **Review Anthropic/Google provider setup** - Policy changes may affect billing
4. **Consider enabling Dreaming** - New experimental memory feature for better recall
5. **Check exec approval policies** - Ensure compliance with latest security model

---

## Sources

- GitHub Releases: https://github.com/openclaw/openclaw/releases
- OpenClaw Hub: https://openclaw-hub.com/releases/
- OpenClaw Newsletter (April 4, 2026): https://buttondown.com/openclaw-newsletter/
- RedPacket Security CVE Alerts
- LeakyCreds Vulnerability Database
- GitHub Security Advisories

---

*Report compiled by subagent research task on April 6, 2026*
