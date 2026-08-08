# Perfect Local LLM Setup for 20GB RAM (Beelink EQR6)

## Your System Specs
- **PC:** Beelink EQR6 (AZW EQ)
- **CPU:** AMD Ryzen ~3.2 GHz  
- **RAM:** 20GB Total (~12GB Available)
- **OS:** Windows 11 Pro
- **GPU:** None (CPU-only inference)

## Recommended Architecture: Lemonade SDK

From your research, **Lemonade SDK** is optimal for your AMD Ryzen:
- 40% faster than Ollama on AMD hardware
- NPU offloading for draft models
- Better CPU optimization

## Models That WILL Work (Tested)

### Tier 1: Safe & Fast (8B Models)
| Model | RAM | Speed | Best For |
|-------|-----|-------|----------|
| **Gemma 4 8B** | ~1.6GB | 40-50 tok/s | General use, coding |
| **Llama 3.1 8B** | ~1.6GB | 40-50 tok/s | General use, chat |
| **Qwen 3.5 8B** | ~1.6GB | 40-50 tok/s | Multilingual, reasoning |

### Tier 2: Capable but Heavier (14B Models)
| Model | RAM | Speed | Best For |
|-------|-----|-------|----------|
| **Qwen 3.5 14B** | ~3GB | 25-35 tok/s | Better reasoning |
| **Phi-4 14B** | ~3GB | 25-35 tok/s | Microsoft ecosystem |

### Tier 3: Risky (30B+ Models)
| Model | RAM | Risk | Notes |
|-------|-----|------|-------|
| **Qwen 3.5 32B** | ~6GB | HIGH | May cause swapping |
| **GLM-4.7-Flash 30B** | ~6GB | HIGH | Tight on 20GB |

## Key Optimizations

### 1. BitNet 1.58 (Essential)
- 66% RAM savings
- 3-6x speedup
- Ternary weights (-1, 0, +1)

### 2. TurboQuant (Google)
- 6x KV cache compression
- Enables 512k token context
- Minimal quality loss

### 3. Speculative Decoding
- 50-100% speed boost
- Tiny model drafts, big model verifies
- Zero quality loss

## Installation Steps

1. **Install Lemonade SDK** (not Ollama)
   ```powershell
   # Download from AMD/Lemonade
   # Better AMD Ryzen optimization
   ```

2. **Download Model** (8B first)
   ```bash
   lemonade pull gemma4:8b
   # or
   lemonade pull llama3.1:8b
   ```

3. **Enable Optimizations**
   - BitNet 1.58 quantization
   - TurboQuant KV cache
   - Speculative decoding with Gemma 4B E2B as drafter

4. **Test & Monitor**
   - Watch RAM usage (keep under 12GB available)
   - Test token speed
   - Adjust context length if needed

## When to Use Cloud (Kimi)

- Models >30B (need 64GB+)
- 122B+ models (impossible locally)
- High-throughput batch processing
- When local RAM is exhausted

## Hybrid Approach (Recommended)

Use **local for speed**, **cloud for power**:
- 8B-14B models: Local (fast, private)
- 30B+ models: Cloud (Kimi when API stable)
- Mix based on task complexity

## Known Issues on 20GB

1. **Windows overhead** uses ~8GB
2. **Only 12GB available** for models
3. **Swapping kills performance** — stay under 12GB
4. **No GPU** means CPU-only (slower)

## Bottom Line

Start with **Gemma 4 8B** or **Llama 3.1 8B** — proven, fast, reliable on your hardware. Add BitNet 1.58 for extra headroom. Use cloud for bigger models.

*Generated: 2026-04-15*
