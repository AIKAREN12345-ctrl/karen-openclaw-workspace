# Local LLM Systems Research: Optimal Setup for 24GB RAM Hardware

**Date:** 2026-03-23  
**Research Focus:** Local LLM deployment, quantization strategies, and hardware optimization for 24GB RAM systems

---

## Executive Summary

Running local LLMs on 24GB RAM hardware requires careful model selection, quantization strategies, and memory management. This research covers optimal configurations for Ollama, model comparisons across major families (Qwen, Llama, Mistral, Phi, DeepSeek), and actionable recommendations for maximizing performance on limited hardware.

---

## 1. Best Models for 24GB RAM

### Parameter Size Guidelines

With 24GB RAM, the following model sizes are feasible depending on quantization level:

| Model Size | Q4_K_M | Q5_K_M | Q8_0 | F16 |
|------------|--------|--------|------|-----|
| 7B | ~4.5GB | ~5.2GB | ~7.5GB | ~14GB |
| 8B | ~5.0GB | ~5.8GB | ~8.5GB | ~16GB |
| 14B | ~9.0GB | ~10.5GB | ~15GB | ~28GB* |
| 32B | ~20GB | ~23GB | ~34GB* | ~62GB* |
| 70B | ~43GB* | ~50GB* | ~72GB* | ~130GB* |

*Requires quantization to fit in 24GB RAM

### Recommended Models for 24GB RAM

**Optimal Choices:**
- **Qwen2.5-14B** (Q4_K_M or Q5_K_M) - Excellent multilingual support, 128K context, Apache 2.0 licensed
- **Llama 3.1-8B** (Q5_K_M or Q8_0) - Strong general performance, tool support, 128K context
- **Mistral-7B** (Q4_K_M or Q5_K_M) - Efficient, outperforms Llama 2 13B
- **Phi-4-14B** (Q4_K_M) - Strong reasoning, 16K context, memory-efficient
- **DeepSeek-R1-14B** (Q4_K_M) - Excellent reasoning capabilities, distilled variant

**Maximum Size:**
- **Qwen2.5-32B** (Q4_K_M at ~20GB) - Pushing limits but feasible with minimal context
- **DeepSeek-R1-32B** (Q4_K_M) - Advanced reasoning, requires careful memory management

---

## 2. Optimal Ollama Configuration for 24GB RAM

### Environment Variables

```bash
# Set maximum memory for model loading
export OLLAMA_MAX_LOADED_MODELS=1

# Limit context window to conserve memory (adjust based on model)
export OLLAMA_CONTEXT_LENGTH=8192

# Enable GPU layers if available (set to 0 for CPU-only)
export OLLAMA_GPU_LAYERS=0

# Configure number of threads (match physical CPU cores)
export OLLAMA_NUM_THREADS=8
```

### Modelfile Optimizations

Create a custom Modelfile for memory-efficient inference:

```dockerfile
FROM qwen2.5:14b

# Reduce context window to save memory
PARAMETER num_ctx 8192

# Adjust temperature for consistent outputs
PARAMETER temperature 0.7

# Limit GPU layers (0 for CPU-only systems)
PARAMETER num_gpu 0

# Set appropriate thread count
PARAMETER num_thread 8

# System prompt
SYSTEM """You are a helpful AI assistant optimized for local deployment."""
```

### Ollama Serve Configuration

```bash
# Start Ollama with memory constraints
ollama serve --max-loaded-models 1 --max-queue 2
```

---

## 3. Model Comparison: Qwen, Llama, Mistral, Phi, DeepSeek

### Qwen2.5 Family (Alibaba)

**Sizes:** 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B

**Strengths:**
- Pretrained on 18 trillion tokens
- 128K token context window
- Multilingual support (29+ languages)
- Excellent coding capabilities (HumanEval 85+)
- Strong math reasoning (MATH 80+)
- Apache 2.0 license (except 3B and 72B)

**Best for:** Multilingual applications, coding tasks, long-context processing

**24GB Recommendation:** Qwen2.5-14B (Q5_K_M) or Qwen2.5-32B (Q4_K_M)

### Llama 3.1 Family (Meta)

**Sizes:** 8B, 70B, 405B

**Strengths:**
- State-of-the-art general knowledge
- 128K context length
- Tool use capabilities
- Multilingual support
- Permissive license allowing output distillation

**Best for:** General-purpose applications, tool use, long-form text summarization

**24GB Recommendation:** Llama 3.1-8B (Q8_0 for best quality, Q5_K_M for balance)

### Mistral Family (Mistral AI)

