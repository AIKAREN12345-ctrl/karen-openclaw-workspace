# Local AI Assistant Stack Requirements (2026)

**Research Date:** 2026-04-08  
**Goal:** Fully local AI assistant with zero cloud dependencies

---

## Current Inventory

### Ollama Models (8 installed)
| Model | Size | Purpose |
|-------|------|---------|
| gemma4:e4b | 9.6 GB | General purpose |
| qwen2.5:14b | 9.0 GB | Primary reasoning |
| llama3.1:8b | 4.9 GB | Tool calling |
| mistral:7b | 4.4 GB | General purpose |
| qwen3.5:latest | 6.6 GB | Latest Qwen |
| nomic-embed-text | 274 MB | **Embeddings** |
| qwen3.5:4b | 3.4 GB | Fast inference |
| qwen3.5:9b | 6.6 GB | Balanced |

### Python Packages
- CrewAI ✓
- ChromaDB ✓
- LangChain-Ollama ✓

---

## Complete Stack Requirements

### 1. Core LLM Runtime ✓
**Status:** Complete
- Ollama installed
- 8 models available
- Tool calling supported (llama3.1, qwen2.5, qwen3.5)

**Best Models for Tool Calling:**
- Llama 3.1 (native tool support)
- Qwen 2.5 (excellent tool adherence)
- Qwen 3.5 (latest, good balance)

---

### 2. Vector Database ✓
**Status:** Complete
- ChromaDB installed
- Alternative: Qdrant (better for production)
- Alternative: Milvus (enterprise scale)

**Recommendation:** ChromaDB is fine for single-user; Qdrant if scaling

---

### 3. Embedding Model ✓
**Status:** Complete
- nomic-embed-text installed (274 MB)
- Good for general embeddings
- Alternative: all-MiniLM-L6-v2

---

### 4. Memory System ⚠️ PARTIAL
**Status:** Needs implementation

**Options:**
1. **Mem0** - Most popular, 47.8K stars, +26% accuracy vs OpenAI memory
2. **Letta (MemGPT)** - Memory-first, stateful agents
3. **LocalRecall** - New 2026, fully local
4. **Momo** - Self-hosted in Rust

**Missing:** Memory layer integration with CrewAI

---

### 5. Web Search Alternative ❌ MISSING
**Status:** Not installed

**Options for Local Search:**
1. **SearXNG** - Metasearch, aggregates 250+ sources
2. **Perplexica** - AI-powered, open-source Perplexity alternative
3. **DuckDuckGo API** - Privacy-focused (still external)

**Recommendation:** SearXNG for true local-first

---

### 6. Document Processing ⚠️ PARTIAL
**Status:** Needs evaluation

**Requirements:**
- PDF parsing
- OCR for images
- Document chunking

**Options:**
1. **Unstructured.io** - Industry standard
2. **Marker** - PDF to markdown
3. **LlamaParse** - Local PDF parsing
4. **PyMuPDF** - Fast PDF extraction

**Missing:** Document ingestion pipeline

---

### 7. Speech/Voice (Optional) ❌ MISSING
**Status:** Not installed

**For Voice Assistant:**
- **STT:** Whisper (OpenAI) or whisper.cpp
- **TTS:** Piper (local), Kokoro TTS, LocalAI TTS
- **Wake Word:** Porcupine or openWakeWord

---

### 8. Multi-Agent Framework ✓
**Status:** Complete
- CrewAI installed
- LangChain-Ollama for Ollama integration

---

### 9. RAG Pipeline ⚠️ PARTIAL
**Status:** Components present, needs assembly

**Required:**
- Document loader ✓ (can use LangChain)
- Text splitter ✓ (LangChain)
- Embedding model ✓ (nomic-embed-text)
- Vector store ✓ (ChromaDB)
- Retriever ✓ (LangChain)

**Missing:** End-to-end RAG workflow

---

### 10. UI/Interface (Optional) ❌ MISSING
**Status:** Not installed

**Options:**
1. **Open WebUI** - Most popular, Ollama native
2. **LobeChat** - Modern, plugin support
3. **Text Generation WebUI** - Feature-rich
4. **Custom** - Build with Streamlit/Gradio

---

## Missing Components Summary

| Component | Priority | Options |
|-----------|----------|---------|
| Memory System | HIGH | Mem0, Letta, LocalRecall |
| Web Search | HIGH | SearXNG, Perplexica |
| Document Processing | MEDIUM | Unstructured.io, Marker |
| RAG Pipeline | MEDIUM | Assemble from existing parts |
| UI Interface | LOW | Open WebUI, LobeChat |
| Speech (STT/TTS) | LOW | Whisper, Piper |

---

## Recommended Next Steps

### Phase 1: Core Functionality (High Priority)
1. **Install Mem0** for persistent memory
   ```bash
   pip install mem0ai
   ```

2. **Set up SearXNG** for local web search
   ```bash
   docker run -d --name searxng -p 8080:8080 searxng/searxng
   ```

3. **Install Unstructured** for document processing
   ```bash
   pip install unstructured
   ```

### Phase 2: RAG Pipeline
1. Build document ingestion workflow
2. Connect ChromaDB + nomic-embed-text
3. Create retrieval-augmented generation flow

### Phase 3: Polish (Optional)
1. Install Open WebUI for chat interface
2. Add Whisper + Piper for voice
3. Fine-tune agent behavior

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│         (Open WebUI / CLI / Voice)                      │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                   AGENT ORCHESTRATOR                     │
│                    (CrewAI / LangChain)                  │
└─────────────────────────────────────────────────────────┘
                           │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│     LLM      │  │    MEMORY    │  │     RAG      │
│   (Ollama)   │  │    (Mem0)    │  │  (ChromaDB)  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Tool Calling│  │  Long-term   │  │  Document    │
│  (Functions) │  │  Persistence │  │  Store       │
└──────────────┘  └──────────────┘  └──────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                    TOOLS / SERVICES                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │Web Search│ │ Doc Proc │ │  Speech  │ │ Calendar │   │
│  │(SearXNG) │ │(Unstruct)│ │(Whisper) │ │ (Local)  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Resources

- [Self-Hosted AI Agents 2026 Guide](https://doneclaw.com/blog/self-hosted-ai-agent-2026/)
- [CrewAI Local Setup Guide](https://localaimaster.com/blog/crewai-local-setup-guide)
- [Mem0 Documentation](https://docs.mem0.ai/)
- [SearXNG Documentation](https://docs.searxng.org/)
- [Unstructured.io Docs](https://docs.unstructured.io/)

---

*Research compiled: 2026-04-08*
