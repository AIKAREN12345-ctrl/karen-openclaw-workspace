#!/usr/bin/env python3
"""
Local LLM Skill Implementation
Handles Ollama integration via node execution
"""

import json
import sys
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

# Configuration
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
DEFAULT_MODEL = "qwen2.5:3b"
FALLBACK_MODELS = ["llama3.2:8b", "phi3:mini", "gemma:2b"]

def ollama_generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    format_mode: Optional[str] = None,
    stream: bool = False,
    keep_alive: str = "0",
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate text using Ollama API
    
    Args:
        prompt: The prompt to generate from
        model: Model name (default: qwen2.5:7b)
        format_mode: "json" for JSON mode, or JSON schema dict
        stream: Whether to stream response
        keep_alive: How long to keep model loaded (default "0" = unload immediately)
        options: Additional model options (temperature, etc.)
    
    Returns:
        Dict with response and metadata
    """
    url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "keep_alive": keep_alive
    }
    
    if format_mode:
        if format_mode == "json":
            payload["format"] = "json"
        else:
            payload["format"] = format_mode
    
    if options:
        payload["options"] = options
    
    data = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return {
                "success": True,
                "response": result.get('response', ''),
                "model": result.get('model', model),
                "total_duration": result.get('total_duration', 0),
                "load_duration": result.get('load_duration', 0),
                "prompt_eval_count": result.get('prompt_eval_count', 0),
                "eval_count": result.get('eval_count', 0),
                "done": result.get('done', False)
            }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP Error {e.code}: {e.reason}",
            "details": e.read().decode('utf-8')
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"Connection failed: {e.reason}",
            "hint": "Is Ollama running? Check: Get-Process ollama"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def ollama_list_models() -> Dict[str, Any]:
    """List available Ollama models"""
    url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return {
                "success": True,
                "models": [m['name'] for m in result.get('models', [])]
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def ollama_status() -> Dict[str, Any]:
    """Check Ollama server status"""
    try:
        # Try to list models as a health check
        result = ollama_list_models()
        if result["success"]:
            return {
                "success": True,
                "status": "running",
                "host": f"{OLLAMA_HOST}:{OLLAMA_PORT}",
                "available_models": result["models"],
                "default_model": DEFAULT_MODEL,
                "recommended": [m for m in result["models"] if m in [DEFAULT_MODEL] + FALLBACK_MODELS]
            }
        else:
            return {
                "success": False,
                "status": "error",
                "error": result.get("error", "Unknown error")
            }
    except Exception as e:
        return {
            "success": False,
            "status": "unreachable",
            "error": str(e)
        }

def format_output(result: Dict[str, Any], verbose: bool = False) -> str:
    """Format the output for display"""
    if not result.get("success"):
        error_msg = f"Error: {result.get('error', 'Unknown error')}"
        if "hint" in result:
            error_msg += f"\nHint: {result['hint']}"
        return error_msg
    
    output = []
    output.append(result.get('response', ''))
    
    if verbose and "eval_count" in result:
        # Calculate tokens per second
        total_duration = result.get('total_duration', 1)
        eval_count = result.get('eval_count', 0)
        tps = (eval_count / total_duration) * 1e9 if total_duration > 0 else 0
        
        output.append(f"\nStats: {eval_count} tokens @ {tps:.1f} tok/s")
        output.append(f"Load: {result.get('load_duration', 0)/1e9:.2f}s")
    
    return "\n".join(output)

def main():
    """Main entry point for skill execution"""
    if len(sys.argv) < 2:
        print("Usage: local-llm <command> [args]")
        print("Commands: generate, status, list")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        result = ollama_status()
        if result["success"]:
            print(f"[OK] Ollama is running on {result['host']}")
            print(f"Available models: {', '.join(result['available_models'])}")
            print(f"Recommended: {', '.join(result['recommended'])}")
        else:
            print(f"[ERROR] {result.get('error', 'Ollama not reachable')}")
    
    elif command == "list":
        result = ollama_list_models()
        if result["success"]:
            print("Available models:")
            for model in result["models"]:
                marker = "*" if model in [DEFAULT_MODEL] + FALLBACK_MODELS else "  "
                print(f"  {marker} {model}")
        else:
            print(f"[ERROR] {result.get('error', 'Failed to list models')}")
    
    elif command == "generate":
        if len(sys.argv) < 3:
            print("Usage: local-llm generate <prompt> [--model <model>] [--format json]")
            sys.exit(1)
        
        prompt = sys.argv[2]
        model = DEFAULT_MODEL
        format_mode = None
        verbose = False
        
        # Parse optional args
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--model" and i + 1 < len(sys.argv):
                model = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--format" and i + 1 < len(sys.argv):
                format_mode = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--verbose":
                verbose = True
                i += 1
            else:
                i += 1
        
        result = ollama_generate(prompt, model=model, format_mode=format_mode)
        print(format_output(result, verbose=verbose))
    
    else:
        print(f"Unknown command: {command}")
        print("Commands: generate, status, list")
        sys.exit(1)

if __name__ == "__main__":
    main()
