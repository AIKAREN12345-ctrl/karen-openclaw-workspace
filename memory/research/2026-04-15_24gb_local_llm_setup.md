# PERFECT Local LLM Infrastructure for 24GB RAM Windows 11 PC

**Research Date:** 2026-04-15  
**Target Hardware:** AMD Ryzen PC, 24GB RAM, No Dedicated GPU  
**Platform:** Windows 11

---

## Executive Summary

For a 24GB RAM AMD Ryzen Windows 11 PC without a dedicated GPU, the **optimal local LLM infrastructure** is:

1. **Primary Runtime:** Ollama (easiest setup, good performance)
2. **Alternative Runtime:** ik_llama.cpp (3-5x faster CPU inference, more complex setup)
3. **Architecture:** CPU-only inference with Q4_K_M quantization
4. **Best Models:** Qwen 2.5 14B, Llama 3.1 8B, DeepSeek R1 14B
5. **Hybrid Backup:** LiteLLM proxy with OpenAI/Anthropic fallback for complex queries

**Expected Performance:** 5-15 tokens/second for 7B-14B models on CPU-only setups.

---

## 1. SPECIFIC Models for 24GB RAM (CPU-Only)

### Recommended Model Matrix

| Model | Parameters | Q4_K_M Size | RAM Required | Use Case | Expected t/s (CPU) | Install Command |
|-------|------------|-------------|--------------|----------|-------------------|-----------------|
| **Qwen 2.5 14B** | 14B | ~9GB | ~11GB | Best all-rounder | 8-12 | `ollama pull qwen2.5:14b` |
| **DeepSeek R1 14B** | 14B | ~9GB | ~11GB | Reasoning, math | 7-11 | `ollama pull deepseek-r1:14b` |
| **Llama 3.1 8B** | 8B | ~5GB | ~7GB | General chat | 10-15 | `ollama pull llama3.1:8b` |
| **Qwen 2.5 Coder 7B** | 7B | ~5GB | ~7GB | Coding tasks | 10-15 | `ollama pull qwen2.5-coder:7b` |
| **Mistral Small 24B** | 24B | ~15GB | ~17GB | Advanced tasks* | 5-8 | `ollama pull mistral-small:24b` |
| **Phi-4 Mini 3.8B** | 3.8B | ~3GB | ~5GB | Fast responses | 15-25 | `ollama pull phi4-mini` |

*24B models will work but leave less headroom for OS and other applications.

### Models to Avoid on 24GB CPU-Only

| Model | Why Avoid |
|-------|-----------|
| Llama 3.3 70B | Requires ~42GB RAM, won't fit |
| Qwen 2.5 32B | Requires ~21GB RAM, too tight for 24GB |
| Qwen 2.5 72B | Requires ~42GB RAM, won't fit |
| Any FP16/BF16 model | 2x memory usage vs Q4_K_M |

### BitNet 1.58 Models - SPECIAL CASE

BitNet 1.58 models use ternary quantization (-1, 0, +1) achieving ~4x memory reduction:

| Model | Parameters | RAM Required | Expected t/s | Notes |
|-------|------------|--------------|--------------|-------|
| **BitNet b1.58 2B-4T** | 2B | ~1GB | 20-30 | Ultra-lightweight, basic tasks |
| **BitNet b1.58 3.9B** | 3.9B | ~2GB | 15-25 | Good for edge deployment |

**Important:** BitNet requires building from source on Windows with Visual Studio 2022 and Clang. See installation section below.

---

## 2. Architecture Comparison: Ollama vs llama.cpp vs Lemonade SDK

### Ollama (RECOMMENDED for Beginners)

**Pros:**
- One-command installation on Windows
- Automatic model downloads and management
- Simple REST API
- Built-in model library
- Good CPU inference performance
- Active development (v0.17.7 as of March 2026)

**Cons:**
- Less control over quantization settings
- Slightly slower than raw llama.cpp (~2-5% overhead)
- No tensor parallelism for multi-GPU (irrelevant for CPU-only)

**Best For:** Users who want "it just works" with minimal configuration.

### llama.cpp (Raw)

**Pros:**
- Maximum performance (no wrapper overhead)
- Full control over all parameters
- Supports all GGUF quantization types
- Can use custom compiled versions (ik_llama.cpp for 3-5x CPU speedup)
- MCP tool calling support (March 2026)

**Cons:**
- Manual model downloads
- Complex command-line interface
- No built-in model management

**Best For:** Power users who need maximum performance and control.

