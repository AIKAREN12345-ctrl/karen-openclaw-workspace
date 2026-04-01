# OpenClaw Local Subagents - Research Findings

## The Core Problem

There are **TWO separate but related bugs** preventing local Ollama subagents from working:

### Bug #1: GitHub Issue #43945 (Auth Pipeline)
**"Subagents miss Ollama credentials and silently fall back to cloud models"**

**Root Cause:**
- Ollama uses `apiKey: "ollama-local"` as a marker (placeholder)
- The auth pipeline classifies this as a "non-secret" and excludes it from `auth-profiles.json`
- Subagents rely exclusively on `auth-profiles.json` for credentials
- Result: 401 auth error → silent fallback to cloud models (GPT-4.1-mini)

**Privacy Impact:**
- Users think data stays local, but it silently routes to OpenAI/Google
- No warning, no log entry visible to users
- Only detectable in deep gateway logs (`/tmp/openclaw/openclaw-*.log`)

**Status:** Open, affects OpenClaw 2026.3.11

---

### Bug #2: GitHub Issue #24654 (Subagent Spawning)
**"Subagent spawning fails with local Ollama models"**

**Root Cause:**
- Subagent registers with Gateway but never spawns Ollama conversation
- Fails immediately (~168ms) with no error message
- No transcript file created
- Issue is specific to `subagent + local model` combination

**Evidence:**
- Main session + Ollama: ✅ Works
- Subagent + API model: ✅ Works  
- Subagent + Ollama: ❌ Fails immediately

**Status:** Open, affects OpenClaw 2026.2.19-2 and likely later

---

## Why Your Cron Jobs Failed Last Night

Your cron jobs were configured to spawn subagents with `model: kimi-coding/k2p5`.
The failures happened because:

1. **Subagent spawning itself is broken** for local contexts (Bug #24654)
2. Even if they spawned, Ollama credentials wouldn't propagate (Bug #43945)
3. The 10-minute timeout was the cron job waiting for a subagent that never started

---

## Workarounds (Until Fixed)

### Workaround 1: Run Directly in Main Session (What We Just Did)
- Skip subagent spawning entirely
- Execute research directly using `web_fetch` in main session
- ✅ No auth issues, no spawning failures
- ✅ Working now

### Workaround 2: Manual Auth Profiles Fix (Hacky)
```bash
# Add Ollama entries to auth-profiles.json manually:
{
  "ollama-local:default": {
    "type": "api_key",
    "provider": "ollama-local",
    "key": "sk-ollama-dummy"  # NOT "ollama-local" - that's a marker!
  }
}

# Protect from gateway overwrite:
chmod 444 ~/.openclaw/agents/main/agent/auth-profiles.json
```
⚠️ Caveats:
- Prevents gateway from updating ANY provider keys
- Must unprotect to add/rotate other API keys
- Updates may regenerate the file

### Workaround 3: Use API Models for Subagents
- Use `kimi-coding/k2p5` or other cloud models
- Costs money but works reliably
- Defeats purpose of local models

---

## Proposed Fixes (From GitHub Issues)

### Fix 1: Propagate All apiKeys to auth-profiles.json
Write all `models.providers.*.apiKey` values regardless of marker classification.

### Fix 2: Skip Auth for Auth-Free Providers
Introduce `auth: "none"` capability for Ollama and similar local backends.

### Fix 3: Fail-Closed Policy Flag
Add `allowCloudFallback: false` or `requireLocal: true` to prevent silent cloud routing.

### Fix 4: Surface Fallback Decisions
User-visible warning when model fallback crosses local→cloud boundary.

### Fix 5: Fix Subagent Spawning
Debug why subagents fail immediately with Ollama models.

---

## Current Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Main session + Ollama | ✅ Working | Interactive chat works fine |
| Cron jobs (direct) | ✅ Working | Our new approach |
| Subagent + Ollama | ❌ Broken | Bug #24654 |
| Subagent + API | ✅ Working | Costs money |
| Auth propagation | ❌ Broken | Bug #43945 |

---

## Recommendation

**Keep using direct execution** (what we implemented today) until OpenClaw fixes both bugs. The research is working now without subagents.

**Monitor these GitHub issues:**
- https://github.com/openclaw/openclaw/issues/43945 (Auth)
- https://github.com/openclaw/openclaw/issues/24654 (Spawning)

When fixed, we can re-enable subagent-based research if needed.

---

*Research completed: 2026-04-01*
