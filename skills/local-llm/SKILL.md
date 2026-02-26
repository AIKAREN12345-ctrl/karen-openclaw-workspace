---
name: local-llm
description: Run local LLM inference via Ollama on the node. Optimized for Windows 11 with qwen2.5:7b.
metadata:
  openclaw:
    requires:
      bins: ["ollama"]
      node: true
    tags: ["ollama", "local", "llm", "windows"]
    author: "Karen"
    version: "1.0.0"
---

# Local LLM Skill

Run local language models via Ollama on the paired node. Designed for Windows 11 with optimized defaults.

## Capabilities

- **Primary Model:** qwen2.5:7b (4.7GB, excellent tool support)
- **Fallback Models:** llama3.2:8b, phi3:mini
- **JSON Mode:** Structured outputs for tool calling
- **Performance:** Metrics tracking (tokens/sec, duration)

## Usage

### Basic Generation
```
/skill local-llm generate "Explain quantum computing simply"
```

### With Specific Model
```
/skill local-llm generate "Write a poem" --model llama3.2:8b
```

### JSON Mode (Structured Output)
```
/skill local-llm generate "List 3 colors" --format json
```

### Check Status
```
/skill local-llm status
```

## Configuration

The skill uses the node to execute Ollama commands. Ensure:
1. Ollama is installed and running on localhost:11434
2. Node is paired and connected
3. Required models are pulled (`ollama pull qwen2.5:7b`)

## Windows 11 Optimizations

- Uses `nodes run` for sandbox bypass (verified working)
- PowerShell-compatible command execution
- Handles Windows path conventions
- Optimized for 16GB RAM systems

## Performance Notes

Based on research:
- qwen2.5:7b: ~4.7GB RAM, best tool support
- Context window: Large recommended (not small)
- First load slower (model loading), subsequent calls faster
- Use `--keep-alive` for sustained sessions

## Troubleshooting

**"Cannot connect to Ollama"**
- Check Ollama is running: `Get-Process ollama`
- Verify port 11434: `python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:11434').status)"`

**"Model not found"**
- Pull model first: `ollama pull qwen2.5:7b`

**"Out of memory"**
- Use smaller model: `--model phi3:mini` (2.2GB)
- Close other applications
- Consider `keep_alive: 0` to unload after each call

## Examples

### Heartbeat Automation
```json
{
  "name": "local-heartbeat",
  "schedule": "0 * * * *",
  "session": "main",
  "agent": "main",
  "skill": "local-llm",
  "args": ["generate", "System status check - report any issues concisely"]
}
```

### Git Commit Message Generator
```
/skill local-llm generate "Write a git commit message for these changes: {{changes}}" --format json --schema '{"type": "object", "properties": {"message": {"type": "string"}}}'
```

## Research Backing

This skill is based on extensive research:
- Reddit r/ollama: Community confirms qwen2.5:7b best for tool calling
- Reddit r/openclaw: Node-based Ollama access is the working pattern
- Ollama API docs: JSON mode for structured outputs
- Windows 11 native: No WSL required

## Version History

- 1.0.0: Initial release with qwen2.5:7b support, Windows 11 optimized