**Sizes:** 7B, 8x7B (MoE), 8x22B (MoE), Small (22B), Large (123B)

**Strengths:**
- Exceptional efficiency (7B outperforms Llama 2 13B)
- Function calling support (v0.3)
- Apache 2.0 license
- Strong code performance relative to size

**Best for:** Resource-constrained environments, function calling, coding

**24GB Recommendation:** Mistral-7B (Q5_K_M) or Mistral-Small-22B (Q4_K_M)

### Phi Family (Microsoft)

**Sizes:** 3.8B (Phi-3/3.5), 14B (Phi-4)

**Strengths:**
- Remarkable performance for size (Phi-3.5 rivals larger models)
- Strong reasoning and logic
- Memory/compute efficient
- 16K context (Phi-4)

**Best for:** Edge deployment, reasoning tasks, memory-constrained scenarios

**24GB Recommendation:** Phi-4-14B (Q4_K_M) - excellent reasoning within RAM limits

### DeepSeek Family (DeepSeek AI)

**Sizes:** 1.5B, 7B, 8B, 14B, 32B, 70B, 671B (R1)

**Strengths:**
- Advanced reasoning capabilities (approaching O3, Gemini 2.5 Pro)
- Distilled variants available
- MIT License (commercial use allowed)
- Strong math and code performance

**Best for:** Complex reasoning, mathematical tasks, coding challenges

**24GB Recommendation:** DeepSeek-R1-14B or DeepSeek-R1-32B (Q4_K_M)

---

## 4. Context Length vs RAM Usage Tradeoffs

### Memory Calculation Formula

```
Total Memory = Model Weights + KV Cache + Overhead

KV Cache = 2 × num_layers × num_heads × head_dim × context_length × bytes_per_param
```

### Context Length Recommendations

| Model Size | Max Context | RAM at Max | Recommended Context | RAM Used |
|------------|-------------|------------|---------------------|----------|
| 7B Q4_K_M | 128K | ~18GB | 32K | ~8GB |
| 14B Q4_K_M | 128K | ~28GB* | 16K | ~12GB |
| 32B Q4_K_M | 128K | ~52GB* | 8K | ~22GB |

*Exceeds 24GB RAM - requires context reduction

### Practical Guidelines

- **For 7B models:** Use up to 32K-64K context comfortably
- **For 14B models:** Limit to 8K-16K context for safe operation
- **For 32B models:** Restrict to 4K-8K context maximum
- **Always monitor:** Use `htop` or Task Manager to track actual RAM usage

---

## 5. Quantization Strategies (Q4_K_M, Q5_K_M, Q8_0)

### Quantization Types Explained

**Q4_K_M (4-bit K-quant medium):**
- Bits per weight: ~4.5
- Quality: Good balance of size vs performance
- Speed: Fast inference
- Use case: General deployment, 24GB RAM constraints

**Q5_K_M (5-bit K-quant medium):**
- Bits per weight: ~5.5
- Quality: Better than Q4, minimal quality loss
- Speed: Slightly slower than Q4
- Use case: When quality matters more than size

**Q8_0 (8-bit legacy):**
- Bits per weight: 8.0
- Quality: Near-FP16 quality
- Speed: Fastest quantized inference
- Use case: Smaller models (7B-8B) where quality is critical

### GGUF Quantization Hierarchy

From smallest/worst to largest/best:
```
Q2_K < Q3_K_S < Q3_K_M < Q3_K_L < Q4_0 < Q4_K_S < Q4_K_M < Q5_0 < Q5_K_S < Q5_K_M < Q6_K < Q8_0 < F16
```

### Recommendations by Model Size

| Model Size | Recommended Quant | File Size | Quality |
|------------|-------------------|-----------|---------|
| 7B | Q5_K_M or Q8_0 | 5-7GB | Excellent |
| 14B | Q4_K_M or Q5_K_M | 9-11GB | Very Good |
| 32B | Q4_K_M | ~20GB | Good |
| 70B | Q4_K_M (partial offload) | ~43GB | Requires GPU offload |

---

## 6. Concurrent Model Loading Strategies

### Single Model Strategy (Recommended for 24GB)

Given 24GB RAM constraints, the safest approach is loading **one model at a time**:

```bash
# Unload current model before loading new one
ollama rm model_name

# Or use Modelfile with explicit memory limits
```

### Multi-Model Strategy (Advanced)

If running multiple smaller models:

```bash
# Example: Two 7B models at Q4_K_M
# Total: ~9GB (fits comfortably)

# Model 1: General chat
ollama run llama3.1:8b-q4_K_M

# Model 2: Coding (after unloading first)
ollama run qwen2.5-coder:7b-q4_K_M
```

