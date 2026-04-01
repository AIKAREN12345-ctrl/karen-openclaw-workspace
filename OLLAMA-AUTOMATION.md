# Ollama Automation Setup

## Overview
Ollama with Qwen 3.5 is configured for:
- Automated research (via cron jobs)
- Memory embeddings (nomic-embed-text)
- Local LLM fallback

## Current Status

### ✅ Working:
- Ollama keepalive (hourly)
- Pre-warm jobs (5x daily)
- Memory embeddings
- Manual subagent spawning

### ❌ Needs Setup:
- Automated research jobs need handlers

## Research Topics

### 1. OpenClaw Updates (6:00 AM)
```bash
python ollama_research.py openclaw
```

### 2. AI Models (12:00 PM, 6:00 PM)
```bash
python ollama_research.py ai_models
```

### 3. Philosophy (8:00 PM)
```bash
python ollama_research.py philosophy
```

### 4. AI Income (10:00 PM)
```bash
python ollama_research.py income
```

## Manual Usage

To run research manually:
```bash
cd ~/.openclaw/workspace
python ollama_research.py ai_models
```

## Models Available

| Model | Size | Purpose |
|-------|------|---------|
| qwen3.5:9b | 6.6 GB | Main chat/research |
| qwen3.5:4b | 3.4 GB | Lightweight option |
| nomic-embed-text | 274 MB | Embeddings |

## Cron Jobs

Current cron jobs (check with: openclaw cron list):
- ollama-keepalive (hourly)
- 5x prewarm jobs (before research)
- github-backup (daily 2am)
- memory-hourly (every 3h)

## Next Steps

To enable automated research, we need to either:
1. Add system event handlers for TRIGGER-RESEARCH-* events
2. Change cron jobs to execute commands instead of system events
3. Use a different automation approach

Recommended: Option 2 - change cron jobs to execute the research script directly.
