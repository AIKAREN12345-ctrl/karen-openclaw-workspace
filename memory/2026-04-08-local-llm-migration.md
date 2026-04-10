# Local LLM Migration Attempt - April 8, 2026

## Background
**Previous Evening (April 7):** Discussed moving Karen to fully local operation using local LLMs instead of cloud APIs (Kimi). Goal was complete self-hosting for privacy and cost reasons.

## Migration Attempt (April 8 Morning)
**Started:** Morning session
**Goal:** Switch from Kimi k2.5 (cloud) to local Ollama models for all LLM operations

### Issues Encountered
1. **Hardware incompatibility** — AMD GPU not properly supported by Ollama (CUDA-only optimization)
2. **Model corruption** — Multiple "Maximum call stack" errors with local models
3. **Sandbox isolation** — OpenClaw subagents cannot reach Ollama due to Docker networking
4. **Performance issues** — CPU inference too slow for interactive use
5. **Configuration chaos** — Reinstalls, plugin disabling, re-pairing nodes

### Reversion Process
**Duration:** All day (morning to afternoon)
**Actions taken:**
- Reinstalled OpenClaw 2026.4.5
- Re-paired node multiple times
- Disabled/re-enabled plugins (unnecessary)
- Deleted 7 local LLM models (~43 GB freed)
- Fixed memory search with nomic-embed-text
- Restored Kimi k2.5 as primary model

### Final Configuration
**Chat/LLM:** Kimi k2.5 (cloud) — reliable, fast, good reasoning
**Embeddings:** nomic-embed-text (local Ollama) — privacy for memory search
**Local models:** None active (only embedding model retained)

## Lessons Learned
1. **Hardware matters** — AMD GPU not viable for Ollama in this setup
2. **Hybrid approach wins** — Cloud for chat, local for embeddings is practical
3. **Test before migrating** — Attempting full local without compatibility check caused chaos
4. **Rollback plan essential** — Took hours to restore working state

## Conclusion
Full local operation is **not viable** with current hardware (AMD GPU, no CUDA). Hybrid approach (cloud LLM + local embeddings) is the working compromise.

**Status:** System restored and operational. Memory search enabled. 43 GB disk space recovered.
