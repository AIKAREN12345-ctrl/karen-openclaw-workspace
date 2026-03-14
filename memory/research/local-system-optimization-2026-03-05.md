# Local System Optimization Research

**Date:** 2026-03-05  
**Research Goal:** Reduce OpenClaw dependency on Kimi cloud API while maintaining reliability

---

## Executive Summary

This research evaluates strategies to make OpenClaw more local-first and less cloud-dependent. The current system relies on Kimi (k2p5) for interactive work and qwen2.5:14b locally for automation. Key findings:

1. **Local LLM alternatives exist** - llama.cpp offers best performance, vLLM for high-throughput serving
2. **Cron job localhost issue** - Sandbox isolation prevents `local-automation` agents from accessing Ollama
3. **Qwen optimization** - Quantization (Q4/Q5) can significantly improve inference speed
4. **Vector DB options** - ChromaDB (easiest), FAISS (fastest), LanceDB (multimodal)
5. **Hybrid architecture** - Tiered routing: local models for routine tasks, cloud for complex reasoning

---

## 1. Alternative Local LLM Options Beyond Ollama

### 1.1 llama.cpp (Recommended for Performance)

**What it is:** The foundational C++ inference engine that powers Ollama and many other tools.

**Advantages:**
- **Fastest inference** for consumer hardware
- Supports all major quantization formats (Q4_K_M, Q5_K_M, Q8_0)
- Direct GPU acceleration (CUDA, ROCm, Metal, Vulkan)
- OpenAI-compatible server mode (`llama-server`)
- Smallest memory footprint

**Performance Benchmarks (from llama.cpp docs):**
| Configuration | Tokens/sec |
|--------------|------------|
| CPU only (-t 7) | 1.7 t/s |
| GPU (-ngl max, -t 1) | 5.5 t/s |
| GPU (-ngl max, -t 4) | 9.1 t/s |
| GPU (-ngl max, -t 7) | 8.7 t/s |

**Windows Installation:**
```powershell
# Requires Visual Studio 2022 with C++ workload
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON  # For NVIDIA GPU
cmake --build build --config Release
```

**Usage with OpenClaw:**
```bash
# Start server
./llama-server -m qwen2.5-14b-q4_k_m.gguf --port 8080 -ngl 99

# OpenClaw can then use http://localhost:8080/v1/chat/completions
```

### 1.2 vLLM (High-Throughput Serving)

**What it is:** Production-grade inference engine with PagedAttention for efficient memory management.

**Advantages:**
- **State-of-the-art throughput** for concurrent requests
- Continuous batching
- Speculative decoding support
- Tensor/pipeline parallelism for multi-GPU
- OpenAI-compatible API

**Best for:** Multi-user scenarios, high request volume

**Installation:**
```bash
pip install vllm
```

**Usage:**
```bash
vllm serve Qwen/Qwen2.5-14B-Instruct --quantization awq --port 8000
```

**Trade-offs:**
- Higher memory usage than llama.cpp
- More complex setup
- Better for servers than single-user desktop

### 1.3 LocalAI (Drop-in OpenAI Replacement)

**What it is:** Unified API wrapper supporting multiple backends (llama.cpp, transformers, diffusers, etc.)

**Advantages:**
- Single API for multiple backends
- Supports text, images, audio, embeddings
- Built-in model gallery
- Docker deployment available
- No GPU required (CPU fallback)

**Backends Supported:**
- llama.cpp (CUDA, ROCm, Intel, Vulkan, Metal)
- vLLM (CUDA, ROCm, Intel)
- transformers (HuggingFace)
- MLX (Apple Silicon)

**Docker Quick Start:**
```bash
docker run -ti --name local-ai -p 8080:8080 localai/localai:latest-aio-cpu
```

### 1.4 Jan (User-Friendly Desktop App)

**What it is:** Electron-based desktop UI for local LLMs

