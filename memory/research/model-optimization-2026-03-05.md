# Model Quantization & Optimization for Local Inference

**Research Date:** 2026-03-05  
**Target System:** Windows 11, 24GB RAM  
**Goal:** Make local models fast enough for practical use

---

## Executive Summary

For a 24GB RAM Windows system, the optimal configuration is:
- **Primary model:** qwen2.5:7b or qwen2.5:14b with Q4_K_M quantization
- **Fast fallback:** qwen2.5:0.5b or qwen2.5:1.5b for quick tasks
- **GPU acceleration:** CUDA if available, otherwise CPU with optimized thread settings
- **Memory management:** Aggressive model unloading with short timeout

---

## 1. GGUF Quantization Formats Explained

### What is GGUF?
GGUF (GGML Universal File) is the standard format for quantized models in llama.cpp/Ollama. It replaces older GGML format and supports multiple quantization schemes.

### Quantization Types

#### K-Quants (Recommended for most users)
Format: `QX_K_X` (e.g., Q4_K_M)

| Format | Bits/Weight | Use Case | Quality |
|--------|-------------|----------|---------|
| Q2_K | 3.16 | Extreme compression | Very low |
| Q3_K_S | 3.64 | Low RAM situations | Low |
| Q3_K_M | 4.00 | Budget option | Medium-low |
| Q3_K_L | 4.30 | Better Q3 option | Medium |
| **Q4_K_S** | 4.67 | **Good balance** | **Good** |
| **Q4_K_M** | 4.89 | **Default choice** | **Good+** |
| Q4_K_L | 4.89 | Uses Q8 for embed/output | Very Good |
| Q5_K_S | 5.57 | High quality | High |
| **Q5_K_M** | 5.70 | **Near-perfect** | **Excellent** |
| Q6_K | 6.56 | Maximum quality | Near-perfect |
| Q8_0 | 8.50 | Almost no loss | Indistinguishable |

#### I-Quants (Improved quantizations - newer)
Format: `IQX_X` (e.g., IQ4_XS)

| Format | Bits/Weight | Notes |
|--------|-------------|-------|
| IQ2_XXS | 2.38 | Experimental, very small |
| IQ2_XS | 2.59 | Surprisingly usable |
| IQ3_XXS | 3.25 | Better than Q3_K_S |
| IQ3_XS | 3.50 | Comparable to Q3_K_M |
| IQ3_M | 3.66 | Good for <Q4 needs |
| IQ4_XS | 4.46 | Smaller than Q4_K_S |
| IQ4_NL | 4.68 | Near Q4_K_M quality |

**Important:** I-quants are **slower on CPU and Metal** than K-quants. Only use I-quants if you have NVIDIA/AMD GPU with cuBLAS/rocBLAS.

### Quantization Tradeoffs

**Quality vs Size:**
- Q4_K_M: ~5% quality loss vs F16, 4x smaller
- Q5_K_M: ~2% quality loss vs F16, 3x smaller
- Q6_K: ~1% quality loss vs F16, 2.5x smaller

**Speed Considerations:**
- Lower bits = faster memory transfer but more computation
- Q4_K_M is often fastest on consumer hardware due to cache efficiency
- Q8_0 is slowest due to memory bandwidth limitations

---

## 2. Best Quantization for Qwen2.5 Models

### Model Size Comparison

| Model | F16 Size | Q4_K_M | Q5_K_M | Q6_K | Q8_0 |
|-------|----------|--------|--------|------|------|
| 0.5B | 1.0 GB | 0.40 GB | 0.42 GB | 0.51 GB | 0.53 GB |
| 1.5B | 3.0 GB | 1.20 GB | 1.30 GB | 1.55 GB | 1.60 GB |
| 3B | 6.0 GB | 2.40 GB | 2.60 GB | 3.10 GB | 3.20 GB |
| 7B | 15.2 GB | 4.68 GB | 5.44 GB | 6.25 GB | 8.10 GB |
| 14B | 29.6 GB | 8.99 GB | 10.51 GB | 12.12 GB | 15.70 GB |

### Recommendations for 24GB RAM System

#### Option 1: Single Large Model (Recommended)
- **qwen2.5:14b with Q4_K_M** (~9GB)
- Leaves 15GB for OS, context, and overhead
- Best quality for complex tasks

