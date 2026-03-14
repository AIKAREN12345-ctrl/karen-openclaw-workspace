# Local Memory Provider Research - OpenClaw 2026.3.1

**Date:** 2026-03-03  
**Researcher:** Subagent for OpenClaw Local Memory  
**OpenClaw Version:** 2026.3.1

---

## Executive Summary

**YES** - You can use `provider: "local"` with node-llama-cpp and a GGUF embedding model for local memory search without cloud API keys.

Key findings:
1. ✅ node-llama-cpp is already installed (v3.16.2) as a peer dependency
2. ✅ Default model auto-downloads from HuggingFace (~0.6 GB)
3. ✅ Config structure supports custom GGUF models via `hf:` URI or local path
4. ✅ Nomic-embed-text can be used through local mode (GGUF format required)

---

## 1. Is node-llama-cpp Already Installed?

**YES** - Already installed at:
```
%APPDATA%\npm\node_modules\openclaw\node_modules\node-llama-cpp
```

Version: **3.16.2**

From `package.json` peerDependencies:
```json
"peerDependencies": {
  "@napi-rs/canvas": "^0.1.89",
  "node-llama-cpp": "3.16.2"
}
```

Also listed in `onlyBuiltDependencies` requiring native compilation.

---

## 2. What GGUF Models Are Available/Working?

### Default Model (Auto-downloaded)
```
hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf
```
- Size: ~0.6 GB
- Source: HuggingFace (ggml-org)
- Format: GGUF Q8_0 quantized
- Auto-downloads on first use if not present

### Nomic-embed-text Support

**Yes**, nomic-embed-text can be used through local mode, but it must be in **GGUF format**.

Available GGUF variants on HuggingFace:
- `nomic-ai/nomic-embed-text-v1.5-GGUF` (various quantizations)
- `nomic-ai/nomic-embed-text-v1-GGUF`

Example model path format:
```
hf:nomic-ai/nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.Q8_0.gguf
```

### Model Path Formats Supported

From the type definitions (`embeddings.d.ts`):

```typescript
type EmbeddingProviderOptions = {
  local?: {
    modelPath?: string;      // GGUF file path or hf: URI
    modelCacheDir?: string;  // Custom cache directory
  };
};
```

**Supported modelPath formats:**
1. **HuggingFace URI**: `hf:org/repo/model.gguf` (auto-downloads)
2. **Absolute path**: `C:\models\embedding.gguf`
3. **Relative path**: Resolved against agent directory

---

## 3. Exact Config Structure for Local Provider

### Minimal Working Config

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
        provider: "local",
        // Optional: specify custom model (defaults to embeddinggemma-300m)
        local: {
          modelPath: "hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf",
          modelCacheDir: "~/.cache/openclaw/models"  // Optional
        },
        // Optional: disable fallback to avoid using cloud APIs
        fallback: "none"
      }
    }
  }
}
```

### Full Config with All Options

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
        provider: "local",        // "local" | "openai" | "gemini" | "voyage" | "mistral" | "auto"
        fallback: "none",         // "none" | "local" | "openai" | "gemini" | "voyage" | "mistral"
        
        // Local embedding configuration
        local: {
          modelPath: "hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf",
          modelCacheDir: "~/.cache/openclaw/models"
        },
        
        // Storage configuration
        store: {
          driver: "sqlite",
          path: "~/.openclaw/memory/{agentId}.sqlite",
          vector: {
            enabled: true,
            extensionPath: "/path/to/sqlite-vec"  // Optional override
          }
        },
        
        // Chunking settings
        chunking: {
          tokens: 400,      // Target tokens per chunk
          overlap: 80       // Token overlap between chunks
        },
        
        // Sync behavior
        sync: {
          onSessionStart: true,
          onSearch: true,
          watch: true,
          watchDebounceMs: 1500,
          intervalMinutes: 5,
          sessions: {
            deltaBytes: 100000,
            deltaMessages: 50
          }
        },
        
        // Query settings
        query: {
          maxResults: 10,
          minScore: 0.0,
          hybrid: {
            enabled: true,
            vectorWeight: 0.7,
            textWeight: 0.3,
            candidateMultiplier: 4,
            mmr: {
              enabled: false,
              lambda: 0.7
            },
            temporalDecay: {
              enabled: false,
              halfLifeDays: 30
            }
          }
        },
        
        // Cache settings
        cache: {
          enabled: true,
          maxEntries: 50000
        },
        
        // Additional memory paths
        extraPaths: [
          "../team-docs",
          "C:/shared-notes"
        ],
        
        // Experimental features
        experimental: {
          sessionMemory: false
        }
      }
    }
  }
}
```

