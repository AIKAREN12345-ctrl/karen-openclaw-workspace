# Qwen 3.5 Ollama Issue Research Report
**Date:** 2026-03-05
**Topic:** Why qwen3.5:9b fails with "unexpected EOF" and timeouts

## Summary

Qwen 3.5 models are currently **broken on Ollama 0.17.5** due to a known issue with the model runner crashing. This is a widespread problem affecting all Qwen 3.5 variants.

## The Issue

**Symptoms:**
- Model loads successfully (appears in `ollama ps`)
- First inference attempt causes runner crash
- "unexpected EOF" error from API
- `ollama run` times out
- Model runner stops unexpectedly

**Root Cause:**
The Ollama model runner crashes with a **segmentation fault (SIGSEGV)** when attempting to generate with Qwen 3.5 models. This is happening in the `ggml_backend_sched_graph_compute_async` function during graph computation.

**Error from logs:**
```
SIGSEGV: segmentation violation
PC=0x7f10c3ef6787 m=31 sigcode=1 addr=0x609000
signal arrived during cgo execution
runtime.cgocall(...)
github.com/ollama/ollama/ml/backend/ggml._Cfunc_ggml_backend_sched_graph_compute_async(...)
```

## Affected Configurations

From GitHub issues research:
- **All Qwen 3.5 variants:** 0.8b, 2b, 4b, 9b, 27b, 35b, 122b
- **All platforms:** Linux (Vulkan, ROCm, CPU), Windows
- **Ollama version:** 0.17.5 (latest)
- **GPU backends:** Vulkan, ROCm, CUDA, CPU-only

## Attempted Workarounds (That Don't Work)

1. **Setting `OLLAMA_CONTEXT_LENGTH=4096`** — Does not fix the crash
2. **Using different GPU backends** — Crashes on Vulkan, ROCm, and CPU
3. **Smaller models** — Even 0.8b crashes
4. **Re-pulling the model** — Same crash after fresh download
5. **Flash attention enabled/disabled** — No effect

## Why It Sometimes Appears to Work

The model loads successfully and appears in `ollama ps`, which makes it seem like it's working. However, the crash only happens on the **first inference attempt**, not during loading.

## Current Status

**GitHub Issues:**
- Issue #14550: "Error running Qwen3.5 models using ollama-vulkan" (Open, 11 comments)
- Issue #14487: "qwen3.5 any seems to not work with Vulkan backend" (Closed, but same issue)
- Issue #14444: "qwen3.5:35b fails with cudaMemcpyAsyncReserve" (Closed, related)

**Official Response:**
Ollama maintainers are aware of the issue. The crash is in the GGML backend during graph computation for the Qwen35MoE architecture.

## Recommendation

**DO NOT use Qwen 3.5 models with Ollama until this is fixed.**

Stick with:
- **qwen2.5:14b** — Working perfectly
- **Other models** — llama3.2, phi4, gemma2, etc.

## When Will It Be Fixed?

No ETA from Ollama team. The issue is marked as a bug and is being investigated. Given the severity (complete crash on inference), it's likely a high priority fix.

## Workaround for Now

Use Qwen 3.5 via:
1. **Alibaba Cloud API** — qwen3.5-plus via ModelStudio
2. **Hugging Face Transformers** — Direct Python usage
3. **Wait for Ollama fix** — Check GitHub issues for updates

## Sources
- https://github.com/ollama/ollama/issues/14550
- https://github.com/ollama/ollama/issues/14487
- https://github.com/ollama/ollama/issues/14444