#### Option 2: Two-Model Strategy
- **Primary:** qwen2.5:7b with Q5_K_M (~5.4GB) for quality tasks
- **Fast:** qwen2.5:0.5b with Q4_K_M (~0.4GB) for quick tasks
- Total footprint: ~6GB, leaving 18GB free

#### Option 3: Three-Model Strategy
- **Heavy:** qwen2.5:14b with Q4_K_M (~9GB) - loaded on-demand
- **Daily driver:** qwen2.5:7b with Q4_K_M (~4.7GB) - always loaded
- **Ultra-fast:** qwen2.5:0.5b with Q4_K_M (~0.4GB) - always loaded

### Specific Recommendations by Use Case

| Use Case | Recommended Model | Quant | Why |
|----------|-------------------|-------|-----|
| Coding | qwen2.5-coder:7b | Q5_K_M | Specialized training |
| Chat/QA | qwen2.5:7b | Q4_K_M | Good balance |
| Complex reasoning | qwen2.5:14b | Q4_K_M | More parameters |
| Tool calling | qwen2.5:7b | Q4_K_M | Tool support |
| Quick tasks | qwen2.5:0.5b | Q4_K_M | Speed |
| Batch processing | qwen2.5:0.5b | Q4_K_M | Efficiency |

---

## 3. GPU Acceleration on Windows

### Options Available

#### 1. NVIDIA CUDA (Best Performance)
- **Requirements:** NVIDIA GPU with CUDA support
- **Ollama:** Built-in CUDA support on Windows
- **Speedup:** 5-20x vs CPU for large models
- **VRAM requirements:** Model must fit entirely in VRAM for best performance

#### 2. AMD ROCm (Linux mainly)
- Windows support is limited/experimental
- Not recommended for Windows users currently

#### 3. DirectML (Windows AI)
- Microsoft's ML acceleration API
- Works with AMD/Intel/NVIDIA on Windows
- **Ollama status:** Not directly supported
- Alternative: Use llama.cpp with DirectML build

#### 4. Vulkan (Cross-platform)
- Works on all GPUs
- Generally slower than CUDA on NVIDIA
- Good fallback option

### GPU Memory Management

**Key insight from Ollama issues:**
- Ollama unloads models from GPU after idle timeout (default: 5 minutes)
- GPU memory leaks were fixed in v0.1.18+
- Models must fit entirely in VRAM - no partial GPU offload in Ollama

**For 24GB RAM + GPU systems:**
- If GPU has 8GB VRAM: Use qwen2.5:7b Q4_K_M (4.7GB fits comfortably)
- If GPU has 12GB VRAM: Can fit qwen2.5:14b Q4_K_M (9GB)
- If GPU has 16GB+ VRAM: Can fit qwen2.5:14b Q5_K_M (10.5GB)

### Checking GPU Support

```bash
# Check if Ollama detects GPU
ollama --version
# Look for "CUDA" or "ROCm" in output

# Force CPU mode if needed
OLLAMA_NO_GPU=1 ollama serve
```

---

## 4. Multi-Model Routing Strategies

### Strategy 1: Simple Size-Based Routing

```
User Request → Classify complexity → Route to model
                    ↓
            ┌───────┴───────┐
            ↓               ↓
        Simple          Complex
            ↓               ↓
    qwen2.5:0.5b      qwen2.5:14b
```

**Implementation:** Use prompt length or keyword heuristics

### Strategy 2: Task-Based Routing

| Task Type | Model | Quant |
|-----------|-------|-------|
| Summarization | 0.5B | Q4_K_M |
| Classification | 0.5B | Q4_K_M |
| Simple Q&A | 1.5B | Q4_K_M |
| Code generation | 7B-Coder | Q5_K_M |
| Complex reasoning | 14B | Q4_K_M |
| Creative writing | 7B | Q5_K_M |

### Strategy 3: Latency-Tiered Routing

**Tier 1 (Instant):** 0.5B model - <100ms response
**Tier 2 (Fast):** 1.5B model - <500ms response  
**Tier 3 (Standard):** 7B model - 1-3s response
**Tier 4 (Quality):** 14B model - 3-10s response

**Implementation in OpenClaw:**
- Add model selection to agent configuration
- Use 0.5B for heartbeats and simple tasks
- Use 7B for interactive work
- Use 14B for complex analysis

### Strategy 4: Context-Aware Routing

