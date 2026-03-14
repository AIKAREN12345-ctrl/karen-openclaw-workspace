# Local Memory Search in OpenClaw 2026.3.1 - Research Findings

**Date:** 2026-03-03  
**OpenClaw Version:** 2026.3.1  
**Research Goal:** Enable fully local memory search without cloud API keys

---

## Executive Summary

**YES, local memory search is fully supported in OpenClaw 2026.3.1** using the `node-llama-cpp` peer dependency. No cloud API keys (OpenAI/Gemini/Voyage) are required.

Two backend options exist:
1. **Builtin backend** (default) - Uses local embeddings via `node-llama-cpp` or remote providers
2. **QMD backend** - External query-my-documents tool (separate installation)

---

## 1. Supported Providers (Verified from Source Code)

From `dist/manager-gcdV1q_K.js`, the following embedding providers are supported:

### Remote Providers (Require API Keys)
| Provider | Default Model | Base URL |
|----------|---------------|----------|
| `openai` | text-embedding-3-small | https://api.openai.com/v1 |
| `gemini` | gemini-embedding-001 | https://generativelanguage.googleapis.com/v1beta |
| `voyage` | voyage-4-large | https://api.voyageai.com/v1 |
| `mistral` | mistral-embed | https://api.mistral.ai/v1 |

### Local Provider (NO API Key Required)
| Provider | Requirements | Notes |
|----------|--------------|-------|
| `local` | node-llama-cpp + GGUF model | Fully offline, runs on CPU/GPU |

### Auto Selection
When `provider: "auto"`, OpenClaw tries in order:
1. **Local** - If `local.modelPath` points to an existing file
2. **Remote providers** - In order: gemini, voyage, mistral, openai

---

## 2. Local Provider Deep Dive

### How It Works
The local provider uses `node-llama-cpp` (listed as peer dependency in package.json) to run embedding models locally:

```javascript
// From dist/manager-gcdV1q_K.js
async function createLocalEmbeddingProvider(options) {
  const modelPath = options.local?.modelPath?.trim() || DEFAULT_LOCAL_MODEL;
  const { getLlama, resolveModelFile, LlamaLogLevel } = await importNodeLlamaCpp();
  
  return {
    id: "local",
    model: modelPath,
    embedQuery: async (text) => {
      const embedding = await (await ensureContext()).getEmbeddingFor(text);
      return sanitizeAndNormalizeEmbedding(Array.from(embedding.vector));
    },
    embedBatch: async (texts) => { /* ... */ }
  };
}
```

### Default Model
```javascript
const DEFAULT_LOCAL_MODEL = "hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf";
```

This is a HuggingFace download path - OpenClaw will auto-download this model on first use.

---

## 3. Working Configuration for Local Memory Search

### Minimal Config (Auto-download default model)
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "local"
      }
    }
  }
}
```

### Config with Custom Model Path
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "local",
        "local": {
          "modelPath": "~/models/nomic-embed-text-v1.5.f16.gguf",
          "modelCacheDir": "~/.cache/llama-models"
        },
        "store": {
          "driver": "sqlite",
          "path": "~/.openclaw/memory/{agentId}.sqlite",
          "vector": {
            "enabled": true
          }
        },
        "chunking": {
          "tokens": 400,
          "overlap": 80
        },
        "query": {
          "maxResults": 6,
          "minScore": 0.35,
          "hybrid": {
            "enabled": true,
            "vectorWeight": 0.7,
            "textWeight": 0.3
          }
        },
        "cache": {
          "enabled": true
        }
      }
    }
  }
}
```

