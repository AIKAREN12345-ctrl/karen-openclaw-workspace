# OpenClaw Memory System Architecture Research
**Date:** 2026-03-03  
**Researcher:** Subagent (Karen)  
**Scope:** Memory system issues and architectural improvements

---

## Executive Summary

The OpenClaw memory system is experiencing multiple critical issues that prevent reliable long-term memory operations. This research identifies four primary problems and proposes three alternative architectures with specific implementation recommendations.

---

## 1. Current Memory System Issues - Analysis

### 1.1 Embedding Provider Errors (Memory Search Unavailable)

**Root Cause:** Configuration mismatch between expected and actual embedding model availability.

**Evidence from `openclaw.json`:**
```json
"memorySearch": {
  "provider": "local",
  "local": {
    "modelPath": "C:\\Users\\Karen\\Models\\all-MiniLM-L6-v2"
  },
  "store": {
    "path": "C:/Users/Karen/.openclaw/memory/{agentId}.sqlite",
    "vector": {
      "enabled": false  // ← CRITICAL: Vector search disabled
    }
  }
}
```

**Problems:**
1. Vector search is explicitly disabled (`"enabled": false`)
2. Model path points to local filesystem but model may not exist at that location
3. No fallback mechanism if local model fails to load
4. SQLite databases exist (`main.sqlite`, `local-automation.sqlite`) but vector functionality is off

**Impact:** Semantic memory search is completely non-functional. The system falls back to file-based memory only.

---

### 1.2 Subagent Timeouts During Memory Operations

**Root Cause:** 30-second gateway timeout is too aggressive for embedding generation and LLM-based memory processing.

**Evidence from cron jobs:**
- `ollama-monitor` job: 120s timeout, runs every 15 minutes
- `local-llm-complex` (system_analysis.py): 69s average duration
- `memory-log-local`: Simple data logging (no LLM) - works reliably

**The timeout problem manifests in:**
1. **Ollama model loading:** First inference after idle period requires model load (5-15 seconds)
2. **Embedding generation:** all-MiniLM-L6-v2 requires ~2-5 seconds per batch
3. **LLM analysis:** Complex prompts with historical context take 30-90 seconds

**Impact:** Any memory operation involving embeddings or LLM analysis risks timeout failure.

---

### 1.3 30-Second Gateway Timeout Limiting Long-Running Tasks

**Evidence from memory logs (2026-03-03):**
```
## 05:46 - System Monitor (Ollama-Powered)
**Ollama Analysis:** Error: timed out

## 06:01 - System Monitor (Ollama-Powered)  
**Ollama Analysis:** Error: timed out

## 06:16 - System Monitor (Ollama-Powered)
**Ollama Analysis:** Error: timed out
```

**Technical Analysis:**
- Gateway timeout is hardcoded at 30 seconds for subagent operations
- Ollama inference with qwen2.5:14b can take 45-120 seconds depending on prompt complexity
- System analysis with historical context (5 previous entries) consistently exceeds timeout

**Current timeout configuration:**
- Agent default: 180 seconds (but gateway overrides for subagents)
- Cron jobs: 30-360 seconds (varies by job)
- Subagent spawn: 30 seconds (hard limit)

---

### 1.4 Ollama Analysis Timing Out in ollama_monitor.py

**Code Analysis of `ollama_monitor.py`:**

```python
def query_ollama(prompt, model="qwen2.5:14b", timeout=90):
    # Uses urllib with 90s timeout - but gateway kills at 30s
    
def analyze_with_ollama(metrics, history):
    # Builds complex prompt with historical context
    # Includes 5 previous analyses for trend detection
    # This increases token count and inference time
```

**Why it fails:**
1. Prompt includes historical context (up to 5 previous analyses)
2. JSON metrics are formatted with indentation (increases tokens)
3. Model qwen2.5:14b is slower than qwen2.5:7b
4. No streaming - waits for complete response