Keep multiple models loaded simultaneously:
- Always loaded: 0.5B (ultra-fast fallback)
- Usually loaded: 7B (primary workhorse)
- On-demand: 14B (complex tasks only)

**Memory footprint:** 0.4 + 4.7 + (9.0 on demand) = ~14GB peak

---

## 5. When to Use Which Model Size

### 0.5B Parameters
**Pros:**
- Blazing fast (100+ tokens/sec on CPU)
- Tiny memory footprint (0.4GB)
- Good for simple classification, extraction

**Cons:**
- Limited reasoning ability
- Poor at following complex instructions
- May hallucinate more

**Best for:**
- Text classification
- Simple entity extraction
- Routing decisions
- Format validation
- Quick summaries of short text

### 1.5B Parameters
**Pros:**
- Still very fast
- Decent instruction following
- Good for structured output

**Cons:**
- Struggles with complex reasoning
- Limited context understanding

**Best for:**
- Tool calling (simple)
- JSON generation
- Basic Q&A
- Sentiment analysis

### 7B Parameters
**Pros:**
- Good balance of speed and quality
- Excellent tool calling support
- Strong coding ability (with Coder variant)
- Fits in most consumer hardware

**Cons:**
- Slower than small models
- May struggle with very complex reasoning

**Best for:**
- General chat/assistant tasks
- Code generation and review
- Multi-step tool use
- Most practical applications

### 14B Parameters
**Pros:**
- Significantly better reasoning
- Better at following complex instructions
- Improved code quality
- Better creative writing

**Cons:**
- Slower (2-3x vs 7B)
- Higher memory requirements
- May be overkill for simple tasks

**Best for:**
- Complex analysis
- Long-form content generation
- Difficult reasoning tasks
- High-quality code generation

### Decision Matrix

| Factor | Use 0.5B | Use 1.5B | Use 7B | Use 14B |
|--------|----------|----------|--------|---------|
| Speed critical | ✓ | ✓ | | |
| Simple task | ✓ | ✓ | | |
| Memory constrained | ✓ | | | |
| Tool calling | | ✓ | ✓ | |
| Complex reasoning | | | ✓ | ✓ |
| Code generation | | | ✓ | ✓ |
| Quality critical | | | | ✓ |

---

## 6. Memory Management & Model Unloading

### Ollama Memory Settings

**Environment variables:**
```bash
# Keep model in memory for X minutes after last use
OLLAMA_KEEP_ALIVE=5m

# Number of parallel requests (affects memory)
OLLAMA_NUM_PARALLEL=1

# Maximum loaded models
OLLAMA_MAX_LOADED_MODELS=1

# GPU layers to offload (0 = CPU only)
OLLAMA_GPU_OVERHEAD=0
```

### Recommended Configuration for 24GB RAM

```bash
# ~/.ollama/config or environment variables
OLLAMA_KEEP_ALIVE=2m          # Unload after 2 min idle
OLLAMA_NUM_PARALLEL=2         # Allow 2 concurrent requests
OLLAMA_MAX_LOADED_MODELS=2    # Keep 2 models loaded max
```

### Manual Model Management

```bash
# List running models
ollama ps

# Stop a specific model
ollama stop qwen2.5:14b

# Stop all models
ollama stop $(ollama ps -q)
```

### Memory Usage by Model

| Model + Quant | RAM Usage | VRAM (if GPU) |
|---------------|-----------|---------------|
| 0.5B Q4_K_M | ~0.6 GB | ~0.5 GB |
| 1.5B Q4_K_M | ~1.8 GB | ~1.4 GB |
| 7B Q4_K_M | ~6.0 GB | ~5.0 GB |
| 7B Q5_K_M | ~7.0 GB | ~6.0 GB |
| 14B Q4_K_M | ~11 GB | ~9.5 GB |
| 14B Q5_K_M | ~13 GB | ~11 GB |

**Note:** Add ~2GB overhead for Ollama itself and context buffer.

### Unloading Strategies

**Strategy 1: Time-based (default)**
- Pros: Simple, automatic
- Cons: May unload during pauses in conversation

**Strategy 2: Explicit control**
- Stop models immediately after use
- Pros: Predictable memory usage
- Cons: Slower response for next request

**Strategy 3: Priority-based**
- Keep small model always loaded
- Load large models on-demand
- Best for mixed workloads

