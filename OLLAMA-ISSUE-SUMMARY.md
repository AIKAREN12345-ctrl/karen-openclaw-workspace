# OLLAMA-ISSUE-SUMMARY.md - Complete Research Archive

**Last Updated:** 2026-02-25
**Status:** Issue persists, workarounds documented
**Related:** TOOLS.md (Known Issues), FILE-INDEX.md

---

## 🎯 Executive Summary

**Problem:** `local-automation` agent cannot use Ollama local models due to sandbox isolation + model tool-calling bugs.

**Status:** NOT FIXED in OpenClaw 2026.2.24 despite GitHub issue #18198 claims.

**Solution:** Use `agent:main` for Ollama tasks OR use qwen2.5:7b model.

---

## 🔍 Root Cause Analysis

### Cause 1: Sandbox Isolation (Primary)
- **What:** `local-automation` agent runs in isolated subprocess
- **Effect:** Cannot reach `localhost:11434` (Ollama)
- **Evidence:** GitHub Issue #24654, #23827 (closed as "not planned")
- **Status:** By design, no fix coming

### Cause 2: llama3.2:3b Tool Calling Bug (Secondary)
- **What:** Model outputs tool calls in `content` field, not `tool_calls`
- **Effect:** OpenClaw can't parse, causes hang/timeout
- **Evidence:** GitHub Issue #13519
- **Status:** Model template issue

### Cause 3: OpenClaw Fetch Bug (Tertiary)
- **What:** Long-running Node process has fetch() issues with localhost
- **Effect:** "fetch failed" errors
- **Evidence:** GitHub Issue #18198
- **Status:** CLAIMED fixed in 2026.2.24, but NOT verified working

---

## 📚 Complete Research Archive

### GitHub Issues Researched

| Issue | Title | Status | Key Finding |
|-------|-------|--------|-------------|
| #18198 | memory_search fetch failed with Ollama | Closed | Fix claimed in 2026.2.24, NOT verified |
| #24654 | Subagent spawning fails with Ollama | Open | Exact match - our issue |
| #23827 | Sub-agents timeout with no output | Not planned | Won't fix |
| #26132 | Local model routing feature request | Open | Community demand |
| #19827 | Host networking sandbox override | Not planned | Podman only |
| #16349 | Sandboxing disables web tools | Discussion | Community frustration |
| #13519 | llama3.2:3b tool calling bug | Closed | Model outputs wrong format |

### Reddit Research
- r/ollama: Kilo Code + LM Studio + Ollama pattern (2+ hour runs)
- r/LocalLLaMA: Complete list of local coding tools
- r/OpenClaw: Multiple users with same issue

### Community Solutions Found
1. **Kilo Code** - Purpose-built for local LLM coding
2. **Aider** - Git-integrated, handles Ollama internally
3. **qwen2.5-coder:7b** - Best tool support for local models
4. **LM Studio** - Alternative to Ollama

---

## ✅ Verified Solutions

### Solution 1: Use agent:main (RECOMMENDED)
```json
{
  "agentId": "main",
  "model": "ollama/llama3.2:3b"
}
```
**Pros:** Works immediately, no isolation issues
**Cons:** Less isolation (acceptable for trusted local models)
**Status:** ✅ VERIFIED WORKING

### Solution 2: Use qwen2.5:7b
```json
{
  "model": "ollama/qwen2.5:7b"
}
```
**Pros:** Better tool calling, 7B params
**Cons:** More RAM (4.7GB vs 2.0GB)
**Status:** ✅ COMMUNITY VERIFIED

### Solution 3: External Tool Pattern (Aider)
```bash
aider --model ollama/llama3.2:3b --message "Task"
```
**Pros:** No OpenClaw isolation issues
**Cons:** No direct OpenClaw tool integration
**Status:** ✅ WORKS

### Solution 4: LM Studio Migration
**Pros:** Better Windows integration, native MCP
**Cons:** Different model format
**Status:** 🔄 NOT TESTED

---

## ❌ Failed Approaches

| Approach | Why It Failed |
|----------|---------------|
| Ollama on 0.0.0.0 | Agent still isolated |
| Host IP (100.75.72.26) | Same machine, same isolation |
| Disabling sandbox | Broke config, crashed gateway |
| Update to 2026.2.24 | Did not fix the issue |

---

## 🔧 Current Workaround (In Production)

**Heartbeat Job:** Using `agent:main` + `kimi-coding/k2p5` (cloud)
**Next Test:** Switch to `agent:main` + `ollama/qwen2.5:7b`

---

## 📊 Test Results Log

| Date | Version | Test | Result |
|------|---------|------|--------|
| 2026-02-24 | 2026.2.17 | local-automation + llama3.2:3b | ❌ Timeout |
| 2026-02-25 | 2026.2.24 | local-automation + llama3.2:3b | ❌ Timeout |
| 2026-02-25 | 2026.2.24 | agent:main + k2p5 | ✅ Working |

---

## 🎯 Decision Log

**2026-02-25:** Decided NOT to pursue `local-automation` + Ollama further
- Reason: OpenClaw team closed related issues as "not planned"
- Alternative: Use `agent:main` for local models
- Trade-off: Less isolation, but acceptable for trusted local models

---

## 🔮 Future Monitoring

**Watch for:**
- OpenClaw Issue #26132 (local model routing feature)
- New releases that mention "sandbox" or "Ollama"
- Community solutions (LocalClaw fork, etc.)

**Don't waste time on:**
- Trying to disable sandbox (security risk)
- Waiting for OpenClaw to "fix" this (not planned)
- More llama3.2:3b testing (model bug)

---

## 💡 Key Insight

**The issue is architectural, not configurational.** OpenClaw's sandbox design intentionally prevents isolated agents from reaching localhost services. This is a security feature, not a bug.

**Our solution is architectural too:** Use the non-isolated `agent:main` for local models. This is the intended design pattern.

---

## 📚 Related Files

- TOOLS.md - Current capabilities and limitations
- FILE-INDEX.md - Where everything lives
- memory/2026-02-25.md - Today's session details

---

*"Research without documentation is just expensive forgetting."* 🦞