---

## 4. Can We Use nomic-embed-text Through Local Mode?

**YES** - Here's how:

### Option A: Using HuggingFace URI (Recommended)

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
        provider: "local",
        local: {
          modelPath: "hf:nomic-ai/nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.Q8_0.gguf"
        },
        fallback: "none"
      }
    }
  }
}
```

### Option B: Manual Download + Local Path

1. Download nomic-embed-text GGUF from HuggingFace:
   ```bash
   # Using huggingface-cli or browser
   https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF
   ```

2. Place in cache directory:
   ```
   %USERPROFILE%\.cache\openclaw\models\nomic-embed-text-v1.5.Q8_0.gguf
   ```

3. Configure with absolute path:
   ```json5
   {
     agents: {
       defaults: {
         memorySearch: {
           enabled: true,
           provider: "local",
           local: {
             modelPath: "C:/Users/Karen/.cache/openclaw/models/nomic-embed-text-v1.5.Q8_0.gguf"
           }
         }
       }
     }
   }
   ```

### Nomic-embed-text Model Variants

| Model | Quantization | Size | URI Path |
|-------|-------------|------|----------|
| nomic-embed-text-v1.5 | Q8_0 | ~260MB | `hf:nomic-ai/nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.Q8_0.gguf` |
| nomic-embed-text-v1.5 | Q4_0 | ~130MB | `hf:nomic-ai/nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.Q4_0.gguf` |
| nomic-embed-text-v1 | Q8_0 | ~260MB | `hf:nomic-ai/nomic-embed-text-v1-GGUF/nomic-embed-text-v1.Q8_0.gguf` |

---

## 5. Setup Steps

### Prerequisites

1. **Native build tools** (for node-llama-cpp):
   - Windows: Visual Studio Build Tools or Visual Studio Community
   - Python 3.x (for node-gyp)

2. **pnpm** (for approve-builds):
   ```bash
   npm install -g pnpm
   ```

### Installation Steps

1. **Approve and build node-llama-cpp:**
   ```bash
   cd %APPDATA%\npm\node_modules\openclaw
   pnpm approve-builds
   # Select: node-llama-cpp
   pnpm rebuild node-llama-cpp
   ```

2. **Configure OpenClaw** (edit `%USERPROFILE%\.openclaw\openclaw.json`):
   ```json5
   {
     agents: {
       defaults: {
         memorySearch: {
           enabled: true,
           provider: "local",
           local: {
             modelPath: "hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf"
           },
           fallback: "none"
         }
       }
     }
   }
   ```

3. **First run** - Model auto-download:
   - On first `memory_search` or `openclaw memory index`, the model will download
   - ~0.6 GB download for default model
   - Cached for subsequent runs

4. **Verify installation:**
   ```bash
   openclaw memory status --deep
   ```

---

## 6. Key Technical Details

### How Local Embeddings Work

From the type definitions:

```typescript
// embeddings.d.ts
export type EmbeddingProvider = {
  id: string;
  model: string;
  maxInputTokens?: number;
  embedQuery: (text: string) => Promise<number[]>;
  embedBatch: (texts: string[]) => Promise<number[][]>;
};