### Memory Management Tips

1. **Unload unused models:**
   ```bash
   ollama stop model_name
   ```

2. **Monitor memory:**
   ```bash
   # Linux/Mac
   free -h
   
   # Windows
   tasklist | findstr ollama
   ```

3. **Use smaller models for concurrent loading:**
   - 3B models: Can load 3-4 concurrently
   - 7B models: Can load 2 concurrently
   - 14B+ models: Single model only

---

## 7. Memory Management Tips for Local LLMs

### System-Level Optimizations

**Linux:**
```bash
# Increase swap space for overflow
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Optimize swappiness
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

**Windows:**
- Set virtual memory to 1.5x-2x physical RAM
- Close unnecessary applications
- Disable Windows Search indexing during inference

### Ollama-Specific Tips

1. **Limit loaded models:**
   ```bash
   export OLLAMA_MAX_LOADED_MODELS=1
   ```

2. **Reduce context aggressively:**
   ```bash
   PARAMETER num_ctx 4096  # Instead of 128K
   ```

3. **Use CPU offloading strategically:**
   ```bash
   PARAMETER num_gpu 0  # Force CPU-only if GPU VRAM is limited
   ```

### Monitoring Tools

```bash
# Real-time memory monitoring
watch -n 1 free -h

# Ollama process monitoring
ps aux | grep ollama

# Disk usage (models are cached)
du -sh ~/.ollama/models/
```

---

## 8. CPU vs GPU Acceleration on Limited Hardware

### CPU-Only Deployment

**Advantages:**
- No GPU VRAM constraints
- Works on any hardware
- Lower power consumption
- No driver dependencies

**Disadvantages:**
- Slower inference (5-20x slower than GPU)
- Higher latency for token generation

**Optimization:**
```bash
# Build llama.cpp with BLAS support
cmake -B build -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS
cmake --build build --config Release

# Set thread count to physical cores
export OMP_NUM_THREADS=8
```

### GPU Acceleration (If Available)

**For NVIDIA GPUs:**
```bash
# Build with CUDA
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release