**Advantages:**
- 100% offline operation
- Built-in model management
- OpenAI-compatible local API (localhost:1337)
- Supports both local and cloud models

**Best for:** Users who want a GUI for model management

### 1.5 Comparison Matrix

| Tool | Speed | Ease of Use | Features | Best For |
|------|-------|-------------|----------|----------|
| **llama.cpp** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Raw performance, scripting |
| **vLLM** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Production serving |
| **LocalAI** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Unified API, multiple modalities |
| **Jan** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Desktop users |
| **Ollama** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Current setup, ease of use |

---

## 2. Fixing the Localhost Access Issue for Cron Jobs

### 2.1 The Problem

From TOOLS.md: "Ollama + local-automation agent: Timeout/failure due to sandbox isolation"

**Root Cause:** Sub-agents spawned with `local-automation` profile run in isolated sandboxes that cannot access localhost services like Ollama (running at localhost:11434).

### 2.2 Solutions

#### Option A: Use `agent:main` for Ollama Tasks (Current Workaround)

**Implementation:**
```json
{
  "agent": "agent:main",
  "model": "local/qwen2.5:14b"
}
```

**Pros:** Works immediately  
**Cons:** Consumes main session resources

#### Option B: Run Ollama in Network Mode

Configure Ollama to listen on all interfaces:

```powershell
# Windows - Set environment variable
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0:11434", "User")

# Then restart Ollama
ollama serve
```

**Then use host IP instead of localhost:**
```
http://192.168.1.x:11434/api/generate
```

**Pros:** Sandbox can reach via network  
**Cons:** Security implications, firewall rules needed

#### Option C: Use Named Pipes (Windows)

Ollama supports Windows named pipes for IPC:

```
\\.\pipe\ollama
```

**Requires:** Ollama client support for named pipes

#### Option D: Switch to llama.cpp Server

Run llama.cpp server instead of Ollama:

```bash
# llama-server binds to all interfaces by default
./llama-server -m model.gguf --host 0.0.0.0 --port 8080
```

**Pros:** More control, potentially faster  
**Cons:** Manual model management

#### Option E: Container-Based Solution

Run Ollama in Docker with host networking:

```bash
docker run -d --network host -v ollama:/root/.ollama ollama/ollama
```

**Note:** `--network host` works on Linux; on Windows use port mapping with host.docker.internal

### 2.3 Recommended Approach

**Short-term:** Continue using `agent:main` for Ollama tasks  
**Long-term:** Migrate to llama.cpp server with proper network configuration for better performance and control

---

## 3. Optimizing qwen2.5:14b Performance

### 3.1 Quantization Options

Qwen2.5-14B model sizes:
| Format | Size | Quality | Speed |
|--------|------|---------|-------|
| FP16 | ~28 GB | ⭐⭐⭐⭐⭐ | Slowest |
| Q8_0 | ~15 GB | ⭐⭐⭐⭐⭐ | Fast |
| Q5_K_M | ~10 GB | ⭐⭐⭐⭐ | Faster |
| Q4_K_M | ~8.5 GB | ⭐⭐⭐⭐ | Fastest recommended |
| Q3_K_M | ~6.5 GB | ⭐⭐⭐ | Fast, quality loss |
| Q2_K | ~5 GB | ⭐⭐ | Very fast, significant loss |

**Recommendation:** Use Q4_K_M or Q5_K_M for best speed/quality balance

### 3.2 Windows-Specific Optimizations

**1. GPU Offloading (-ngl flag)**
```bash
# Offload all layers to GPU
ollama run qwen2.5:14b --num-gpu-layers 99

# Or in Modelfile
PARAMETER num_gpu_layers 99
```

**2. Context Length Optimization**
```bash
# Reduce context for faster inference (default 2048)
PARAMETER num_ctx 4096  # Increase if needed
```

**3. Thread Configuration**
```bash
# Match physical cores, not logical
PARAMETER num_thread 8  # For 8-core CPU
```