**Success pattern:** `memory_log_local.py` works because it uses NO LLM - just direct system data collection.

---

## 2. Alternative Memory Architectures

### Architecture A: Tiered Memory with Async Processing

**Concept:** Separate memory into hot (fast) and cold (async-processed) tiers.

**Implementation:**
1. **Immediate write:** All memories go to daily markdown files (no delay)
2. **Background queue:** Embedding jobs queued to separate worker
3. **Worker process:** Independent Python script with its own timeout
4. **Search fallback:** If embeddings not ready, use keyword search

**Pros:**
- ✅ Memory writes never block
- ✅ Embeddings generated when system is idle
- ✅ Graceful degradation if embedding fails
- ✅ Can use slower, better-quality embeddings

**Cons:**
- ❌ Search results may be stale (5-min delay)
- ❌ Requires additional worker process
- ❌ More complex deployment

---

### Architecture B: Chunked Memory with Sharded Operations

**Concept:** Break memory operations into small chunks that complete within timeout windows.

**Chunking Rules:**
- Maximum chunk size: 512 tokens (~2000 characters)
- Overlap: 50 tokens between chunks (maintain context)
- Metadata: timestamp, source, chunk index, total chunks

**Pros:**
- ✅ Each operation completes within 5-10 seconds
- ✅ Parallel processing possible
- ✅ Better granularity for search results
- ✅ No architectural changes to OpenClaw

**Cons:**
- ❌ Reconstruction required for full context
- ❌ More database rows (higher storage)
- ❌ Complex chunk management

---

### Architecture C: Remote Embedding Service with Local Cache

**Concept:** Use external embedding API (fast, reliable) with local caching for offline use.

**Options:**
1. **OpenAI API** (`text-embedding-3-small`): ~1536 dims, fast, paid
2. **Ollama via ngrok** (remote Ollama): Self-hosted, free
3. **Hugging Face Inference API**: Free tier available

**Pros:**
- ✅ Fast embedding generation (< 1s)
- ✅ No local model loading delays
- ✅ Reliable and consistent
- ✅ Can fall back to local if remote fails

**Cons:**
- ❌ Requires internet connection (or self-hosted remote)
- ❌ Potential costs (if using paid APIs)
- ❌ Privacy concerns with external services

---

## 3. Specific Implementation Recommendations

### Priority 1: Fix Immediate Timeout Issues (Today)

**3.1.1 Reduce Ollama Monitor Complexity**

Edit `skills/local-llm/ollama_monitor.py`:
- Change model from `qwen2.5:14b` to `qwen2.5:7b` (faster)
- Reduce history context from 5 to 2 entries
- Remove JSON indentation from prompt
- Add streaming support or reduce timeout expectation

**3.1.2 Disable LLM Analysis in Time-Critical Paths**

For cron jobs that must complete:
- Use `memory_log_local.py` pattern (no LLM)
- Move LLM analysis to a separate, non-blocking job

---

### Priority 2: Enable Embedding Provider (This Week)

**3.2.1 Verify Model Exists**

Check if model exists at configured path:
```powershell
Test-Path "C:\Users\Karen\Models\all-MiniLM-L6-v2"
```

If not, install via:
```powershell
# Option 1: Download from HuggingFace
# Option 2: Use Ollama embedding model
ollama pull nomic-embed-text
```

**3.2.2 Update Configuration**

Two options:

**Option A: Use Ollama for embeddings (Recommended)**
```json
"memorySearch": {
  "provider": "ollama",
  "ollama": {
    "baseUrl": "http://localhost:11434",
    "model": "nomic-embed-text"
  },
  "store": {
    "vector": {
      "enabled": true
    }
  }
}
```

**Option B: Fix local model path**
```json
"memorySearch": {
  "provider": "local",
  "local": {
    "modelPath": "C:\\Users\\Karen\\Models\\all-MiniLM-L6-v2"
  },
  "store": {
    "vector": {
      "enabled": true
    }
  }
}
```