# Offload layers to GPU
ollama run model --gpu-layers 35
```

**For AMD GPUs:**
```bash
# Build with ROCm/HIP
cmake -B build -DGGML_HIP=ON -DGPU_TARGETS=gfx1030
cmake --build build --config Release
```

**Layer Offloading Strategy:**
- Full offload: All layers on GPU (fastest, requires VRAM > model size)
- Partial offload: Balance between GPU VRAM and system RAM
- CPU-only: No GPU layers (slowest, most compatible)

### 24GB RAM + Limited VRAM Scenario

Common configuration: 24GB RAM + 4-8GB VRAM

**Strategy:**
1. Load model weights in system RAM (24GB)
2. Offload 10-20 layers to GPU VRAM (4-8GB)
3. Process remaining layers on CPU

```bash
# Example: 14B model with partial GPU offload
ollama run qwen2.5:14b --gpu-layers 20
```

---

## 9. Best Use Cases for Each Model Type

### General Chat & Assistant Tasks

**Best Models:**
- Llama 3.1-8B (Q8_0) - Most capable generalist
- Qwen2.5-14B (Q5_K_M) - Multilingual, long context
- Mistral-7B (Q5_K_M) - Efficient, fast

**Use when:** You need a versatile assistant for everyday tasks

### Coding & Development

**Best Models:**
- Qwen2.5-Coder-14B - Specialized for code
- DeepSeek-R1-14B - Strong reasoning for complex code
- CodeLlama-13B - Established code model

**Use when:** Code generation, debugging, explanation

### Reasoning & Mathematics

**Best Models:**
- DeepSeek-R1-14B/32B - Advanced reasoning
- Qwen2.5-Math-7B - Specialized math model
- Phi-4-14B - Strong logic and reasoning

**Use when:** Mathematical problems, logical reasoning, step-by-step thinking

### Multilingual Applications

**Best Models:**
- Qwen2.5-14B (29+ languages)
- Llama 3.1-8B (multilingual)
- Aya-8B (23 languages)

**Use when:** Non-English content, translation, multilingual chat

### Memory-Constrained Edge Deployment

**Best Models:**
- Phi-3.5-3.8B - Remarkable quality for size
- Qwen2.5-3B - Efficient small model
- Llama 3.2-3B - Meta's compact model

**Use when:** Running multiple models, very limited RAM, edge devices

### Long Context Processing

**Best Models:**
- Qwen2.5-14B (128K context, reduce for 24GB)
- Llama 3.1-8B (128K context)
- Mistral-Nemo-12B (128K context)

**Use when:** Document analysis, long conversations, RAG applications

---

## 10. Future-Proofing: What to Watch For

### Emerging Trends

1. **Mixture of Experts (MoE) Models**
   - DeepSeek-V2/V3, Qwen3-MoE
   - More parameters, same inference cost
   - Watch for: Efficient MoE inference on consumer hardware

2. **Improved Quantization**
   - IQ (Importance Matrix) quantization
   - 1-2 bit quantization with acceptable quality
   - Watch for: GGUF format updates, new quantization types

3. **Long Context Optimization**
   - Ring attention, sliding window attention
   - Infinite context techniques
   - Watch for: Reduced memory scaling for long contexts

4. **Multi-Modal Models**
   - LLaVA, Qwen-VL, Gemma Vision
   - Vision + language in one model
   - Watch for: Efficient vision encoder quantization

### Hardware Considerations

**Upgrade Path:**
- **Priority 1:** More GPU VRAM (enables larger models)
- **Priority 2:** Faster CPU (improves CPU-only inference)
- **Priority 3:** More system RAM (enables concurrent models)

**Technology to Watch:**
- Unified Memory (Apple Silicon, Intel Meteor Lake)
- CXL memory expansion
- NPU acceleration (Intel, AMD, Qualcomm)

### Software Developments

**Key Projects:**
- llama.cpp: Continuous optimization, new backends
- Ollama: Simplified deployment, model management
- vLLM: High-throughput serving
- MLC LLM: Universal deployment

**Features to Enable:**
- Flash Attention 2 (memory-efficient attention)
- Continuous batching (throughput optimization)
- Speculative decoding (latency reduction)

---

## Specific Recommendations for 24GB RAM

### Tier 1: Best Overall Experience

**Single Model Setup:**
- Qwen2.5-14B (Q5_K_M) - ~10.5GB
- Context: 16K tokens
- Use case: General assistant with multilingual support

**Alternative:**
- Llama 3.1-8B (Q8_0) - ~8GB
- Context: 32K tokens
- Use case: Maximum quality for smaller model

### Tier 2: Maximum Capability

**Pushing the Limits:**
- Qwen2.5-32B (Q4_K_M) - ~20GB
- Context: 4K-8K tokens
- Use case: When you need the most capable model possible

**Reasoning Focus:**
- DeepSeek-R1-32B (Q4_K_M) - ~23GB
- Context: 4K tokens
- Use case: Complex reasoning, math, coding challenges

### Tier 3: Concurrent/Flexible Setup

**Multiple Smaller Models:**
- Mistral-7B (Q4_K_M) - ~4.5GB
- Phi-4-14B (Q4_K_M) - ~9GB
- Qwen2.5-Coder-7B (Q4_K_M) - ~4.5GB
- Total: ~18GB (allows switching without reloading)

### Configuration Template

```dockerfile
# Modelfile for 24GB RAM optimization
FROM qwen2.5:14b-q5_K_M

# Conservative context for safety
PARAMETER num_ctx 16384

# CPU optimization
PARAMETER num_thread 8
PARAMETER num_gpu 0

# Generation parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1

SYSTEM """You are a helpful AI assistant running on optimized local hardware."""
```

---

## Conclusion

24GB RAM is a sweet spot for local LLM deployment, enabling:
- High-quality 14B models (Q5_K_M quantization)
- Maximum capability 32B models (Q4_K_M quantization)
- Multiple smaller models for different tasks

**Key Takeaways:**
1. Use Q5_K_M for 7B-14B models (best quality/size ratio)
2. Use Q4_K_M for 32B models (necessary for fitting in RAM)
3. Limit context length to 8K-16K for larger models
4. Monitor memory usage and adjust accordingly
5. Consider CPU-only deployment for maximum compatibility

**Recommended Starting Point:**
```bash
ollama run qwen2.5:14b-q5_K_M
```

This provides an excellent balance of capability, quality, and memory efficiency for 24GB RAM systems.

---

## References

- Ollama Library: https://ollama.com/library
- Qwen2.5 Documentation: https://qwenlm.github.io/blog/qwen2.5/
- Hugging Face Quantization: https://huggingface.co/docs/transformers/quantization
- GGUF Format: https://huggingface.co/docs/hub/gguf
- llama.cpp Build Guide: https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
- r/LocalLLaMA Wiki: https://www.reddit.com/r/LocalLLaMA/wiki/index

---

*Research compiled from official documentation, community resources, and technical specifications.*