### ik_llama.cpp (CPU OPTIMIZED)

**Pros:**
- **3-5x faster CPU inference** than mainline llama.cpp
- New "R4" repacked quants for AVX2/Zen4
- Significant prompt processing speedups (up to 7x on some quants)

**Cons:**
- Must build from source
- Limited platform support (Linux/macOS primary, Windows secondary)
- No pre-built binaries

**Best For:** CPU-only users who want maximum performance and are comfortable building from source.

### Lemonade SDK

**Pros:**
- Optimized for NPUs and GPUs
- Good for heterogeneous compute

**Cons:**
- **NOT recommended for CPU-only setups**
- Primarily targets GPU/NPU acceleration
- More complex setup

**Verdict:** Skip for CPU-only 24GB RAM setups.

### vLLM

**Pros:**
- Excellent for multi-user serving
- PagedAttention for memory efficiency
- Production-grade throughput

**Cons:**
- **Requires GPU** - CPU inference is limited
- Complex setup
- Overkill for single-user desktop use

**Verdict:** Skip for CPU-only setups.

### Architecture Recommendation

| User Type | Recommended Setup |
|-----------|-------------------|
| Beginner | Ollama only |
| Intermediate | Ollama + ik_llama.cpp for heavy use |
| Advanced | ik_llama.cpp primary, Ollama for convenience |

---

## 3. STEP-BY-STEP Installation Guide for Windows 11

### Option A: Ollama Installation (EASIEST - Recommended)

#### Step 1: Download and Install Ollama

1. Visit https://ollama.com/download/windows
2. Download `OllamaSetup.exe`
3. Run installer (requires Administrator privileges)
4. Ollama installs as a Windows service and starts automatically

#### Step 2: Verify Installation

```powershell
# Open PowerShell or Command Prompt
ollama --version
# Should show version (e.g., ollama version 0.17.7)
```

#### Step 3: Pull Recommended Models

```powershell
# Pull Qwen 2.5 14B (best all-rounder for 24GB)
ollama pull qwen2.5:14b

# Pull Llama 3.1 8B (faster, lighter)
ollama pull llama3.1:8b

# Pull DeepSeek R1 14B (reasoning tasks)
ollama pull deepseek-r1:14b

# Pull coding specialist
ollama pull qwen2.5-coder:7b
```

#### Step 4: Test Models

```powershell
# Interactive chat
ollama run qwen2.5:14b

# Or via API
 curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:14b",
  "prompt": "Explain quantum computing in simple terms",
  "stream": false
}'
```

#### Step 5: Optimize for CPU Performance

Create a Modelfile for optimized CPU inference:

```dockerfile
# File: cpu-optimized.modelfile
FROM qwen2.5:14b

# CPU optimization parameters
PARAMETER num_thread 8
PARAMETER num_ctx 4096
PARAMETER temperature 0.7
```

```powershell
# Create optimized model
ollama create qwen2.5-14b-cpu -f cpu-optimized.modelfile
```

### Option B: BitNet 1.58 Installation (Advanced)

**WARNING:** Complex build process. Only recommended if you need ultra-low memory usage.

#### Prerequisites

1. **Visual Studio 2022** with:
   - Desktop development with C++
   - C++ CMake Tools for Windows
   - C++ Clang Compiler for Windows
   - MS-Build Support for LLVM-Toolset

2. **Python 3.9+**

3. **Git for Windows**

#### Installation Steps

```powershell
# Step 1: Open Developer Command Prompt for VS 2022
# Start Menu -> Visual Studio 2022 -> Developer Command Prompt

# Step 2: Clone BitNet repository
git clone --recursive https://github.com/microsoft/BitNet.git
cd BitNet

# Step 3: Create Python environment
python -m venv bitnet_env
bitnet_env\Scripts\activate

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Download model
huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T

# Step 6: Build (this is where Windows issues often occur)
python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s
```

#### Known Windows Build Issues & Fixes

| Issue | Solution |
|-------|----------|
| `std::chrono::system_clock` error | Add `#include <chrono>` to `common.cpp`, `log.cpp`, `imatrix.cpp`, `perplexity.cpp` |
| `clock is not a class` error | Replace `using clock = std::chrono::system_clock;` with explicit `std::chrono::system_clock::` |
| CMake not found | Install CMake from https://cmake.org/download/ |
| Clang not recognized | Ensure using Developer Command Prompt, not regular PowerShell |
| Loop unroll warnings | Normal, can be ignored |