**4. Flash Attention (if supported)**
```bash
# Enable Flash Attention for faster inference
OLLAMA_FLASH_ATTENTION=1 ollama serve
```

### 3.3 llama.cpp Specific Optimizations

```bash
./llama-cli \
  -m qwen2.5-14b-q4_k_m.gguf \
  -ngl 99 \              # GPU layers
  -fa \                   # Flash attention
  -t 8 \                  # Threads
  -c 4096 \               # Context
  --temp 0.6 \            # Temperature
  --top-k 20 \
  --top-p 0.95
```

### 3.4 Expected Performance

With RTX 4090 (24GB VRAM):
- Q4_K_M: ~40-60 tokens/sec
- Q5_K_M: ~35-50 tokens/sec

With CPU only (8 cores):
- Q4_K_M: ~5-10 tokens/sec

---

## 4. Local Vector Databases and Search Alternatives

### 4.1 ChromaDB (Recommended for Simplicity)

**Features:**
- Pure Python, easy setup
- Built-in embedding functions
- Persistent or in-memory
- LangChain/LlamaIndex integration

**Installation:**
```bash
pip install chromadb
```

**Usage:**
```python
import chromadb
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.create_collection("memory")
```

**Pros:** Easiest to use, great documentation  
**Cons:** Not the fastest for very large datasets

### 4.2 FAISS (Recommended for Speed)

**Features:**
- Meta's high-performance library
- GPU acceleration
- Multiple index types (Flat, IVF, HNSW)
- Billions of vectors possible

**Installation:**
```bash
conda install -c pytorch faiss-gpu  # GPU
pip install faiss-cpu               # CPU
```

**Pros:** Fastest search, GPU support  
**Cons:** Lower-level API, requires more setup

### 4.3 LanceDB (Recommended for Multimodal)

**Features:**
- Columnar storage (Apache Arrow)
- Zero-copy reads
- Automatic versioning
- GPU index building
- Multimodal support (text, images, video)

**Installation:**
```bash
pip install lancedb
```

**Pros:** Modern, fast, handles complex data  
**Cons:** Newer, smaller community

### 4.4 Comparison

| Feature | ChromaDB | FAISS | LanceDB |
|---------|----------|-------|---------|
| Setup | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Speed | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Scale | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Features | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Best For | Quick start | Max performance | Complex apps |

### 4.5 Recommendation for OpenClaw

**Use ChromaDB** for:
- Memory system implementation
- Quick prototyping
- Small-to-medium datasets (<1M vectors)

**Migration path:**
```python
# Current: No local vector DB
# Future:
import chromadb
client = chromadb.PersistentClient(path="~/.openclaw/vector_db")
memory_collection = client.get_or_create_collection("long_term_memory")
```

---

## 5. Hybrid Architectures to Minimize Cloud API Usage

### 5.1 Tiered Routing Strategy

```
User Request
    │
    ▼
┌─────────────────┐
│  Request Router │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┬────────────────┐
    ▼         ▼              ▼                ▼
┌───────┐ ┌────────┐ ┌──────────────┐ ┌─────────────┐
│Simple │ │Medium  │ │Complex       │ │Critical     │
│Tasks  │ │Tasks   │ │Reasoning     │ │Accuracy     │
│       │ │        │ │              │ │             │
│qwen2.5│ │qwen2.5 │ │Kimi (k2p5)   │ │Kimi + Verify│
│14b    │ │14b-Q8  │ │              │ │             │
└───────┘ └────────┘ └──────────────┘ └─────────────┘
```

### 5.2 Task Classification

| Task Type | Example | Model | Est. Savings |
|-----------|---------|-------|--------------|
| **Simple** | Greetings, acknowledgments | Local 7B | 100% |
| **Routine** | Heartbeats, status checks | Local 14B | 100% |
| **Standard** | Coding, analysis | Local 14B-Q8 | 80% |
| **Complex** | Architecture decisions | Kimi | 0% |
| **Critical** | Security, irreversible ops | Kimi | 0% |

