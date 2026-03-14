# OpenClaw Memory System Fixes

**Research Date:** 2026-03-03  
**Issues Addressed:**
1. Memory search broken - embedding provider error
2. Subagent timeouts on memory operations
3. 30-second gateway timeout blocking long tasks

---

## 1. Embedding Provider Fix

### Current Problem
From `openclaw.json`:
```json
"memorySearch": {
  "provider": "local",
  "local": {
    "modelPath": "C:\\Users\\Karen\\Models\\all-MiniLM-L6-v2"
  }
}
```

The `modelPath` points to a directory that **does not exist** (confirmed: `Directory not found`).

### Solution Options

#### Option A: Use Ollama for Embeddings (Recommended)
Ollama is already running with `nomic-embed-text` installed:

```json
"memorySearch": {
  "provider": "ollama",
  "ollama": {
    "baseUrl": "http://localhost:11434",
    "model": "nomic-embed-text"
  }
}
```

**Pros:**
- Already installed and working
- No additional model downloads needed
- Fast local inference

#### Option B: Fix Local Model Path
Download all-MiniLM-L6-v2 GGUF and update path:

```json
"memorySearch": {
  "provider": "local",
  "local": {
    "modelPath": "C:\\Users\\Karen\\Models\\all-MiniLM-L6-v2\\model.gguf"
  }
}
```

**Note:** Requires `node-llama-cpp` which may need `pnpm approve-builds`.

#### Option C: Use Remote Provider
If local embedding fails, configure Gemini (free tier available):

```json
"memorySearch": {
  "provider": "gemini",
  "model": "gemini-embedding-001",
  "remote": {
    "apiKey": "${GEMINI_API_KEY}"
  }
}
```

### Immediate Action
```bash
# Edit config
openclaw config edit

# Set provider to ollama
# Restart gateway
openclaw gateway restart
```

---

## 2. Alternative Memory Architectures (Timeout Workarounds)

### Problem
Memory operations can be slow due to:
- Embedding generation
- SQLite vector search
- Large memory files

### Solutions

#### A. Disable Vector Search (Fallback to BM25)
If embeddings are problematic, disable vector search entirely:

```json
"memorySearch": {
  "provider": "none",
  "query": {
    "hybrid": {
      "enabled": false
    }
  }
}
```

**Result:** Falls back to BM25 keyword search (fast, no embeddings).

#### B. Use QMD Backend (Experimental but Robust)
QMD runs as a separate sidecar process with better async handling:

```json
"memory": {
  "backend": "qmd",
  "qmd": {
    "includeDefaultMemory": true,
    "update": {
      "interval": "5m",
      "debounceMs": 15000,
      "waitForBootSync": false
    },
    "limits": {
      "maxResults": 6,
      "timeoutMs": 4000
    }
  }
}
```

**Prerequisites:**
- Install QMD: `bun install -g https://github.com/tobi/qmd`
- SQLite with extensions: `brew install sqlite` (macOS) or use WSL2 on Windows

#### C. Reduce Memory Scope
Limit what gets indexed:

```json
"memorySearch": {
  "extraPaths": [],
  "experimental": {
    "sessionMemory": false
  }
}
```

---

## 3. Background/Async Processing

### Gateway Timeout Configuration
The 30-second timeout is likely the default HTTP timeout. Configure agent timeout:

```json
"agents": {
  "defaults": {
    "timeoutSeconds": 180
  }
}
```

**Note:** Already set to 180s in current config. If still timing out:

### Subagent Timeout Handling
For long-running memory operations, spawn subagents with extended timeouts:

```json
"agents": {
  "list": [
    {
      "id": "memory-worker",
      "name": "memory-worker",
      "model": "ollama/qwen2.5:7b",
      "timeoutSeconds": 300
    }
  ]
}
```

### Async Memory Updates
Configure memory to index asynchronously:

```json
"memorySearch": {
  "sync": {
    "watch": true,
    "debounceMs": 5000
  }
}
```

This prevents blocking on file changes.

---

## 4. AI Agent Memory Best Practices

### Architecture Patterns

#### Pattern 1: Tiered Memory (Recommended)
```
L1: Session Context (in-context learning)
L2: Daily Notes (memory/YYYY-MM-DD.md) - auto-loaded
L3: Long-term Memory (MEMORY.md) - curated
L4: Vector Search (semantic retrieval)
```

#### Pattern 2: Hybrid Search Strategy
```json
"memorySearch": {
  "query": {
    "hybrid": {
      "enabled": true,
      "vectorWeight": 0.7,
      "textWeight": 0.3,
      "mmr": {
        "enabled": true,
        "lambda": 0.7
      },
      "temporalDecay": {
        "enabled": true,
        "halfLifeDays": 30
      }
    }
  }
}
```

**Why:**
- Vector = semantic similarity ("Mac Studio" ≈ "the machine running the gateway")
- BM25 = exact tokens (IDs, error strings, code symbols)
- MMR = diversity (avoid duplicate results)
- Temporal decay = recency boost

#### Pattern 3: Embedding Caching
```json
"memorySearch": {
  "cache": {
    "enabled": true,
    "maxEntries": 50000
  }
}
```

Prevents re-embedding unchanged chunks.

### Operational Best Practices

1. **Pre-warm embeddings:** Run a test query after gateway start to trigger model load
2. **Monitor SQLite size:** Large `memory/<agentId>.sqlite` files slow down search
3. **Use temporal decay:** For agents with months of daily notes
4. **Limit maxResults:** Cap at 6-10 to reduce context bloat
5. **Disable in groups:** Memory search should be DM-only for privacy

### Configuration Summary (Recommended)

```json5
{
  agents: {
    defaults: {
      timeoutSeconds: 180,
      memorySearch: {
        // Use Ollama for embeddings
        provider: "ollama",
        ollama: {
          baseUrl: "http://localhost:11434",
          model: "nomic-embed-text"
        },
        // Hybrid search for best results
        query: {
          hybrid: {
            enabled: true,
            vectorWeight: 0.7,
            textWeight: 0.3
          }
        },
        // Cache embeddings
        cache: {
          enabled: true,
          maxEntries: 50000
        },
        // Async updates
        sync: {
          watch: true,
          debounceMs: 5000
        }
      }
    }
  }
}
```

---

## Quick Fix Checklist

- [ ] Change `memorySearch.provider` from `"local"` to `"ollama"`
- [ ] Remove or fix `local.modelPath` 
- [ ] Verify `ollama list` shows `nomic-embed-text`
- [ ] Restart gateway: `openclaw gateway restart`
- [ ] Test memory search: `openclaw agent --message "search memory for test"`
- [ ] If timeouts persist, increase `agents.defaults.timeoutSeconds` to 300
- [ ] If still failing, consider QMD backend or disable vector search

---

## References

- OpenClaw Memory Docs: https://docs.openclaw.ai/concepts/memory
- Configuration Reference: https://docs.openclaw.ai/gateway/configuration-reference
- QMD Backend: https://github.com/tobi/qmd