---

## 7. Specific Recommendations for Our Setup

### Current Setup Analysis
- **RAM:** 24GB
- **OS:** Windows 11
- **Current models:** qwen2.5:14b (9GB), nomic-embed-text (0.3GB)
- **Issue:** Subagent cannot use Ollama due to sandbox isolation

### Recommended Model Portfolio

1. **qwen2.5:0.5b (Q4_K_M)** - 0.4GB
   - For ultra-fast tasks
   - Always keep loaded

2. **qwen2.5:1.5b (Q4_K_M)** - 1.2GB
   - For simple tool calling
   - Good middle ground

3. **qwen2.5:7b (Q5_K_M)** - 5.4GB
   - Primary daily driver
   - Best quality/speed balance

4. **qwen2.5:14b (Q4_K_M)** - 9.0GB
   - For complex tasks only
   - Load on-demand

### Memory Budget

| Scenario | Models Loaded | Total RAM | Available |
|----------|---------------|-----------|-----------|
| Minimal | 0.5B | ~1GB | ~22GB |
| Standard | 0.5B + 7B | ~7GB | ~16GB |
| Heavy | 0.5B + 14B | ~12GB | ~11GB |
| Maximum | 0.5B + 7B + 14B | ~16GB | ~7GB |

### Performance Targets

With proper optimization:
- **0.5B:** 50-100 tokens/sec (CPU), 200+ tokens/sec (GPU)
- **7B Q5_K_M:** 15-25 tokens/sec (CPU), 40-60 tokens/sec (GPU)
- **14B Q4_K_M:** 8-15 tokens/sec (CPU), 25-40 tokens/sec (GPU)

### Action Items

1. **Download recommended models:**
   ```bash
   ollama pull qwen2.5:0.5b
   ollama pull qwen2.5:1.5b
   ollama pull qwen2.5:7b
   # Keep 14b if needed for complex tasks
   ```

2. **Configure Ollama for better memory management:**
   ```powershell
   # Set environment variables in Windows
   [Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "2m", "User")
   [Environment]::SetEnvironmentVariable("OLLAMA_NUM_PARALLEL", "2", "User")
   ```

3. **Test GPU acceleration:**
   ```bash
   ollama run qwen2.5:7b
   # Check Task Manager for GPU usage
   ```

4. **Implement model routing in OpenClaw:**
   - Use 0.5B for heartbeats
   - Use 7B for interactive tasks
   - Use 14B only when explicitly needed

---

## 8. Additional Optimization Tips

### Context Length
- Default: 2048 tokens
- For long conversations: 4096 or 8192
- Longer context = more memory usage
- Recommendation: Keep at 2048 for most tasks

### Batch Size
- Ollama handles this automatically
- For llama.cpp: adjust `-b` parameter
- Larger batches = better throughput, higher latency

### Thread Settings (CPU only)
- Ollama auto-detects CPU cores
- For 24GB system with modern CPU: 8-16 threads optimal
- More threads ≠ always faster (diminishing returns)

### Disk Cache
- Ollama caches models in `~/.ollama/models/`
- Ensure SSD for faster model loading
- Models load from disk to RAM on first use

---

## Sources

1. llama.cpp quantization README: https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md
2. Qwen2.5 official blog: https://qwenlm.github.io/blog/qwen2.5/
3. Hugging Face quantization docs: https://huggingface.co/docs/transformers/quantization
4. Bartowski GGUF repositories (qwen2.5 variants)
5. llama.cpp feature matrix: https://github.com/ggml-org/llama.cpp/wiki/Feature-matrix
6. Ollama library: https://ollama.com/library/qwen2.5

---

## Summary

For a 24GB RAM Windows system, the optimal setup is:

1. **Use Q4_K_M quantization** as the default - best speed/quality tradeoff
2. **Keep 0.5B model loaded** for instant responses
3. **Use 7B Q5_K_M** as primary model for most tasks
4. **Load 14B only when needed** for complex reasoning
5. **Set OLLAMA_KEEP_ALIVE=2m** for aggressive unloading
6. **Use GPU if available** - 5-20x speedup for large models
7. **Consider Q5_K_M for 7B** if quality is priority over speed

This configuration provides fast responses for simple tasks while maintaining the ability to handle complex reasoning when needed, all within the 24GB RAM constraint.
