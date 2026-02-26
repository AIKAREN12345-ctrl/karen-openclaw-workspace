# Optimized Local LLM Configuration for 24GB RAM
# Strategy: Load/unload models per task, keep only what's needed

# Model Tiers (RAM usage):
# - gemma:2b     ~1.7GB  (light tasks, quick responses)
# - phi3:mini    ~2.2GB  (general automation)
# - llama3.2:3b  ~2.0GB  (tool calling - currently broken)
# - qwen2.5:7b   ~4.7GB  (complex tasks, best tool support)

# Recommended Usage Pattern:
# 1. Light automation (status checks, logging): gemma:2b or phi3:mini
# 2. Complex reasoning: qwen2.5:7b (unload after use)
# 3. Never keep multiple models loaded simultaneously

# Cron Job Optimization:
# - Use smaller models for frequent tasks
# - Use qwen2.5:7b only for complex hourly tasks
# - Set keep_alive: 0 to unload immediately after use

# Current Setup:
# - hourly-memory-log: Kimi (cloud, 0 RAM)
# - local-llm-hourly: qwen2.5:7b (4.7GB during run, then unload)
# - karen-heartbeat: Kimi (cloud, 0 RAM)

# RAM Budget (24GB total):
# - Windows 11 + OpenClaw: ~6GB
# - Ollama (when active): ~5GB
# - Free for other tasks: ~13GB
# - Safety buffer: ~3GB

# Future Optimization Ideas:
# 1. Use gemma:2b for all cron jobs (saves 3GB per job)
# 2. Only load qwen2.5:7b on-demand for complex tasks
# 3. Consider phi3:mini as daily driver (2.2GB, good balance)
# 4. Monitor RAM with: Get-Process ollama | Select-Object WorkingSet

# Command to check current Ollama RAM usage:
# Get-Process ollama | Select-Object Name, @{N='RAM_MB';E={[math]::Round($_.WorkingSet/1MB,2)}}