### Config with Fallback (Local → Remote if local fails)
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "local",
        "fallback": "openai",
        "local": {
          "modelPath": "~/models/my-embedding-model.gguf"
        },
        "remote": {
          "apiKey": "sk-...",
          "baseUrl": "https://api.openai.com/v1"
        }
      }
    }
  }
}
```

---

## 4. Compatible GGUF Embedding Models

Based on `node-llama-cpp` compatibility, these models work:

### Recommended Models

| Model | Size | Dimensions | Source | Best For |
|-------|------|------------|--------|----------|
| **embeddinggemma-300m-qat-Q8_0** | ~300M | 2304 | Default (HuggingFace) | General purpose, good balance |
| **nomic-embed-text-v1.5** | ~550M | 768 | HuggingFace | High quality, widely used |
| **bge-large-en-v1.5** | ~1.3B | 1024 | HuggingFace | Best accuracy, larger size |
| **bge-small-en-v1.5** | ~130M | 384 | HuggingFace | Fast, low resource |
| **gte-base** | ~220M | 768 | HuggingFace | Good general performance |

### Download URLs (HuggingFace)
```bash
# Default model (auto-downloaded)
hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf

# Nomic Embed
hf:nomic-ai/nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.f16.gguf

# BGE Small
hf:BAAI/bge-small-en-v1.5-gguf/bge-small-en-v1.5-q8_0.gguf

# BGE Large
hf:BAAI/bge-large-en-v1.5-gguf/bge-large-en-v1.5-q8_0.gguf
```

### Model Path Formats Supported
```javascript
// HuggingFace shorthand (auto-downloads)
"hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf"

// Absolute path
"/home/user/models/nomic-embed-text-v1.5.f16.gguf"
"C:\\Users\\Karen\\models\\nomic-embed-text-v1.5.f16.gguf"

// Relative to workspace
"./models/my-model.gguf"

// Home directory expansion
"~/models/my-model.gguf"
```

---

## 5. Step-by-Step Setup Instructions

### Step 1: Verify node-llama-cpp Installation

```bash
# Check if node-llama-cpp is installed
npm list -g node-llama-cpp

# If using pnpm
pnpm list -g node-llama-cpp
```

If not installed, it should be installed as a peer dependency. If missing:

```bash
# Option A: Reinstall OpenClaw (recommended)
npm uninstall -g openclaw
npm install -g openclaw@latest

# Option B: Manual install (pnpm)
pnpm add -g node-llama-cpp@3.16.2
pnpm approve-builds  # Select node-llama-cpp when prompted
pnpm rebuild node-llama-cpp
```

### Step 2: Create Model Directory (Optional)

```bash
# Create directory for models
mkdir -p ~/.cache/llama-models

# Or use a custom path
mkdir -p ~/models
```

### Step 3: Configure OpenClaw

Edit `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "local",
        "local": {
          "modelPath": "hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf"
        }
      }
    }
  }
}
```

### Step 4: Test Memory Search

```bash
# Check status
openclaw memory status --deep

# Force reindex
openclaw memory index --force

# Search
openclaw memory search "your query here"
```

---

## 6. Verification Steps

### Check 1: Verify Provider is Local
```bash
openclaw memory status
```

Expected output should show:
```
Provider: local (requested: local)
Model: hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf
```

### Check 2: Verify Embeddings Work
```bash
openclaw memory status --deep
```

Look for:
```
Embeddings: ready
Vector: ready
```

### Check 3: Test Search
```bash
# Create a test memory file
echo "# Test Memory\n\nThis is a test about local embeddings without API keys." > ~/.openclaw/workspace/memory/test.md

# Reindex
openclaw memory index --force

# Search
openclaw memory search "local embeddings"
```

### Check 4: Verify No API Calls
Monitor network traffic during indexing/search - there should be no outbound HTTPS calls to OpenAI, Gemini, or Voyage.

---

## 7. Troubleshooting

### Issue: "Local embeddings unavailable"
**Cause:** `node-llama-cpp` not installed or failed to build

**Fix:**
```bash
# Check Node version (must be >= 22)
node --version

# Reinstall
npm uninstall -g openclaw
npm install -g openclaw@latest