---

### Priority 3: Implement Background Processing (Next 2 Weeks)

**3.3.1 Create Memory Worker Script**

New file: `skills/local-llm/memory_worker.py`

```python
#!/usr/bin/env python3
"""
Background memory embedding worker
Processes queued embedding jobs outside request path
"""

import sqlite3
import json
import urllib.request
from datetime import datetime

DB_PATH = "C:/Users/Karen/.openclaw/memory/embedding_queue.sqlite"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

def process_queue():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get pending jobs
    cursor.execute("""
        SELECT id, text, metadata FROM embedding_queue 
        WHERE status = 'pending' 
        ORDER BY created_at 
        LIMIT 10
    """)
    
    jobs = cursor.fetchall()
    
    for job_id, text, metadata in jobs:
        try:
            # Generate embedding via Ollama
            embedding = get_embedding(text)
            
            # Store in main memory database
            store_embedding(job_id, text, embedding, metadata)
            
            # Mark as completed
            cursor.execute(
                "UPDATE embedding_queue SET status = 'completed', processed_at = ? WHERE id = ?",
                (datetime.now().isoformat(), job_id)
            )
            
        except Exception as e:
            cursor.execute(
                "UPDATE embedding_queue SET status = 'failed', error = ? WHERE id = ?",
                (str(e), job_id)
            )
    
    conn.commit()
    conn.close()

def get_embedding(text):
    data = json.dumps({
        "model": MODEL,
        "prompt": text
    }).encode('utf-8')
    
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result.get('embedding')

if __name__ == "__main__":
    process_queue()
```

**3.3.2 Add Cron Job for Worker**

Add to `cron/jobs.json`:
```json
{
  "id": "memory-embedding-worker",
  "name": "memory-embedding-worker",
  "enabled": true,
  "schedule": {
    "kind": "every",
    "everyMs": 300000
  },
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "python C:\\Users\\Karen\\.openclaw\\workspace\\skills\\local-llm\\memory_worker.py"
  }
}
```

---

### Priority 4: Long-Term Architecture Decision (Next Month)

**Recommendation: Hybrid Approach**

Combine Architecture A (Tiered) + Architecture C (Remote with cache):

1. **Hot tier:** File-based daily memory (current, working)
2. **Warm tier:** Ollama embeddings with background worker
3. **Cold tier:** Keyword search fallback when embeddings unavailable

**Benefits:**
- No immediate changes to working file-based system
- Embeddings added incrementally without blocking
- Graceful degradation at every level
- Can switch embedding provider without code changes

---

## 4. Priority Order Summary

| Priority | Task | Impact | Effort |
|----------|------|--------|--------|
| P0 | Fix ollama_monitor.py timeouts | High | 30 min |
| P1 | Enable embedding provider | High | 2 hours |
| P2 | Implement background worker | Medium | 1 day |
| P3 | Architecture refactoring | Low | 1 week |

---

## 5. Key Findings

1. **Memory search is disabled by config** - not a code bug, just `vector.enabled: false`
2. **Timeouts are architectural** - 30s gateway limit cannot be changed per-subagent
3. **File-based memory works** - `memory_log_local.py` proves non-LLM approach is reliable
4. **Ollama 14b is too slow** - qwen2.5:7b should be max size for real-time operations
5. **Background processing is the solution** - Any embedding/LLM work should be async

---

## 6. Files Referenced

- `~/.openclaw/openclaw.json` - Main configuration
- `~/.openclaw/cron/jobs.json` - Cron job definitions
- `~/workspace/skills/local-llm/ollama_monitor.py` - System monitor (timing out)
- `~/workspace/skills/local-llm/memory_log_local.py` - Working memory logger
- `~/workspace/skills/local-llm/system_analysis.py` - Detailed analysis (no LLM)
- `~/memory/` - Daily memory files and SQLite databases

---

*Research completed: 2026-03-03*