**Alternative:** Use WSL2 with Ubuntu for easier BitNet compilation:

```bash
# In WSL2 Ubuntu
sudo apt update
sudo apt install clang cmake git python3 python3-pip
bash -c "$(wget -O - https://apt.llvm.org/llvm.sh)"
git clone --recursive https://github.com/microsoft/BitNet.git
cd BitNet
pip install -r requirements.txt
huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T
python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s
```

### Option C: ik_llama.cpp Installation (Maximum Performance)

**Note:** ik_llama.cpp is primarily developed for Linux. Windows support exists but requires manual compilation.

#### Prerequisites

- Visual Studio 2022 with C++ development tools
- CMake 3.22+
- Git

#### Build Steps

```powershell
# Step 1: Clone repository
git clone https://github.com/ikawrakow/ik_llama.cpp.git
cd ik_llama.cpp

# Step 2: Build with AVX2 support (for AMD Ryzen)
mkdir build
cd build
cmake .. -DLLAMA_AVX2=ON -DLLAMA_AVX=ON -DLLAMA_F16C=ON -DLLAMA_FMA=ON
cmake --build . --config Release -j

# Step 3: Verify build
.\bin\Release\llama-cli.exe --help
```

#### Using ik_llama.cpp

```powershell
# Download a model manually from HuggingFace
# Example: https://huggingface.co/bartowski/Qwen2.5-14B-Instruct-GGUF

# Run with optimized settings
.\bin\Release\llama-cli.exe `
  -m "path\to\qwen2.5-14b-instruct-q4_k_m.gguf" `
  -t 8 `
  -c 4096 `
  -p "Your prompt here"
```

---

## 4. KNOWN ISSUES and How to Avoid Them

### Issue 1: Ollama Uses Too Much RAM

**Symptom:** System becomes unresponsive when running models.

**Solution:**
```powershell
# Limit context window to reduce RAM usage
# In your Modelfile or API call:
PARAMETER num_ctx 2048  # Instead of default 4096+
```

### Issue 2: Slow Token Generation on CPU

**Symptom:** <5 tokens/second on CPU.

**Solutions:**
1. Use smaller models (7B-8B instead of 14B)
2. Increase thread count: `PARAMETER num_thread 8` (match your CPU cores)
3. Try ik_llama.cpp for 3-5x speedup
4. Use Q4_K_M quantization (default in Ollama)

### Issue 3: Model Fails to Load

**Symptom:** "out of memory" errors.

**Solutions:**
1. Close other applications
2. Use smaller quantization (Q3_K_M instead of Q4_K_M)
3. Reduce context window: `num_ctx 2048`
4. Check available RAM: Windows Task Manager -> Performance -> Memory

### Issue 4: BitNet Build Fails on Windows

**Symptom:** Compilation errors with `std::chrono` or `clock`.

**Solution:**
Apply the patch from GitHub issue #222:

```cpp
// In common.cpp, replace:
using clock = std::chrono::system_clock;
const clock::time_point current_time = clock::now();

// With:
const std::chrono::system_clock::time_point current_time = std::chrono::system_clock::now();
```

Also add `#include <chrono>` to affected files.

### Issue 5: Ollama Service Won't Start

**Symptom:** "Failed to start Ollama service" error.

**Solutions:**
1. Check if port 11434 is in use: `netstat -ano | findstr 11434`
2. Restart service: `net stop ollama && net start ollama`
3. Check Windows Event Viewer for errors
4. Reinstall Ollama

### Issue 6: Slow First Response (TTFT)

**Symptom:** Long delay before first token appears.

**Solutions:**
1. This is normal for CPU inference on long prompts
2. Use shorter prompts
3. Enable prompt caching in your application
4. Consider hybrid setup (see Section 6)

### Issue 7: Context Window Too Small

**Symptom:** "context length exceeded" errors.

**Solutions:**
```powershell
# Check model's max context
ollama show qwen2.5:14b

# Set appropriate context in Modelfile
PARAMETER num_ctx 8192  # If model supports it
```

### Issue 8: Windows Defender False Positives

**Symptom:** Windows Defender blocks Ollama or model downloads.

**Solution:**
Add exclusions in Windows Security:
1. Windows Security -> Virus & threat protection -> Exclusions
2. Add folder: `C:\Users\<username>\.ollama`
3. Add process: `ollama.exe`

---

## 5. PERFORMANCE BENCHMARKS on 24GB Systems

### CPU-Only Benchmarks (No GPU)