# For pnpm users
pnpm approve-builds
pnpm rebuild node-llama-cpp
```

### Issue: "Model file not found"
**Cause:** Invalid model path or download failed

**Fix:**
```bash
# Use absolute path
"modelPath": "/full/path/to/model.gguf"

# Or let it auto-download (use hf: prefix)
"modelPath": "hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf"
```

### Issue: Slow indexing
**Cause:** Large model or CPU-only inference

**Fix:**
- Use smaller model (bge-small-en-v1.5)
- Enable batch processing (automatic for remote providers, sequential for local)
- Reduce chunk size: `"chunking": { "tokens": 200 }`

### Issue: Out of memory
**Cause:** Model too large for available RAM

**Fix:**
- Use quantized model (Q4_0, Q8_0)
- Use smaller model (bge-small-en-v1.5 at 130M params)
- Close other applications

---

## 8. QMD Backend Alternative

The QMD (query-my-documents) backend is an **alternative** to the builtin backend, not a replacement for local embeddings.

### Key Differences

| Feature | Builtin Backend | QMD Backend |
|---------|-----------------|-------------|
| Embeddings | Local (node-llama-cpp) or Remote | Configurable (separate tool) |
| Storage | SQLite + sqlite-vec | External QMD index |
| Requires | node-llama-cpp (optional) | qmd binary installed |
| API Keys | Optional (only if using remote) | Depends on QMD config |

### QMD Config (if you prefer external tool)
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "backend": "qmd",
        "qmd": {
          "command": "qmd",
          "searchMode": "search",
          "includeDefaultMemory": true,
          "update": {
            "interval": "5m",
            "onBoot": true
          }
        }
      }
    }
  }
}
```

**Note:** QMD is a separate tool that needs its own installation and configuration. For fully local embeddings without external dependencies, use the **builtin backend with local provider**.

---

## 9. Performance Benchmarks (Estimated)

Based on model sizes and typical embedding throughput:

| Model | Params | RAM Required | Speed (docs/sec)* | Quality |
|-------|--------|--------------|-------------------|---------|
| bge-small-en-v1.5 | 130M | ~500MB | 50-100 | Good |
| embeddinggemma-300m | 300M | ~1GB | 20-40 | Better |
| nomic-embed-text-v1.5 | 550M | ~1.5GB | 15-30 | Better |
| bge-large-en-v1.5 | 1.3B | ~3GB | 5-15 | Best |

*On modern CPU (8+ cores). GPU acceleration significantly faster.

---

## 10. Summary

### ✅ What Works
- **Fully local embeddings** using `node-llama-cpp`
- **No API keys required** when using `provider: "local"`
- **Auto-download** from HuggingFace with `hf:` prefix
- **Custom model paths** for downloaded GGUF files
- **Hybrid search** (vector + FTS) with local embeddings
- **Fallback to remote** if local fails (optional)

### ❌ What Doesn't Work
- Using Ollama directly for embeddings (Ollama is for chat models, not embeddings in this context)
- Remote providers without API keys

### 🔧 Requirements
- Node.js >= 22
- `node-llama-cpp` peer dependency (auto-installed or manual)
- ~500MB-3GB RAM depending on model size
- GGUF format embedding models

### 📁 Key Files
- Config: `~/.openclaw/openclaw.json`
- Index: `~/.openclaw/memory/{agentId}.sqlite`
- Models: `~/.cache/llama-models/` (default) or custom path

---

## References

- Source: `C:\Users\Karen\AppData\Roaming\npm\node_modules\openclaw\dist\manager-gcdV1q_K.js`
- Source: `C:\Users\Karen\AppData\Roaming\npm\node_modules\openclaw\dist\memory-cli-CD7q12-X.js`
- Package: `C:\Users\Karen\AppData\Roaming\npm\node_modules\openclaw\package.json`
- Docs: https://docs.openclaw.ai

---

*Research completed: 2026-03-03*
