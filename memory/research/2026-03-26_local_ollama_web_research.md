# Research: Local Ollama Models with Web Access

## Current Situation (March 26, 2026)

**Problem:** Ollama subagents timeout due to OpenClaw auth bug (GitHub #43945)
- Native Ollama works for interactive chat
- Subagents cannot use Ollama (sandbox isolation issue)
- Research automation currently uses Kimi K2.5 (API costs)

**Goal:** Enable local Ollama models to perform web_fetch operations without API costs

---

## Potential Solutions

### Option 1: Wait for OpenClaw Fix (Official)
**Status:** OpenClaw team aware of issue (GitHub #43945)
**Timeline:** Unknown
**Pros:** Cleanest solution, no workarounds needed
**Cons:** No control over timeline, continuing API costs

---

### Option 2: Direct Ollama Integration (No Subagents)
**Architecture:** Run research directly in main session with Ollama

**Implementation:**
```python
# Instead of spawning subagent:
# Use native Ollama in main session for research tasks

# Flow:
1. Cron triggers main session
2. Main session switches to Ollama model
3. Execute web_fetch + research
4. Switch back to Kimi for chat
```

**Pros:**
- Zero API costs for research
- Uses existing Ollama setup
- No sandbox issues

**Cons:**
- Blocks main session during research
- Cannot parallelize tasks
- More complex session management

**Feasibility:** HIGH - Can implement today

---

### Option 3: Separate Research Service
**Architecture:** Standalone Python service that uses Ollama directly

**Implementation:**
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  OpenClaw Cron  │────▶│ Research Service │────▶│   Ollama    │
│   (triggers)    │     │  (Python/Flask)  │     │  (local)    │
└─────────────────┘     └──────────────────┘     └─────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │  web_fetch  │
                        │  DuckDuckGo │
                        └─────────────┘
```

**Components:**
1. **Research Service** - Flask/FastAPI app running locally
2. **Ollama Integration** - Direct API calls to localhost:11434
3. **Web Fetch** - Python requests + BeautifulSoup
4. **Storage** - Save results to memory/research/

**Pros:**
- Fully local, zero API costs
- No OpenClaw subagent limitations
- Can parallelize research tasks
- Independent of OpenClaw updates

**Cons:**
- More infrastructure to maintain
- Need to build web scraping logic
- Separate authentication/monitoring

**Feasibility:** MEDIUM - Requires development effort

---

### Option 4: Browser Automation Bridge
**Architecture:** Use browser automation to feed web content to Ollama

**Implementation:**
```
OpenClaw ──▶ Browser (CDP) ──▶ Web Content ──▶ Ollama (local)
                (port 18800)      (extracted)      (process)
```

**Tools:**
- Playwright or Selenium for browser control
- Ollama API for local processing
- Custom bridge script

**Pros:**
- Uses existing browser setup
- Can handle JavaScript-heavy sites
- Visual verification possible

**Cons:**
- Complex to build
- Slower than direct HTTP
- Resource intensive

**Feasibility:** LOW - Overly complex for this use case

---

### Option 5: Docker Network Solution
**Architecture:** Run Ollama in Docker on same network as OpenClaw subagents

**Implementation:**
```yaml
# docker-compose.yml
version: '3'
services:
  ollama:
    image: ollama/ollama
    networks:
      - openclaw-network
    volumes:
      - ollama:/root/.ollama
    
  openclaw-subagent:
    network_mode: service:ollama  # Share network
```

**Pros:**
- Subagents can reach Ollama
- No auth issues
- Isolated environment

**Cons:**
- GPU passthrough complex on Windows
- AMD GPU support limited
- Overkill for this problem

**Feasibility:** LOW - Too complex, GPU issues

---

## Recommended Approach

### Phase 1: Direct Ollama in Main Session (Immediate)
**Quick win:** Modify HEARTBEAT.md to run research in main session

**Changes:**
1. Cron jobs trigger main session instead of subagents
2. Main session temporarily switches to Ollama
3. Executes research with web_fetch
4. Returns to Kimi

**Code pattern:**
```python
# In main session handler
if research_triggered:
    # Switch to Ollama
    /model ollama/qwen2.5:7b
    
    # Execute research
    web_fetch(urls...)
    analyze_with_ollama()
    save_results()
    
    # Switch back
    /model kimi-coding/k2p5
```

**Timeline:** Can implement today
**Cost:** Zero API for research

---

### Phase 2: Research Service (Long-term)
**Build standalone service for better architecture**

**Timeline:** 1-2 weeks development
**Benefits:** Fully independent, parallel processing

---

## Technical Considerations

### web_fetch Alternative
Since DuckDuckGo blocks bots, alternatives:
1. **SearXNG** - Self-hosted metasearch engine
2. **Brave Search API** - Has free tier
3. **Google Custom Search** - Requires API key
4. **Direct site fetching** - If URLs known

### Ollama Model Selection for Research
| Model | Size | Speed | Quality | VRAM Needed |
|-------|------|-------|---------|-------------|
| qwen2.5:7b | 4.7GB | Fast | Good | 4GB |
| qwen2.5:14b | 9.0GB | Medium | Better | 6GB |
| llama3.2:3b | 2.0GB | Very Fast | Basic | 2GB |

**Recommendation:** qwen2.5:7b for research (good balance)

---

## Implementation Plan

### Immediate (Today)
1. Test direct Ollama research in main session
2. Modify one cron job to use main session
3. Verify web_fetch works with Ollama

### Short-term (This Week)
1. Update HEARTBEAT.md with new approach
2. Migrate all research triggers
3. Monitor API cost savings

### Long-term (If Needed)
1. Build standalone research service
2. Add parallel processing
3. Implement self-hosted search

---

## Cost Analysis

| Approach | Daily Cost | Monthly Cost | Setup Effort |
|----------|-----------|--------------|--------------|
| Current (Kimi) | ~$0.50 | ~$15 | None |
| Direct Ollama | $0 | $0 | Low |
| Research Service | $0 | $0 | Medium |

**Potential Savings:** $15/month

---

## Conclusion

**Best immediate option:** Direct Ollama in main session
- Zero additional infrastructure
- Can implement today
- Proven to work (tested this morning)

**Best long-term option:** Standalone research service
- Cleanest architecture
- No OpenClaw limitations
- Full control over execution

**Recommendation:** Start with Phase 1 (direct Ollama), migrate to Phase 2 (service) if needed.