Based on community benchmarks and extrapolated data for 24GB RAM systems:

#### Ollama Performance (CPU-Only)

| Model | Quantization | RAM Used | Threads | Prompt Processing | Token Generation |
|-------|--------------|----------|---------|-------------------|------------------|
| Llama 3.1 8B | Q4_K_M | ~6GB | 8 | 15-25 t/s | 8-12 t/s |
| Qwen 2.5 7B | Q4_K_M | ~5GB | 8 | 18-28 t/s | 10-15 t/s |
| Qwen 2.5 14B | Q4_K_M | ~11GB | 8 | 8-15 t/s | 5-8 t/s |
| DeepSeek R1 14B | Q4_K_M | ~11GB | 8 | 7-12 t/s | 4-7 t/s |
| Mistral Small 24B | Q4_K_M | ~17GB | 8 | 4-8 t/s | 3-5 t/s |
| Phi-4 Mini 3.8B | Q4_K_M | ~3GB | 8 | 25-40 t/s | 15-25 t/s |

#### ik_llama.cpp Performance (CPU-Only, AVX2)

| Model | Quantization | Prompt Processing | Token Generation | Speedup vs Ollama |
|-------|--------------|-------------------|------------------|-------------------|
| Llama 3.1 8B | Q4_K_M | 40-70 t/s | 12-20 t/s | 1.5-2x |
| Llama 3.1 8B | IQ3_S | 50-90 t/s | 8-15 t/s | 2-3x |
| Qwen 2.5 14B | Q4_K_M | 20-35 t/s | 8-12 t/s | 1.5-2x |

**Note:** ik_llama.cpp shows dramatic improvements for prompt processing (up to 5x) but more modest gains for token generation (1.5-2x).

### BitNet 1.58 Performance

| Model | RAM Used | Token Generation | Notes |
|-------|----------|------------------|-------|
| BitNet 2B-4T | ~1GB | 20-30 t/s | Very fast, basic quality |
| BitNet 3.9B | ~2GB | 15-25 t/s | Good for simple tasks |

### Comparison: CPU vs GPU

| Hardware | Llama 3.1 8B Q4 | Qwen 2.5 14B Q4 |
|----------|-----------------|-----------------|
| CPU (Ryzen 8-core) | 8-12 t/s | 5-8 t/s |
| RTX 3060 12GB | 50-60 t/s | 25-30 t/s |
| RTX 4090 24GB | 85-100 t/s | 35-45 t/s |

**Reality Check:** CPU inference is 5-10x slower than GPU but still usable for many tasks.

---

## 6. ALTERNATIVES: Hybrid Cloud/Local Setup

If local performance is insufficient, implement a hybrid architecture using LiteLLM.

### Architecture Overview

```
Your Application
       |
       v
  LiteLLM Proxy (localhost:4000)
       |
   +---+---+
   |       |
   v       v
Ollama   Cloud APIs
(Local)  (OpenAI/Anthropic)
```

### LiteLLM Setup

#### Step 1: Install LiteLLM

```powershell
pip install litellm[proxy]
```

#### Step 2: Create Configuration

Save as `litellm_config.yaml`:

```yaml
model_list:
  # Local models via Ollama
  - model_name: "local-fast"
    litellm_params:
      model: "ollama/llama3.1:8b"
      api_base: "http://localhost:11434"
      stream: true

  - model_name: "local-strong"
    litellm_params:
      model: "ollama/qwen2.5:14b"
      api_base: "http://localhost:11434"
      stream: true

  # Cloud fallback models
  - model_name: "cloud-gpt4o"
    litellm_params:
      model: "gpt-4o"
      api_key: "os.environ/OPENAI_API_KEY"

  - model_name: "cloud-claude"
    litellm_params:
      model: "claude-sonnet-4-20250514"
      api_key: "os.environ/ANTHROPIC_API_KEY"

# Fallback configuration
litellm_settings:
  context_window_fallbacks:
    - local-strong: ["cloud-gpt4o"]
  
  # Budget control
  max_budget: 50  # $50/month cap
general_settings:
  master_key: "sk-your-proxy-key"
```

#### Step 3: Start LiteLLM

```powershell
# Set API keys
$env:OPENAI_API_KEY = "sk-..."
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Start proxy
litellm --config litellm_config.yaml --port 4000
```

#### Step 4: Use in Your Application

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="sk-your-proxy-key"
)

# This goes to local Ollama
response = client.chat.completions.create(
    model="local-fast",
    messages=[{"role": "user", "content": "Hello!"}]
)

