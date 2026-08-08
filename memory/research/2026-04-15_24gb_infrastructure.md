# Comprehensive Local LLM Infrastructure Guide
## 24GB RAM Windows 11 PC (AMD Ryzen, No GPU)

**Research Date:** 2026-04-15  
**Target System:** Windows 11, AMD Ryzen CPU, 24GB RAM, No Dedicated GPU  
**Document Version:** 1.0

---

## Table of Contents

1. [System Limitations](#1-system-limitations)
2. [Architecture Comparison](#2-architecture-comparison)
3. [Perfect Setup Guide](#3-perfect-setup-guide)
4. [Known Issues & Fixes](#4-known-issues--fixes)
5. [Performance Expectations](#5-performance-expectations)

---

## 1. SYSTEM LIMITATIONS

### 1.1 Exact RAM Usage Breakdown

| Component | Memory Usage | Notes |
|-----------|--------------|-------|
| **Windows 11 Base OS** | 4-6 GB | Idle system with essential services |
| **Windows Defender/Security** | 0.5-1 GB | Real-time protection active |
| **System Cache/Buffers** | 2-3 GB | File cache, standby memory |
| **Background Apps** | 1-2 GB | Browser tabs, utilities, etc. |
| **Available for LLMs** | **12-16 GB** | Usable memory for model inference |

**Critical Insight:** With 24GB total RAM, you realistically have **12-16GB available** for LLM inference. This limits you to:
- Q4_K_M quantized 7B models (~4-5GB)
- Q4_K_M quantized 14B models (~8-9GB) 
- Q4_K_M quantized 30B models (~18-20GB) - marginal, may swap

### 1.2 CPU-Only Inference Limitations vs GPU

| Aspect | CPU-Only (Your Setup) | GPU-Accelerated |
|--------|----------------------|-----------------|
| **Inference Speed** | 5-15 tokens/sec | 20-65+ tokens/sec |
| **Memory Bandwidth** | DDR4/DDR5 limited | GDDR6X/GDDR7 - 5-10x faster |
| **Parallel Processing** | AVX2/AVX-512 SIMD | Thousands of CUDA cores |
| **Model Size Limit** | RAM-constrained | VRAM-constrained |
| **Power Consumption** | 65-125W (CPU) | 150-450W (GPU+CPU) |
| **Latency** | Higher (30-100ms TTFT) | Lower (10-30ms TTFT) |

**Key Limitations:**
- **No CUDA acceleration** - Cannot use NVIDIA GPU optimizations
- **No Metal acceleration** - Cannot use Apple Silicon unified memory benefits
- **AVX2/AVX-512 dependent** - Performance varies by Ryzen generation
- **Memory bandwidth bottleneck** - CPU RAM is 5-10x slower than GPU VRAM

### 1.3 Windows 11 Specific Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| **Windows Defender Real-time Scanning** | 10-20% performance hit | Add model directories to exclusions |
| **Windows Update Background Activity** | Periodic CPU/disk usage | Set "Active Hours" appropriately |
| **Memory Compression** | Adds 5-10% overhead | Disable if RAM is tight |
| **WSL2 Memory Reservation** | Reserves 50% RAM by default | Configure `.wslconfig` file |
| **System Restore Points** | Disk space usage | Monitor and clean regularly |
| **Page File Management** | Can cause stuttering | Set fixed page file size |

**Windows 11 Pro Tips:**
- Disable "Game Mode" - it can interfere with background inference
- Set power plan to "High Performance" for consistent CPU clocks
- Disable "Focus Assist" notifications during long inference sessions

---

## 2. ARCHITECTURE COMPARISON

### 2.1 Ollama vs llama.cpp vs Lemonade SDK

| Feature | Ollama | llama.cpp | Lemonade SDK |
|---------|--------|-----------|--------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Windows Support** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **CPU Optimization** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Model Management** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **API Compatibility** | OpenAI-compatible | OpenAI-compatible | Custom |
| **Community Size** | Large | Very Large | Small |
| **Documentation** | Excellent | Good | Moderate |

### 2.2 Which Works Best for 24GB CPU-Only Setup

**RECOMMENDATION: Ollama (Primary) + llama.cpp (Advanced)**

**Why Ollama for 24GB CPU-Only:**
1. **Automatic CPU Optimization** - Detects AVX2/AVX-512 automatically
2. **Simplified Model Management** - One-command model downloads
3. **Built-in Quantization** - Automatically serves Q4_K_M optimized models
4. **CPU Thread Management** - Auto-configures based on physical cores
5. **Windows Native Support** - First-class Windows support since late 2024

**When to use llama.cpp:**
- Maximum performance tuning needed
- Custom quantization experiments
- Research/benchmarking scenarios
- Specific KV cache optimizations (TurboQuant)

**Lemonade SDK Considerations:**
- Good for enterprise deployments
- Requires more setup on Windows
- Smaller community for troubleshooting

### 2.3 Installation Complexity Comparison

| Tool | Installation Time | Complexity | Prerequisites |
|------|------------------|------------|---------------|
| **Ollama** | 5 minutes | Very Low | Windows 10/11, 8GB+ RAM |
| **llama.cpp** | 15-30 minutes | Medium | CMake, Visual Studio Build Tools, Python |
| **Lemonade SDK** | 20-40 minutes | Medium-High | Python 3.9+, specific dependencies |

---

## 3. PERFECT SETUP GUIDE

### 3.1 Step-by-Step Windows 11 Installation

#### Phase 1: System Preparation (5 minutes)

```powershell
# 1. Check Windows version (must be 1903 or higher)
winver

# 2. Verify system architecture
wmic os get osarchitecture
# Should return "64-bit"

# 3. Check available RAM
systeminfo | findstr "Total Physical Memory"

# 4. Check available storage
Get-PSDrive C | Select-Object Used,Free

# 5. Set power plan to High Performance
powercfg /setactive SCHEME_MIN
```

#### Phase 2: Windows Optimization (10 minutes)

```powershell
# 1. Add Windows Defender exclusions for model directories
# GUI: Windows Security → Virus & threat protection → Exclusions
# Add these paths:
# - C:\Program Files\Ollama
# - C:\Users\%USERNAME%\.ollama
# - C:\Users\%USERNAME%\llama-models (create this folder)

# 2. Disable Windows Search indexing for model directories
# Control Panel → Indexing Options → Modify → Uncheck model folders

# 3. Configure page file (optional but recommended)
# System Properties → Advanced → Performance Settings → Advanced → Virtual Memory
# Set custom size: Initial 4096 MB, Maximum 8192 MB on SSD
```

#### Phase 3: Ollama Installation (5 minutes)

**Method A: Official Installer (Recommended)**

1. Download from https://ollama.com/download/windows
2. Run `OllamaSetup.exe` as Administrator
3. Accept license agreement
4. Choose installation directory (default: `C:\Program Files\Ollama`)
5. **IMPORTANT:** Check "Add to PATH"
6. Complete installation

**Method B: Windows Package Manager**

```powershell
# Install via winget
winget install Ollama.Ollama

# Verify installation
ollama --version
# Should display: ollama version 0.6.x or higher
```

#### Phase 4: Post-Installation Configuration

```powershell
# 1. Configure Ollama for CPU-only mode
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_GPU", "0", "User")

# 2. Set CPU threads to physical core count (not logical)
# For Ryzen 5/7: usually 6-8 physical cores
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS", "8", "User")

# 3. Configure model storage location (optional)
# Move to larger drive if C: is small
$newPath = "D:\OllamaModels"
New-Item -ItemType Directory -Path $newPath -Force
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $newPath, "User")

# 4. Set context window (balance memory vs capability)
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "8192", "User")

# 5. Restart Ollama service
# Right-click Ollama tray icon → Quit
# Then restart Ollama application
```

### 3.2 Model Download and Configuration

#### Recommended Models for 24GB CPU-Only

| Model | Size | RAM Required | Tokens/sec* | Best For |
|-------|------|--------------|-------------|----------|
| **phi4:mini** | 2.4GB | 4GB | 8-12 | General chat, coding |
| **gemma3:1b** | 815MB | 2GB | 10-15 | Fast responses, simple tasks |
| **qwen2.5:7b** | 4.7GB | 6GB | 6-10 | Coding, reasoning |
| **mistral:7b** | 4.1GB | 6GB | 6-10 | General purpose |
| **llama3.2:8b** | 4.7GB | 6GB | 5-9 | Versatile, well-tested |
| **qwen2.5:14b** | 9.0GB | 12GB | 4-7 | Better reasoning |
| **deepseek-r1:7b** | 4.7GB | 6GB | 5-8 | Math, reasoning |

*Estimated on Ryzen 7-class CPU with AVX2

#### Model Download Commands

```powershell
# Download models (run one at a time, they're large)

# 1. Start with small model for testing
ollama pull gemma3:1b

# 2. Good all-rounder for coding
ollama pull qwen2.5:7b

# 3. Reasoning specialist
ollama pull deepseek-r1:7b

# 4. Larger model if RAM permits
ollama pull qwen2.5:14b

# List downloaded models
ollama list
```

#### Testing Your Setup

```powershell
# Test basic functionality
ollama run gemma3:1b "Hello, are you working?"

# Test with verbose output to verify CPU mode
ollama run qwen2.5:7b --verbose "Explain quantum computing in simple terms"
# Look for "num_gpu_layers=0" in output to confirm CPU-only

# Check running models and memory usage
ollama ps
```

#### Creating Custom Model Configurations

Create a file named `Modelfile`:

```dockerfile
FROM qwen2.5:7b

# System prompt
SYSTEM """You are a helpful, accurate, and efficient AI assistant optimized for CPU inference. 
Provide concise but complete answers."""

# Parameters for CPU optimization
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096
PARAMETER num_thread 8
PARAMETER num_gpu_layers 0
PARAMETER repeat_penalty 1.1
```

Build and run:

```powershell
# Create custom model
ollama create cpu-optimized -f Modelfile

# Run it
ollama run cpu-optimized
```

### 3.3 BitNet 1.58 Setup

**What is BitNet:** Microsoft's 1-bit LLM architecture using ternary weights (-1, 0, +1) achieving ~35x memory reduction vs FP16.

**Prerequisites:**
- Python 3.9+
- CMake 3.22+
- Clang 18+ (Windows requires Visual Studio 2022 with ClangCL)
- Conda (recommended)

#### Installation Steps

```powershell
# 1. Install Visual Studio 2022 with ClangCL workload
# Download from: https://visualstudio.microsoft.com/downloads/
# Required components: Desktop development with C++, ClangCL

# 2. Install Python 3.9+ and Conda
# Download Anaconda or Miniconda

# 3. Open "x64 Native Tools Command Prompt for VS 2022"
# Run as Administrator

# 4. Clone BitNet repository
git clone --recursive https://github.com/microsoft/BitNet.git
cd BitNet

# 5. Create Conda environment
conda create -n bitnet-cpp python=3.9
conda activate bitnet-cpp
pip install -r requirements.txt

# 6. Set up Visual Studio environment
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

# 7. Download a BitNet model
huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T

# 8. Build and quantize
python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s

# 9. Run inference
python run_inference.py -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf -p "You are a helpful assistant" -cnv
```

**Available BitNet Models:**
- `microsoft/BitNet-b1.58-2B-4T` (recommended for beginners) - ~400MB
- `HF1BitLLM/Llama3-8B-1.58-100B-tokens` - ~2GB
- `tiiuae/Falcon3-1B-Instruct-1.58bit` - ~300MB

**Windows-Specific Notes:**
- Clang must be installed via Visual Studio Installer
- Use Developer Command Prompt, not regular PowerShell
- If build fails, verify LLVM/Clang is in PATH

### 3.4 TurboQuant Integration

**What is TurboQuant:** Google's KV cache compression algorithm achieving 3.8-6.4x compression with minimal quality loss.

**Status for Windows CPU:** TurboQuant is primarily implemented for GPU backends (Metal, CUDA, HIP). CPU support is limited but emerging.

#### Option A: llama.cpp with TurboQuant (Experimental)

```powershell
# 1. Clone the TurboQuant fork
git clone https://github.com/TheTom/llama-cpp-turboquant.git
cd llama-cpp-turboquant
git checkout feature/turboquant-kv-cache

# 2. Build with CPU support (no GPU)
cmake -B build -DCMAKE_BUILD_TYPE=Release -DLLAMA_NATIVE=ON
cmake --build build --config Release -j

# 3. Verify turbo types are available
.\build\bin\llama-server --help | findstr turbo

# 4. Run with TurboQuant KV cache
.\build\bin\llama-server `
  -m models\your-model.gguf `
  --cache-type-k turbo3 `
  --cache-type-v turbo3 `
  -c 8192 `
  -t 8
```

**Cache Type Options:**
- `turbo2`: 2.5 bits, 6.4x compression (extreme memory pressure)
- `turbo3`: 3.5 bits, 4.6x compression (recommended)
- `turbo4`: 4.25 bits, 3.8x compression (best quality)

#### Option B: Asymmetric K/V (Recommended for Q4_K_M Models)

```powershell
# For models with Q4_K_M weights, use asymmetric config
# Keep K at q8_0 precision, compress V with turbo

.\build\bin\llama-server `
  -m models\qwen2.5-7b-q4_k_m.gguf `
  --cache-type-k q8_0 `
  --cache-type-v turbo4 `
  -c 8192 `
  -t 8
```

**Important:** TurboQuant on CPU is experimental. For production use on CPU-only systems, stick with standard Ollama or llama.cpp without TurboQuant until CPU optimizations mature.

---

## 4. KNOWN ISSUES & FIXES

### 4.1 Common Failures on 24GB Systems

#### Issue 1: Out of Memory (OOM) Errors

**Symptoms:**
```
Error: model allocation failed
Error: out of memory
Model fails to load or crashes during inference
```

**Root Causes:**
- Model + KV cache exceeds available RAM
- Windows background processes consuming memory
- Page file too small or on slow HDD

**Solutions:**

```powershell
# 1. Use smaller models or more aggressive quantization
ollama pull qwen2.5:7b        # Instead of 14b
ollama pull gemma3:1b         # For tight memory

# 2. Reduce context window
ollama run qwen2.5:7b --num-ctx 2048

# 3. Close background applications
Get-Process | Where-Object {$_.WorkingSet -gt 500MB} | Stop-Process

# 4. Increase page file size
# System Properties → Advanced → Performance → Virtual Memory
# Set to 8192-16384 MB on SSD

# 5. Monitor memory during load
# Open Task Manager → Performance → Memory while loading model
```

#### Issue 2: Slow Model Loading (2+ minutes)

**Symptoms:**
- Model takes excessive time to load
- Disk activity at 100% during load

**Solutions:**

```powershell
# 1. Ensure models are on SSD, not HDD
# Check drive type in Task Manager → Performance

# 2. Add model directory to Windows Defender exclusions
# Windows Security → Virus & threat protection → Exclusions

# 3. Disable Windows Search indexing for model folder
# Indexing Options → Modify

# 4. Pre-load model into memory (if RAM permits)
ollama run model_name &
# Then use API calls - model stays loaded
```

#### Issue 3: CPU Throttling / Thermal Issues

**Symptoms:**
- Initial fast inference, then slows down
- High CPU temperatures (90°C+)
- Fan noise increases dramatically

**Solutions:**

```powershell
# 1. Reduce thread count to reduce heat
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS", "4", "User")

# 2. Use CPU affinity to limit cores
# Task Manager → Details → ollama.exe → Set Affinity

# 3. Ensure adequate cooling
# Clean dust from CPU cooler
# Reapply thermal paste if old

# 4. Consider undervolting (advanced)
# Use Ryzen Master or BIOS settings
```

### 4.2 Windows-Specific Problems

#### Issue 4: "ollama is not recognized" Error

**Solution:**

```powershell
# 1. Manually add to PATH
$ollamaPath = "C:\Program Files\Ollama"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$ollamaPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$ollamaPath", "User")
}

# 2. Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 3. Open NEW PowerShell window (old window won't see changes)
```

#### Issue 5: Windows Defender Blocking Ollama

**Solution:**

```powershell
# Run as Administrator

# Add exclusions
Add-MpPreference -ExclusionPath "C:\Program Files\Ollama"
Add-MpPreference -ExclusionPath "$env:USERPROFILE\.ollama"
Add-MpPreference -ExclusionProcess "ollama.exe"

# Verify exclusions
Get-MpPreference | Select-Object -Property ExclusionPath, ExclusionProcess
```

#### Issue 6: Port 11434 Already in Use

**Solution:**

```powershell
# Find process using port
netstat -ano | findstr :11434

# Kill the process (replace PID)
taskkill /PID <process_id> /F

# Or change Ollama port
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "127.0.0.1:11435", "User")
```

#### Issue 7: WSL2 Memory Conflicts

If using WSL2 alongside Ollama:

```powershell
# Create/edit .wslconfig in C:\Users\<username>\
[wsl2]
memory=8GB
swap=2GB
processors=4

# This leaves more RAM for Ollama
```

### 4.3 How to Avoid Errors

#### Pre-Flight Checklist

```powershell
# Run before starting inference session:

# 1. Check available memory
Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object FreePhysicalMemory

# 2. Close unnecessary applications
Get-Process | Where-Object {$_.ProcessName -match "chrome|firefox|edge"} | Stop-Process

# 3. Check CPU temperature (if monitoring software installed)
# Should be <70°C before starting

# 4. Verify Ollama is running
curl http://localhost:11434
# Should return "Ollama is running"

# 5. Test with small model first
ollama run gemma3:1b "test"
```

#### Best Practices

1. **Start Small:** Always test with 1B-3B models before loading larger ones
2. **Monitor Resources:** Keep Task Manager open to watch RAM/CPU usage
3. **One Model at a Time:** Unload models before loading new ones on limited RAM
4. **Regular Restarts:** Restart Ollama service daily for long-running setups
5. **Keep Updated:** `ollama update` regularly for performance improvements

---

## 5. PERFORMANCE EXPECTATIONS

### 5.1 Realistic Tokens/Second by Model

**Testing Conditions:**
- AMD Ryzen 7 5800X or equivalent
- 24GB DDR4-3200 RAM
- Windows 11 23H2
- CPU-only, no GPU
- Q4_K_M quantization

| Model | Parameters | RAM Used | Context 2K | Context 8K | Context 16K |
|-------|------------|----------|------------|------------|-------------|
| **gemma3:1b** | 1B | 1.5GB | 12-15 t/s | 10-12 t/s | 8-10 t/s |
| **phi4:mini** | 3.8B | 3GB | 8-12 t/s | 7-9 t/s | 5-7 t/s |
| **qwen2.5:7b** | 7B | 5GB | 6-10 t/s | 5-7 t/s | 4-5 t/s |
| **mistral:7b** | 7B | 4.5GB | 6-9 t/s | 5-6 t/s | 4-5 t/s |
| **llama3.2:8b** | 8B | 5GB | 5-8 t/s | 4-6 t/s | 3-4 t/s |
| **qwen2.5:14b** | 14B | 9GB | 4-7 t/s | 3-5 t/s | 2-3 t/s |
| **deepseek-r1:7b** | 7B | 5GB | 5-8 t/s | 4-6 t/s | 3-4 t/s |

**Notes:**
- Speed decreases with longer context (KV cache processing)
- First token latency (TTFT): 0.5-2 seconds depending on prompt length
- Ryzen 5000 series (Zen 3): Use lower end of ranges
- Ryzen 7000 series (Zen 4): Use higher end of ranges
- AVX-512 capable CPUs (some Intel, Ryzen 9000): +20-30% performance

### 5.2 Context Length Limits

| Model | Max Context | Practical Limit* | Memory per 1K tokens |
|-------|-------------|------------------|---------------------|
| gemma3:1b | 32K | 16K | ~50MB |
| phi4:mini | 128K | 32K | ~100MB |
| qwen2.5:7b | 128K | 32K | ~200MB |
| mistral:7b | 32K | 16K | ~200MB |
| llama3.2:8b | 128K | 32K | ~200MB |
| qwen2.5:14b | 128K | 16K | ~400MB |

*Practical limit considers RAM constraints and acceptable performance

**Context Length Recommendations:**

| Use Case | Recommended Context | Notes |
|----------|---------------------|-------|
| Quick Q&A | 2K | Fastest responses, minimal RAM |
| Document summarization | 8K | Good balance |
| Code analysis | 16K | Can analyze larger files |
| Long conversations | 8-16K | Depends on history length |
| Book/chapter analysis | 32K | Requires 14B+ model |

### 5.3 When to Use Cloud Fallback

**Use Local (Ollama) When:**
- Privacy is critical (medical, legal, proprietary data)
- Working offline or with unreliable internet
- Cost sensitivity (no per-token charges)
- Latency tolerance (5-15 t/s acceptable)
- Batch processing (can run overnight)

**Use Cloud API (Claude, GPT-4, etc.) When:**

| Scenario | Why Cloud Wins |
|----------|----------------|
| **Real-time coding autocomplete** | Need <100ms latency, 50+ t/s |
| **Complex reasoning tasks** | 70B+ models too slow on CPU |
| **Large context analysis** | >32K tokens with good performance |
| **High-volume production** | GPU throughput irreplaceable |
| **Voice assistants** | Low latency critical |
| **Creative writing** | Larger models produce better prose |
| **Multi-modal (vision)** | CPU too slow for image processing |

**Hybrid Approach (Recommended):**

```python
# Example: Use local for privacy, cloud for complexity

def process_document(text):
    if len(text) < 4000:
        # Local - fast enough for short docs
        return ollama_generate("qwen2.5:7b", text)
    elif contains_sensitive_data(text):
        # Local - privacy required
        return ollama_generate("qwen2.5:14b", text)
    else:
        # Cloud - better quality for long/complex
        return claude_api_call(text)
```

### 5.4 Performance Optimization Tips

#### For Maximum Speed

```powershell
# 1. Use all physical cores
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS", "8", "User")

# 2. Reduce context to minimum needed
ollama run model --num-ctx 2048

# 3. Use smaller models for speed-critical tasks
ollama pull qwen2.5:7b  # Instead of 14b

# 4. Keep models loaded (avoid reload penalty)
# Use API instead of CLI for multiple requests
```

#### For Maximum Quality

```powershell
# 1. Use largest model that fits in RAM
ollama pull qwen2.5:14b  # If RAM permits

# 2. Increase context for better coherence
ollama run model --num-ctx 8192

# 3. Adjust temperature for consistency
PARAMETER temperature 0.5  # Lower = more focused

# 4. Use reasoning models for complex tasks
ollama pull deepseek-r1:7b
```

#### For Memory Efficiency

```powershell
# 1. Use aggressive quantization (if available)
ollama pull model:q3_K_M  # 3-bit vs 4-bit

# 2. Reduce batch size
PARAMETER num_batch 256  # Default is often 512

# 3. Enable memory mapping (automatic in Ollama)
# Models load on-demand from disk

# 4. Unload models when not needed
ollama stop model_name
```

---

## Quick Reference Card

### Essential Commands

```powershell
# Install Ollama
winget install Ollama.Ollama

# Download models
ollama pull qwen2.5:7b
ollama pull gemma3:1b

# Run interactively
ollama run qwen2.5:7b

# One-shot generation
ollama run qwen2.5:7b "Your prompt here"

# List models
ollama list

# Check status
ollama ps

# Remove model
ollama rm model_name

# Update Ollama
ollama update
```

### Environment Variables

```powershell
# CPU-only mode
$env:OLLAMA_NUM_GPU="0"

# Thread count (match physical cores)
$env:OLLAMA_NUM_THREADS="8"

# Custom model path
$env:OLLAMA_MODELS="D:\OllamaModels"

# Context length
$env:OLLAMA_CONTEXT_LENGTH="8192"
```

### Model Size Quick Reference

| Model Size | RAM Needed | Use Case |
|------------|------------|----------|
| 1B | 2GB | Edge devices, fast responses |
| 3B | 3-4GB | Mobile/laptop, simple tasks |
| 7B | 5-6GB | General purpose, coding |
| 14B | 10-12GB | Better reasoning, analysis |
| 30B | 20-24GB | High quality (marginal on 24GB) |

---

## Resources & References

### Official Documentation
- Ollama: https://ollama.com/docs
- llama.cpp: https://github.com/ggerganov/llama.cpp
- BitNet: https://github.com/microsoft/BitNet
- TurboQuant: https://github.com/TheTom/turboquant_plus

### Model Repositories
- Ollama Library: https://ollama.com/library
- Hugging Face: https://huggingface.co/models

### Community
- r/LocalLLaMA: https://reddit.com/r/LocalLLaMA
- Ollama Discord: https://discord.gg/ollama

---

## Document Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-15 | Initial comprehensive guide |

---

*This guide was compiled for 24GB RAM Windows 11 systems with AMD Ryzen CPUs running without dedicated GPU. Performance figures are estimates based on community benchmarks and may vary by specific hardware configuration.*