// node-llama.d.ts
export declare function importNodeLlamaCpp(): Promise<{
  default: typeof import("node-llama-cpp");
  getLlama(params: {
    logLevel: import("node-llama-cpp").LlamaLogLevel;
  }): Promise<import("node-llama-cpp").Llama>;
  resolveModelFile(modelPath: string, cacheDir?: string): Promise<string>;
  LlamaLogLevel: typeof import("node-llama-cpp").LlamaLogLevel;
}>;
```

The local provider uses:
1. `node-llama-cpp` for GGUF model loading and inference
2. `LlamaEmbeddingContext` for generating embeddings
3. `resolveModelFile()` for HuggingFace URI resolution
4. SQLite with sqlite-vec for vector storage

### Auto-Selection Logic

If `provider` is not set, OpenClaw auto-selects:
1. `local` if `memorySearch.local.modelPath` is configured and file exists
2. `openai` if OpenAI key can be resolved
3. `gemini` if Gemini key can be resolved
4. `voyage` if Voyage key can be resolved
5. `mistral` if Mistral key can be resolved
6. Otherwise disabled

### Memory Index Storage

- Location: `~/.openclaw/memory/{agentId}.sqlite`
- Format: SQLite with optional sqlite-vec extension
- Embeddings cached to avoid re-computation
- Automatic reindex when provider/model/chunking changes

---

## 7. Troubleshooting

### Issue: "node-llama-cpp build failed"

**Solution:**
```bash
cd %APPDATA%\npm\node_modules\openclaw
pnpm approve-builds
# Select node-llama-cpp
pnpm rebuild node-llama-cpp
```

### Issue: "Model download fails"

**Solution:**
- Check internet connection
- Verify HuggingFace is accessible
- Try manual download and use local path

### Issue: "Out of memory during embedding"

**Solution:**
- Use smaller quantization (Q4_0 instead of Q8_0)
- Reduce `chunking.tokens` value
- Close other applications

### Issue: "Slow first search"

**Expected:** First search triggers model download and index build. Subsequent searches are fast.

---

## 8. Comparison: Local vs Ollama

| Feature | Local (node-llama-cpp) | Ollama |
|---------|------------------------|--------|
| Requires separate daemon | No | Yes |
| Model download | Auto (HF) | Manual (`ollama pull`) |
| API key required | No | No |
| Embedding dimensions | Model-dependent (768-1024) | Model-dependent |
| Speed | Fast (direct) | Fast (local API) |
| Setup complexity | Medium (native builds) | Low |
| Works in sandbox | Yes | No (requires localhost) |

**Key advantage of Local mode:** Works in sandboxed environments where Ollama cannot be reached (like `local-automation` agent).

---

## 9. References

### Type Definitions
- `dist/plugin-sdk/memory/embeddings.d.ts` - Embedding provider types
- `dist/plugin-sdk/memory/node-llama.d.ts` - node-llama-cpp integration
- `dist/plugin-sdk/agents/memory-search.d.ts` - Memory search config
- `dist/plugin-sdk/config/types.memory.d.ts` - Memory config types

### Documentation
- `docs/concepts/memory.md` - Comprehensive memory documentation
- `docs/cli/memory.md` - CLI reference

### Package Info
- `node-llama-cpp` v3.16.2 - https://github.com/withcatai/node-llama-cpp
- Default model: https://huggingface.co/ggml-org/embeddinggemma-300m-qat-q8_0-GGUF

---

## 10. Working Config Examples

### Minimal Local Setup (Default Model)
```json5
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
        provider: "local",
        fallback: "none"
      }
    }
  }
}
```

### Nomic-embed-text Setup
```json5
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
        provider: "local",
        local: {
          modelPath: "hf:nomic-ai/nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.Q8_0.gguf"
        },
        fallback: "none"
      }
    }
  }
}
```

### Local with Hybrid Search
```json5
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
        provider: "local",
        fallback: "none",
        query: {
          hybrid: {
            enabled: true,
            vectorWeight: 0.7,
            textWeight: 0.3
          }
        }
      }
    }
  }
}
```

---

*End of Research Document*