### 5.3 Confidence-Based Routing

```python
def route_request(prompt, complexity_score):
    if complexity_score < 0.3:
        return "local/qwen2.5:7b"  # Fast, simple
    elif complexity_score < 0.7:
        return "local/qwen2.5:14b"  # Capable
    else:
        return "kimi/k2p5"  # Reliable
```

### 5.4 Fallback Strategy

```
1. Try local model
2. If response confidence < threshold:
   a. Retry with higher temperature
   b. Or escalate to cloud model
3. Log results for model improvement
```

### 5.5 Cost-Benefit Analysis

**Current State (estimated):**
- Kimi API: ~$0.01-0.03 per 1K tokens
- Daily usage: ~50K tokens = $0.50-1.50/day
- Monthly: ~$15-45

**With Hybrid Approach:**
- Local inference: $0 (hardware already owned)
- Cloud for 20% of requests: ~$3-9/month
- **Savings: ~70-80%**

**Hardware Amortization:**
- GPU upgrade (RTX 4070 Ti): ~$800
- Break-even: 18-26 months vs cloud-only

---

## 6. Actionable Recommendations

### Immediate (This Week)

1. **Test qwen2.5:14b with Q4_K_M quantization**
   ```bash
   ollama pull qwen2.5:14b-q4_K_M
   # Compare speed vs current setup
   ```

2. **Enable Flash Attention**
   ```powershell
   [Environment]::SetEnvironmentVariable("OLLAMA_FLASH_ATTENTION", "1", "User")
   ```

3. **Document cron job workaround**
   - Update TOOLS.md with `agent:main` requirement for Ollama tasks

### Short-term (This Month)

4. **Install ChromaDB for memory search**
   ```bash
   pip install chromadb
   ```
   - Implement semantic memory search
   - Migrate from disabled local search

5. **Set up llama.cpp server**
   - Build from source with CUDA
   - Test with qwen2.5-14b GGUF
   - Benchmark vs Ollama

6. **Implement hybrid routing**
   - Create task complexity classifier
   - Route simple tasks to local models
   - Keep Kimi for complex reasoning

### Long-term (Next Quarter)

7. **Evaluate vLLM for multi-agent scenarios**
   - If running multiple sub-agents concurrently
   - Better throughput than Ollama

8. **Consider GPU upgrade**
   - RTX 4070 Ti Super (16GB) or RTX 4090 (24GB)
   - Enables larger models or higher quantization

9. **Implement LocalAI as unified backend**
   - Single API for all local models
   - Easier model switching

### Priority Matrix

| Priority | Task | Impact | Effort |
|----------|------|--------|--------|
| 🔴 High | Q4_K_M quantization | High | Low |
| 🔴 High | Flash Attention | High | Low |
| 🟡 Medium | ChromaDB setup | Medium | Medium |
| 🟡 Medium | llama.cpp evaluation | High | Medium |
| 🟢 Low | vLLM exploration | Medium | High |
| 🟢 Low | GPU upgrade | High | High |

---

## 7. References

- [llama.cpp Documentation](https://github.com/ggml-org/llama.cpp)
- [vLLM Documentation](https://docs.vllm.ai)
- [Qwen2.5/3 Documentation](https://qwen.readthedocs.io)
- [ChromaDB](https://docs.trychroma.com)
- [FAISS](https://github.com/facebookresearch/faiss)
- [LanceDB](https://lancedb.com)
- [LocalAI](https://localai.io)
- [Open WebUI](https://docs.openwebui.com)

---

## Appendix: Current System Specs

From TOOLS.md:
- **OS:** Windows 11
- **GPU:** (Not specified - need to check)
- **RAM:** (Not specified - need to check)
- **Current Model:** qwen2.5:14b (9.0 GB)
- **Embeddings:** nomic-embed-text (274 MB)

**Recommended next step:** Verify GPU model and VRAM to determine optimal quantization level.