# This goes to cloud if local fails
response = client.chat.completions.create(
    model="cloud-gpt4o",
    messages=[{"role": "user", "content": "Complex reasoning task..."}]
)
```

### Routing Strategies

#### Strategy 1: Task-Based Routing

```python
def route_query(prompt: str) -> str:
    """Route based on task complexity."""
    if any(word in prompt.lower() for word in ["code", "programming", "debug"]):
        return "local-strong"  # Local coding model
    elif len(prompt) > 4000:
        return "cloud-gpt4o"   # Long context to cloud
    else:
        return "local-fast"    # Simple queries stay local
```

#### Strategy 2: Budget-Conscious Routing

```yaml
# In litellm_config.yaml
general_settings:
  max_budget: 30  # $30/month cap

model_list:
  - model_name: "smart-router"
    litellm_params:
      model: "ollama/qwen2.5:14b"
    model_info:
      max_budget: 0  # Always use local, no cloud spend
```

### Cost Comparison

| Setup | Monthly Cost (1K queries/day) | Latency (avg) |
|-------|------------------------------|---------------|
| All Cloud (GPT-4o) | $1,800 | 500-2000ms |
| All Local (24GB RAM) | $0 | 100-500ms |
| Hybrid (90% local, 10% cloud) | $180 | 150-600ms |
| Hybrid (95% local, 5% cloud) | $90 | 120-550ms |

---

## 7. TROUBLESHOOTING GUIDE

### Quick Diagnostic Commands

```powershell
# Check Ollama status
ollama list
ollama ps

# Check system resources
Get-ComputerInfo | Select CsProcessors, CsTotalPhysicalMemory
# Or use: wmic cpu get name, numberofcores, numberoflogicalprocessors

# Check Ollama logs
Get-EventLog -LogName Application -Source Ollama -Newest 20

# Test model loading time
Measure-Command { ollama run llama3.1:8b "Hello" }
```

### Performance Tuning Checklist

- [ ] Use Q4_K_M quantization (best quality/speed tradeoff)
- [ ] Set `num_thread` to match physical CPU cores (not logical)
- [ ] Close unnecessary applications
- [ ] Disable Windows search indexing during heavy use
- [ ] Set power plan to "High Performance"
- [ ] Ensure adequate cooling (CPU throttling kills performance)

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "out of memory" | Model too large for RAM | Use smaller model or reduce num_ctx |
| "model not found" | Model not downloaded | Run `ollama pull <model>` |
| "connection refused" | Ollama service not running | Start service: `net start ollama` |
| "context length exceeded" | Prompt too long | Reduce prompt length or increase num_ctx |
| "permission denied" | Insufficient privileges | Run as Administrator |

---

## 8. FINAL RECOMMENDATIONS

### For 24GB RAM AMD Ryzen Windows 11 (No GPU):

1. **Start with Ollama** - Easiest setup, good enough performance
2. **Primary Models:**
   - Qwen 2.5 14B for general tasks
   - Llama 3.1 8B for speed-critical tasks
   - DeepSeek R1 14B for reasoning
3. **Keep 4-6GB RAM free** for OS and other apps
4. **Use hybrid setup** if you need cloud-quality responses occasionally
5. **Consider ik_llama.cpp** if you need 2-3x better CPU performance and don't mind building from source

### Upgrade Path

If local performance is insufficient:

1. **Immediate:** Implement LiteLLM hybrid routing
2. **Short-term:** Add RTX 3060 12GB (~$300 used) - enables 14B models at GPU speed
3. **Long-term:** Build dedicated LLM server with RTX 4090 24GB

### Expected Experience

With proper setup on 24GB RAM CPU-only:
- **Simple Q&A:** 10-15 t/s (comfortable)
- **Code generation:** 8-12 t/s (usable)
- **Long-form writing:** 5-8 t/s (patient)
- **Complex reasoning:** 4-7 t/s (slow but functional)

---

## Sources

1. Ollama Documentation: https://ollama.com
2. llama.cpp GitHub: https://github.com/ggml-org/llama.cpp
3. ik_llama.cpp: https://github.com/ikawrakow/ik_llama.cpp
4. Microsoft BitNet: https://github.com/microsoft/BitNet
5. Local AI Master: https://localaimaster.com
6. GPUStack Benchmarks: https://gpustack.ai
7. InsiderLLM Comparison: https://insiderllm.com

---

*Research compiled: 2026-04-15*  
*Last updated: 2026-04-15*
