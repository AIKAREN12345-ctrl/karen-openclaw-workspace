# COMPLETE LOCAL OPENCLAW SETUP GUIDE
## Fully Local AI Agent on 20GB RAM Windows 11 (AMD Ryzen, No GPU)

**Date:** 2026-04-15  
**Target System:** Windows 11, AMD Ryzen CPU, 20GB RAM, No Dedicated GPU  
**Goal:** Zero-cloud-dependencies, fully private AI agent setup

---

## Table of Contents

1. [Prerequisites & Hardware Assessment](#1-prerequisites--hardware-assessment)
2. [Windows 11 Optimizations for Local LLMs](#2-windows-11-optimizations-for-local-llms)
3. [OpenClaw Installation (No Cloud Dependencies)](#3-openclaw-installation-no-cloud-dependencies)
4. [Ollama Setup & Configuration](#4-ollama-setup--configuration)
5. [BitNet 1.58 Integration for Maximum Efficiency](#5-bitnet-158-integration-for-maximum-efficiency)
6. [Model Selection for 20GB RAM Systems](#6-model-selection-for-20gb-ram-systems)
7. [TurboQuant & Speculative Decoding Setup](#7-turboquant--speculative-decoding-setup)
8. [llama.cpp CPU Optimization](#8-llamacpp-cpu-optimization)
9. [Performance Tuning for CPU-Only Inference](#9-performance-tuning-for-cpu-only-inference)
10. [Fallback Strategies](#10-fallback-strategies)
11. [Troubleshooting Common Issues](#11-troubleshooting-common-issues)
12. [Quick Reference Commands](#12-quick-reference-commands)

---

## 1. Prerequisites & Hardware Assessment

### Minimum Requirements for This Guide

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | AMD Ryzen 5 (6-core) | AMD Ryzen 7/9 (8+ cores) |
| **RAM** | 16GB | 20GB+ (you have 20GB ✓) |
| **Storage** | 50GB free (SSD) | 100GB+ NVMe SSD |
| **OS** | Windows 11 22H2+ | Windows 11 24H2 |
| **GPU** | None required | Integrated AMD graphics acceptable |

### Your System Profile
- **Platform:** Windows 11 on AMD Ryzen
- **RAM:** 20GB (Good for 8B-14B models with quantization)
- **GPU:** None (CPU-only inference required)
- **Target:** Fully local, no API calls

### Pre-Installation Checklist

```powershell
# Run these in PowerShell as Administrator to check your system

# 1. Check Windows version (must be 22H2 or later)
winver

# 2. Check available RAM
systeminfo | findstr "Total Physical Memory"

# 3. Check CPU info
wmic cpu get Name,NumberOfCores,NumberOfLogicalProcessors

# 4. Check free disk space
Get-PSDrive C | Select-Object Used,Free

# 5. Check if WSL2 is installed (optional but recommended)
wsl --version

# 6. Check PowerShell version ($PSVersionTable.PSVersion.Major must be 7+)
$PSVersionTable.PSVersion
```

**⚠️ CRITICAL:** If PowerShell version is below 7, install it first:
```powershell
winget install Microsoft.PowerShell
```

---

## 2. Windows 11 Optimizations for Local LLMs

### 2.1 Disable Memory Compression (Critical for LLM Performance)

Windows 11 memory compression can significantly slow down LLM inference:

```powershell
# Run as Administrator
# Disable memory compression
Disable-MMAgent -mc

# Verify it's disabled
Get-MMAgent | Select-Object MemoryCompression
```

### 2.2 Configure Virtual Memory (Pagefile)

With 20GB RAM, set a fixed pagefile to prevent dynamic resizing overhead:

```powershell
# Run as Administrator
# Disable automatic management
$computer = Get-WmiObject -Class Win32_ComputerSystem
$computer.AutomaticManagedPagefile = $false
$computer.Put()

# Set custom pagefile (16GB on fast drive)
$pagefile = Get-WmiObject -Class Win32_PageFileSetting
$pagefile.InitialSize = 16384  # 16GB initial
$pagefile.MaximumSize = 16384  # 16GB max (fixed)
$pagefile.Put()

# Restart required
Restart-Computer
```

### 2.3 Optimize Power Settings for Performance

```powershell
# Set high performance power plan
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Disable CPU throttling (if on desktop)
powercfg -attributes SUB_PROCESSOR 5d76a2ca-e8c0-402f-a133-2158492d58ad -ATTRIB_HIDE
```

### 2.4 Windows Security Exclusions (Optional but Recommended)

Add exclusions to Windows Defender for LLM folders to prevent scanning overhead:

```powershell
# Run as Administrator
# Add exclusion for Ollama
Add-MpPreference -ExclusionPath "$env:USERPROFILE\.ollama"

# Add exclusion for OpenClaw workspace
Add-MpPreference -ExclusionPath "$env:USERPROFILE\.openclaw"

# Add exclusion for model storage (if using custom location)
Add-MpPreference -ExclusionPath "C:\Models"
```

### 2.5 Disable Unnecessary Background Apps

```powershell
# Disable background apps
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" -Name "GlobalUserDisabled" -Value 1

# Disable Game Mode (can interfere with CPU scheduling)
Set-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "AllowAutoGameMode" -Value 0
```

### 2.6 AMD-Specific Optimizations

```powershell
# Enable high-performance mode for AMD CPUs (if available)
# Check if AMD Ryzen Master is installed
if (Test-Path "C:\Program Files\AMD\RyzenMaster\") {
    Write-Host "AMD Ryzen Master detected - consider using it for CPU tuning"
}

# Set process priority for background tasks
# This will be done per-process when running Ollama
```

---

## 3. OpenClaw Installation (No Cloud Dependencies)

### 3.1 Method 1: Local Prefix Installer (RECOMMENDED for Fully Local Setup)

This method keeps everything local without requiring system-wide Node.js:

```powershell
# Create local directory
mkdir -Force "$env:USERPROFILE\.openclaw"
Set-Location "$env:USERPROFILE\.openclaw"

# Download and run local installer
Invoke-WebRequest -Uri "https://openclaw.ai/install-cli.sh" -OutFile "install-cli.sh"

# The installer will set up OpenClaw in ~/.openclaw without system dependencies
```

### 3.2 Method 2: NPM Global Install (If Node.js is already installed)

```powershell
# Check if Node.js is installed
node --version  # Should be v20 or higher
npm --version

# Install OpenClaw globally
npm install -g openclaw

# Initialize OpenClaw
openclaw
```

### 3.3 Method 3: Standalone Windows Binary

```powershell
# Download Windows standalone binary
$releaseUrl = "https://github.com/OpenClaw/openclaw/releases/latest"
# Download openclaw-win-x64.exe from releases page

# Place in local bin directory
mkdir -Force "$env:USERPROFILE\.openclaw\bin"
# Move downloaded binary to bin directory

# Add to PATH (for current session)
$env:PATH += ";$env:USERPROFILE\.openclaw\bin"

# Add to PATH (permanent)
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$env:USERPROFILE\.openclaw\bin", "User")
```

### 3.4 Post-Installation Configuration

```powershell
# Navigate to workspace
Set-Location "$env:USERPROFILE\.openclaw\workspace"

# Create essential directories
mkdir -Force "memory"
mkdir -Force "skills"
mkdir -Force "scripts"

# Create initial configuration files
```

### 3.5 Create SOUL.md (Identity File)

```powershell
@'
# SOUL.md - Who You Are

## Core Truths

**Be genuinely helpful, not performatively helpful.**
**Have opinions.** You're allowed to disagree, prefer things.
**Be resourceful before asking.** Try to figure it out first.
**Earn trust through competence.**

## Boundaries

- Private things stay private. Period.
- When in doubt, ask before acting externally.
- Never send half-baked replies to messaging surfaces.

## Vibe

Be the assistant you'd actually want to talk to. Concise when needed, thorough when it matters.
'@ | Set-Content -Path "$env:USERPROFILE\.openclaw\workspace\SOUL.md" -Encoding UTF8
```

### 3.6 Create USER.md (Human Profile)

```powershell
@'
# USER.md - About Your Human

- **Name:** [Your Name]
- **What to call them:** [Preferred name]
- **Pronouns:** [Optional]
- **Timezone:** [Your timezone]
- **Hardware:** AMD Ryzen, 20GB RAM, No GPU
- **Setup Type:** Fully Local (No cloud dependencies)

## Context

- Running fully local AI setup on Windows 11
- 20GB RAM limits model size to 8B-14B range
- CPU-only inference (no GPU acceleration)
- Values privacy and offline capability
'@ | Set-Content -Path "$env:USERPROFILE\.openclaw\workspace\USER.md" -Encoding UTF8
```

### 3.7 Configure OpenClaw for Local-Only Operation

Edit the OpenClaw configuration to disable cloud providers:

```json
// ~/.openclaw/config.json
{
  "defaultModel": "ollama:qwen2.5:14b",
  "providers": {
    "ollama": {
      "enabled": true,
      "host": "http://localhost:11434",
      "models": [
        "qwen2.5:8b",
        "qwen2.5:14b",
        "llama3.2:3b",
        "phi4:14b",
        "gemma3:4b",
        "mistral:7b"
      ]
    },
    "openai": {
      "enabled": false
    },
    "anthropic": {
      "enabled": false
    },
    "openrouter": {
      "enabled": false
    }
  },
  "tools": {
    "exec": {
      "enabled": true,
      "security": "allowlist"
    },
    "web_search": {
      "enabled": false
    },
    "web_fetch": {
      "enabled": false
    }
  }
}
```

---

## 4. Ollama Setup & Configuration

### 4.1 Install Ollama for Windows

```powershell
# Download Ollama Windows installer
$ollamaUrl = "https://ollama.com/download/OllamaSetup.exe"
$ollamaInstaller = "$env:TEMP\OllamaSetup.exe"

Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaInstaller

# Run installer silently
Start-Process -FilePath $ollamaInstaller -ArgumentList "/S" -Wait

# Verify installation
ollama --version
```

### 4.2 Configure Ollama for 20GB RAM System

Create/modify Ollama environment configuration:

```powershell
# Create Ollama configuration directory
mkdir -Force "$env:USERPROFILE\.ollama"

# Set environment variables for Ollama (System-wide)
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "127.0.0.1:11434", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "$env:USERPROFILE\.ollama\models", "User")

# Critical for CPU-only: Limit threads to prevent system freeze
# Set to (Physical Cores - 1) to keep system responsive
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS", "6", "User")

# Memory optimization for 20GB RAM
[Environment]::SetEnvironmentVariable("OLLAMA_MAX_LOADED_MODELS", "1", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "5m", "User")

# CPU-specific optimizations
[Environment]::SetEnvironmentVariable("OLLAMA_CPU_ONLY", "1", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "8192", "User")

# Apply environment variables to current session
$env:OLLAMA_HOST = "127.0.0.1:11434"
$env:OLLAMA_MODELS = "$env:USERPROFILE\.ollama\models"
$env:OLLAMA_NUM_THREADS = "6"
$env:OLLAMA_MAX_LOADED_MODELS = "1"
$env:OLLAMA_KEEP_ALIVE = "5m"
$env:OLLAMA_CPU_ONLY = "1"
$env:OLLAMA_CONTEXT_LENGTH = "8192"
```

### 4.3 Start Ollama Service

```powershell
# Start Ollama (it runs as a background service)
Start-Process ollama

# Wait for service to start
Start-Sleep -Seconds 5

# Verify Ollama is running
Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing
```

### 4.4 Ollama Systemd/Service Configuration (Alternative)

Create a scheduled task for auto-start:

```powershell
# Create Ollama startup task
$action = New-ScheduledTaskAction -Execute "ollama" -Argument "serve"
$trigger = New-ScheduledTaskTrigger -AtLogon
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "OllamaServer" -Action $action -Trigger $trigger -Settings $settings -Description "Ollama LLM Server"

# Start the task now
Start-ScheduledTask -TaskName "OllamaServer"
```

---

## 5. BitNet 1.58 Integration for Maximum Efficiency

### 5.1 What is BitNet 1.58?

BitNet 1.58 is Microsoft's 1-bit LLM technology that uses ternary weights (-1, 0, +1) instead of full precision. This provides:
- **16x memory reduction** compared to FP16
- **CPU-optimized inference** (no GPU needed)
- **Faster token generation** on consumer hardware
- **2B-4T parameter models** that run efficiently on limited RAM

### 5.2 Install BitNet Dependencies

```powershell
# Prerequisites for BitNet on Windows
# 1. Visual Studio 2022 Build Tools (if not installed)
winget install Microsoft.VisualStudio.2022.BuildTools

# 2. Python 3.10+ with pip
python --version

# 3. CMake
winget install Kitware.CMake

# 4. Git
winget install Git.Git
```

### 5.3 Install BitNet from Source

```powershell
# Create BitNet directory
mkdir -Force "C:\Tools\BitNet"
Set-Location "C:\Tools\BitNet"

# Clone BitNet repository
git clone https://github.com/microsoft/BitNet.git
cd BitNet

# Install Python dependencies
pip install -r requirements.txt

# Build bitnet.cpp (Windows-specific)
# Note: This requires Visual Studio 2022 with C++ tools
mkdir build
cd build
cmake .. -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release

# Verify installation
.\Release\bitnet.exe --help
```

### 5.4 Download BitNet Models

```powershell
# Download BitNet b1.58 2B-4T model (recommended for 20GB RAM)
# This model uses only ~500MB RAM but provides surprising quality

# Using HuggingFace CLI
pip install huggingface-hub

huggingface-cli download microsoft/bitnet-b1.58-2B-4T --local-dir C:\Models\bitnet-b1.58-2B-4T

# Or download manually from:
# https://huggingface.co/microsoft/bitnet-b1.58-2B-4T
```

### 5.5 Create BitNet Wrapper for OpenClaw

Since BitNet doesn't natively integrate with Ollama, create a wrapper:

```powershell
# Create BitNet server script
@'
#!/usr/bin/env python3
"""
BitNet wrapper for OpenClaw integration
Provides HTTP API compatible with Ollama
"""

import subprocess
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

BITNET_PATH = "C:\\Tools\\BitNet\\BitNet\\build\\Release\\bitnet.exe"
MODEL_PATH = "C:\\Models\\bitnet-b1.58-2B-4T"

class BitNetHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/generate":
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            
            prompt = post_data.get('prompt', '')
            
            # Run BitNet inference
            result = subprocess.run(
                [BITNET_PATH, "-m", MODEL_PATH, "-p", prompt, "-n", "512"],
                capture_output=True,
                text=True
            )
            
            response = {
                "response": result.stdout,
                "done": True
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == "/api/tags":
            # Return model info
            models = {
                "models": [{
                    "name": "bitnet-b1.58-2B-4T",
                    "size": 500000000,
                    "parameter_size": "2B",
                    "quantization": "1.58-bit"
                }]
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(models).encode())
    
    def log_message(self, format, *args):
        # Suppress logs
        pass

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 11435), BitNetHandler)
    print("BitNet server running on port 11435")
    server.serve_forever()
'@ | Set-Content -Path "$env:USERPROFILE\.openclaw\scripts\bitnet_server.py" -Encoding UTF8

# Create startup script for BitNet server
@'
@echo off
python "%USERPROFILE%\.openclaw\scripts\bitnet_server.py"
'@ | Set-Content -Path "$env:USERPROFILE\.openclaw\scripts\start-bitnet.bat" -Encoding ASCII
```

### 5.6 Configure OpenClaw for BitNet

```json
// Add to ~/.openclaw/config.json
{
  "providers": {
    "bitnet": {
      "enabled": true,
      "host": "http://localhost:11435",
      "models": ["bitnet-b1.58-2B-4T"]
    }
  }
}
```

---

## 6. Model Selection for 20GB RAM Systems

### 6.1 Recommended Models (8B-14B Range)

| Model | Size | Quantization | RAM Usage | Speed (tok/s) | Best For |
|-------|------|--------------|-----------|---------------|----------|
| **Qwen2.5 14B** | 14B | Q4_K_M | ~9GB | 5-8 | General purpose, coding |
| **Qwen2.5 8B** | 8B | Q4_K_M | ~5.5GB | 8-12 | Fast responses, chat |
| **Phi-4 14B** | 14B | Q4_K_M | ~9GB | 4-7 | Reasoning, analysis |
| **Llama 3.2 3B** | 3B | Q4_K_M | ~2GB | 15-25 | Quick tasks, summaries |
| **Gemma 3 4B** | 4B | Q4_K_M | ~3GB | 12-18 | Google ecosystem tasks |
| **Mistral 7B** | 7B | Q4_K_M | ~4.5GB | 10-15 | General chat |
| **DeepSeek-R1 14B** | 14B | Q4_K_M | ~9GB | 3-6 | Deep reasoning |
| **BitNet 2B-4T** | 2B | 1.58-bit | ~0.5GB | 20-40 | Maximum efficiency |

### 6.2 Download Recommended Models

```powershell
# Pull models optimized for your 20GB system

# Primary: Qwen2.5 14B (best balance of quality and speed)
ollama pull qwen2.5:14b

# Secondary: Qwen2.5 8B (faster fallback)
ollama pull qwen2.5:8b

# Tertiary: Phi-4 14B (excellent reasoning)
ollama pull phi4:14b

# Fast option: Llama 3.2 3B (for quick tasks)
ollama pull llama3.2:3b

# Verify all models
ollama list
```

### 6.3 Model Benchmarking Script

```powershell
# Create benchmark script
@'
#!/usr/bin/env python3
"""Benchmark Ollama models for CPU inference"""

import requests
import time
import json

MODELS = [
    "qwen2.5:8b",
    "qwen2.5:14b",
    "phi4:14b",
    "llama3.2:3b"
]

TEST_PROMPT = "Explain the concept of machine learning in three sentences."

def benchmark_model(model_name):
    print(f"\nBenchmarking {model_name}...")
    
    start_time = time.time()
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model_name,
            "prompt": TEST_PROMPT,
            "stream": False,
            "options": {
                "num_thread": 6,
                "num_ctx": 4096
            }
        }
    )
    
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        tokens = result.get('eval_count', 0)
        total_time = end_time - start_time
        tokens_per_sec = tokens / total_time if total_time > 0 else 0
        
        print(f"  Tokens generated: {tokens}")
        print(f"  Time: {total_time:.2f}s")
        print(f"  Speed: {tokens_per_sec:.2f} tok/s")
        return {
            "model": model_name,
            "tokens": tokens,
            "time": total_time,
            "tok_per_sec": tokens_per_sec
        }
    else:
        print(f"  ERROR: {response.status_code}")
        return None

if __name__ == "__main__":
    print("CPU Inference Benchmark - 20GB RAM System")
    print("=" * 50)
    
    results = []
    for model in MODELS:
        result = benchmark_model(model)
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    for r in sorted(results, key=lambda x: x['tok_per_sec'], reverse=True):
        print(f"{r['model']}: {r['tok_per_sec']:.2f} tok/s")
'@ | Set-Content -Path "$env:USERPROFILE\.openclaw\scripts\benchmark_models.py" -Encoding UTF8

# Run benchmark
python "$env:USERPROFILE\.openclaw\scripts\benchmark_models.py"
```

---

## 7. TurboQuant & Speculative Decoding Setup

### 7.1 Understanding TurboQuant

TurboQuant is an advanced quantization method that provides better quality than standard Q4_K_M at similar file sizes. It's particularly effective for CPU inference.

### 7.2 Speculative Decoding Explained

Speculative Decoding uses a smaller "draft" model to predict tokens, which are then verified by the main model. This can provide **2-3x speedup** with minimal quality loss.

### 7.3 Enable Speculative Decoding in Ollama

```powershell
# Set environment variable for speculative decoding
[Environment]::SetEnvironmentVariable("OLLAMA_SPECULATIVE_DECODING", "1", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_DRAFT_MODEL", "llama3.2:3b", "User")

# Apply to current session
$env:OLLAMA_SPECULATIVE_DECODING = "1"
$env:OLLAMA_DRAFT_MODEL = "llama3.2:3b"

# Restart Ollama
Get-Process ollama | Stop-Process -Force
Start-Sleep -Seconds 2
Start-Process ollama
```

### 7.4 Create Custom Modelfile with TurboQuant

```powershell
# Create optimized Modelfile for Qwen2.5 14B
@'
FROM qwen2.5:14b

# System prompt optimized for local inference
SYSTEM """You are a helpful AI assistant running on local hardware. 
Provide concise, accurate responses optimized for CPU inference.
Avoid unnecessary verbosity."""

# Parameter optimizations for 20GB RAM, CPU-only
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 8192
PARAMETER num_thread 6
PARAMETER num_batch 512
PARAMETER repeat_penalty 1.1

# Enable Flash Attention (if supported by build)
PARAMETER flash_attn true
'@ | Set-Content -Path "$env:USERPROFILE\.ollama\Modelfile.qwen-optimized" -Encoding UTF8

# Create the optimized model
ollama create qwen2.5:14b-optimized -f "$env:USERPROFILE\.ollama\Modelfile.qwen-optimized"
```

### 7.5 Alternative: IQ4_XS Quantization (Higher Quality)

```powershell
# Download IQ4_XS quantized models (better quality than Q4_K_M)
# These require manual download from HuggingFace or other sources

# Example: Download from HuggingFace
pip install huggingface-hub

# Search for IQ4_XS quantized models
# https://huggingface.co/models?search=IQ4_XS
```

---

## 8. llama.cpp CPU Optimization

### 8.1 Build llama.cpp from Source (Optimized for AMD)

```powershell
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build with AMD CPU optimizations
mkdir build
cd build

# Configure with optimizations for AMD Ryzen
# AVX2 and AVX-512 (if supported by your CPU)
cmake .. `
    -DCMAKE_BUILD_TYPE=Release `
    -DLLAMA_NATIVE=ON `
    -DLLAMA_AVX2=ON `
    -DLLAMA_AVX512=OFF `  # Set ON if your CPU supports AVX-512
    -DLLAMA_OPENMP=ON `
    -DLLAMA_CPU=ON

# Build
cmake --build . --config Release -j $env:NUMBER_OF_PROCESSORS

# Verify binaries
.\bin\Release\llama-cli.exe --help
```

### 8.2 llama.cpp Server Configuration

```powershell
# Start llama.cpp server with CPU optimizations
$llamaServer = "C:\Tools\llama.cpp\build\bin\Release\llama-server.exe"
$modelPath = "$env:USERPROFILE\.ollama\models\blobs\*qwen2.5-14b*"

# Find actual model file
$modelFile = Get-ChildItem -Path "$env:USERPROFILE\.ollama\models\blobs" | 
    Where-Object { $_.Name -match "qwen" -or $_.Name -match "14b" } | 
    Select-Object -First 1

# Start server with optimal CPU settings
& $llamaServer `
    --model $modelFile.FullName `
    --ctx-size 8192 `
    --threads 6 `
    --threads-batch 6 `
    --batch-size 512 `
    --ubatch-size 512 `
    --flash-attn `
    --port 8080
```

### 8.3 llama.cpp Performance Flags Reference

| Flag | Description | Recommended Value |
|------|-------------|-------------------|
| `--threads` | CPU threads for generation | Physical cores - 1 |
| `--threads-batch` | CPU threads for prompt processing | Same as --threads |
| `--ctx-size` | Context window | 4096-8192 |
| `--batch-size` | Maximum batch size | 512-1024 |
| `--ubatch-size` | Micro-batch size | 512 |
| `--flash-attn` | Enable Flash Attention | Always enable |
| `--no-mmap` | Disable memory mapping | Use if RAM is sufficient |
| `--mlock` | Lock pages in memory | Use for consistent performance |

---

## 9. Performance Tuning for CPU-Only Inference

### 9.1 Thread Optimization

```powershell
# Determine optimal thread count
$physicalCores = (Get-WmiObject -Class Win32_Processor).NumberOfCores
$logicalProcessors = (Get-WmiObject -Class Win32_Processor).NumberOfLogicalProcessors

# For LLMs: Use physical cores - 1 (leave one for OS)
$optimalThreads = $physicalCores - 1
Write-Host "Physical cores: $physicalCores"
Write-Host "Recommended threads for Ollama: $optimalThreads"

# Set in environment
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS", "$optimalThreads", "User")
```

### 9.2 Memory Allocation Strategy

With 20GB RAM, follow this allocation:

| Component | RAM Allocation | Notes |
|-----------|--------------|-------|
| **OS + Background** | 4-6GB | Keep Windows responsive |
| **Active Model** | 8-10GB | Q4_K_M 14B model |
| **Context/Cache** | 2-4GB | KV cache, conversation history |
| **Reserved** | 2GB | Emergency buffer |

### 9.3 Batch Size Optimization

```powershell
# Test different batch sizes
$batchSizes = @(256, 512, 1024)

foreach ($size in $batchSizes) {
    Write-Host "\nTesting batch size: $size"
    
    # Set batch size via environment
    $env:OLLAMA_NUM_BATCH = $size
    
    # Restart Ollama with new settings
    Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Start-Process ollama
    Start-Sleep -Seconds 5
    
    # Run quick benchmark
    $response = Invoke-WebRequest `
        -Uri "http://localhost:11434/api/generate" `
        -Method POST `
        -Body (@{
            model = "qwen2.5:8b"
            prompt = "Count from 1 to 10."
            stream = $false
        } | ConvertTo-Json) `
        -ContentType "application/json" `
        -UseBasicParsing
    
    Write-Host "Batch size $size completed"
}
```

### 9.4 Context Window Sizing

```powershell
# Context length vs. RAM usage (approximate)
# 8K context = ~2GB additional RAM
# 16K context = ~4GB additional RAM
# 32K context = ~8GB additional RAM

# For 20GB total RAM with 14B model:
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "8192", "User")

# For 20GB total RAM with 8B model:
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "16384", "User")
```

### 9.5 Process Priority Management

```powershell
# Create script to boost Ollama priority
@'
# Boost Ollama process priority
$process = Get-Process ollama -ErrorAction SilentlyContinue
if ($process) {
    $process.PriorityClass = "High"
    Write-Host "Ollama priority set to High"
} else {
    Write-Host "Ollama not running"
}

# Also set CPU affinity if needed (optional)
# $process.ProcessorAffinity = 0x3F  # Use first 6 cores only
'@ | Set-Content -Path "$env:USERPROFILE\.openclaw\scripts\boost-ollama.ps1" -Encoding UTF8

# Run after starting Ollama
& "$env:USERPROFILE\.openclaw\scripts\boost-ollama.ps1"
```

---

## 10. Fallback Strategies

### 10.1 Model Fallback Chain

Configure OpenClaw to automatically fall back to smaller models:

```json
// ~/.openclaw/config.json
{
  "modelFallbacks": {
    "primary": "qwen2.5:14b",
    "on_timeout": "qwen2.5:8b",
    "on_oom": "llama3.2:3b",
    "on_error": "phi4:14b"
  },
  "timeout": {
    "request_timeout_ms": 120000,
    "max_retries": 2
  }
}
```

### 10.2 Automatic Model Switching Script

```powershell
# Create smart model selector
@'
#!/usr/bin/env python3
"""Smart model selection based on available RAM"""

import psutil
import requests
import json

MODELS = {
    "high_ram": "qwen2.5:14b",      # >12GB available
    "medium_ram": "qwen2.5:8b",      # 8-12GB available
    "low_ram": "llama3.2:3b",        # <8GB available
    "emergency": "bitnet-b1.58-2B-4T" # Minimal RAM
}

def get_available_ram():
    mem = psutil.virtual_memory()
    return mem.available / (1024**3)  # GB

def select_model():
    available = get_available_ram()
    print(f"Available RAM: {available:.1f} GB")
    
    if available > 12:
        return MODELS["high_ram"]
    elif available > 8:
        return MODELS["medium_ram"]
    elif available > 4:
        return MODELS["low_ram"]
    else:
        return MODELS["emergency"]

if __name__ == "__main__":
    model = select_model()
    print(f"Selected model: {model}")
    
    # Write to config
    config = {"current_model": model}
    with open("model_selection.json", "w") as f:
        json.dump(config, f)
'@ | Set-Content -Path "$env:USERPROFILE\.openclaw\scripts\smart_model.py" -Encoding UTF8

# Install psutil if needed
pip install psutil
```

### 10.3 Hybrid CPU/GPU (If iGPU Available)

If your AMD Ryzen has integrated graphics:

```powershell
# Check for AMD iGPU
$gpu = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -match "AMD" }
if ($gpu) {
    Write-Host "AMD GPU detected: $($gpu.Name)"
    
    # Ollama may automatically use iGPU
    # Force CPU-only if iGPU is weak:
    [Environment]::SetEnvironmentVariable("OLLAMA_CPU_ONLY", "0", "User")
} else {
    Write-Host "No AMD GPU detected - using CPU-only mode"
    [Environment]::SetEnvironmentVariable("OLLAMA_CPU_ONLY", "1", "User")
}
```

### 10.4 Emergency Recovery Mode

```powershell
# Create emergency reset script
@'
# Emergency Ollama reset
Write-Host "EMERGENCY RESET: Stopping all LLM processes..."

# Kill Ollama
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force

# Clear model cache (forces reload)
Remove-Item -Path "$env:USERPROFILE\.ollama\models\*" -Recurse -Force -ErrorAction SilentlyContinue

# Reset to smallest model
$env:OLLAMA_DEFAULT_MODEL = "llama3.2:3b"

# Restart with minimal settings
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS", "4", "Process")
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "4096", "Process")

Start-Process ollama
Write-Host "Ollama restarted with minimal settings"
'@ | Set-Content -Path "$env:USERPROFILE\.openclaw\scripts\emergency-reset.ps1" -Encoding UTF8
```

---

## 11. Troubleshooting Common Issues

### 11.1 Issue: Ollama Won't Start

**Symptoms:** Port 11434 not responding, connection refused

**Solutions:**
```powershell
# Check if port is in use
Get-NetTCPConnection -LocalPort 11434

# Kill existing processes
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process *llama* -ErrorAction SilentlyContinue | Stop-Process -Force

# Clear lock files
Remove-Item -Path "$env:TEMP\ollama*" -Force -ErrorAction SilentlyContinue

# Restart service
Start-Process ollama -ArgumentList "serve" -NoNewWindow
```

### 11.2 Issue: Out of Memory Errors

**Symptoms:** "runtime error: out of memory", system freeze

**Solutions:**
```powershell
# Reduce thread count
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS", "4", "User")

# Reduce context length
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "4096", "User")

# Use smaller model
ollama run llama3.2:3b

# Disable memory mapping (forces RAM load)
[Environment]::SetEnvironmentVariable("OLLAMA_NO_MMAP", "1", "User")

# Enable memory locking
[Environment]::SetEnvironmentVariable("OLLAMA_MLOCK", "1", "User")
```

### 11.3 Issue: Slow Token Generation (< 2 tok/s)

**Symptoms:** Responses take minutes, very slow output

**Solutions:**
```powershell
# Check CPU throttling
Get-WmiObject MSAcpi_ThermalZoneTemperature | 
    Select-Object InstanceName, @{Name="Temp(C)";Expression={($_.CurrentTemperature - 2732) / 10.0}}

# Check if using too many threads
# Try reducing to physical core count / 2
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS", "4", "User")

# Use smaller quantization
ollama pull qwen2.5:8b-q4_0  # Faster but lower quality

# Check for Windows Defender scanning
Get-MpPreference | Select-Object ExclusionPath
```

### 11.4 Issue: Model Download Fails

**Symptoms:** "pull failed", partial downloads, checksum errors

**Solutions:**
```powershell
# Clear partial downloads
Remove-Item -Path "$env:USERPROFILE\.ollama\models\blobs\*.partial" -Force

# Retry with explicit tag
ollama pull qwen2.5:14b-q4_k_m

# Check disk space
Get-PSDrive C | Select-Object Used,Free

# Use mirror/regional endpoint if available
[Environment]::SetEnvironmentVariable("OLLAMA_REGISTRY", "https://registry.ollama.ai", "User")
```

### 11.5 Issue: OpenClaw Can't Connect to Ollama

**Symptoms:** "connection refused", "no such host"

**Solutions:**
```powershell
# Verify Ollama is running
Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing

# Check firewall
Get-NetFirewallRule | Where-Object { $_.DisplayName -match "ollama" }

# Add firewall rule if needed
New-NetFirewallRule -DisplayName "Ollama" -Direction Inbound -LocalPort 11434 -Protocol TCP -Action Allow

# Test with curl alternative
(Invoke-WebRequest -Uri "http://127.0.0.1:11434/api/tags" -UseBasicParsing).Content
```

### 11.6 Issue: Windows Defender Blocking

**Symptoms:** Slow performance, files quarantined

**Solutions:**
```powershell
# Add exclusions (run as Administrator)
Add-MpPreference -ExclusionPath "$env:USERPROFILE\.ollama"
Add-MpPreference -ExclusionPath "$env:USERPROFILE\.openclaw"
Add-MpPreference -ExclusionProcess "ollama.exe"

# Verify exclusions
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

### 11.7 Issue: High CPU Temperature / Throttling

**Symptoms:** Performance degrades over time, thermal warnings

**Solutions:**
```powershell
# Reduce thread count to reduce heat
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS", "4", "User")

# Add delay between requests
# In your OpenClaw config, add request throttling

# Monitor temperatures
# Install OpenHardwareMonitor or use AMD Ryzen Master
```

---

## 12. Quick Reference Commands

### 12.1 Daily Operations

```powershell
# Start Ollama
Start-Process ollama

# Check running models
ollama ps

# List available models
ollama list

# Run interactive chat
ollama run qwen2.5:14b

# Stop Ollama
Get-Process ollama | Stop-Process -Force
```

### 12.2 OpenClaw Operations

```powershell
# Start OpenClaw
openclaw

# Check OpenClaw status
openclaw status

# Update OpenClaw
npm update -g openclaw

# View logs
Get-Content "$env:USERPROFILE\.openclaw\logs\openclaw.log" -Tail 50
```

### 12.3 Performance Monitoring

```powershell
# Monitor RAM usage while running LLM
while ($true) {
    $mem = Get-WmiObject Win32_OperatingSystem
    $used = ($mem.TotalVisibleMemorySize - $mem.FreePhysicalMemory) / 1MB
    $total = $mem.TotalVisibleMemorySize / 1MB
    Write-Host "RAM: $([math]::Round($used,1)) / $([math]::Round($total,1)) GB" -NoNewline
    Write-Host " ($([math]::Round(($used/$total)*100,1))%)"
    Start-Sleep -Seconds 2
}

# Monitor CPU usage
Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 2 -MaxSamples 10
```

### 12.4 Maintenance Commands

```powershell
# Clean up old models
ollama rm qwen2.5:14b  # Remove specific model

# Prune unused images (Docker-style)
# Ollama automatically manages this

# Clear conversation cache
Remove-Item -Path "$env:USERPROFILE\.ollama\history" -Force -ErrorAction SilentlyContinue

# Update all models
$models = ollama list | Select-String "^\S+" | ForEach-Object { $_.Matches[0].Value }
foreach ($model in $models) {
    Write-Host "Updating $model..."
    ollama pull $model
}
```

### 12.5 Emergency Commands

```powershell
# Kill all LLM processes
Get-Process *ollama*,*llama* | Stop-Process -Force

# Free up RAM immediately
[GC]::Collect()
[GC]::WaitForPendingFinalizers()

# Restart with minimal config
$env:OLLAMA_NUM_THREADS = "2"
$env:OLLAMA_CONTEXT_LENGTH = "2048"
Start-Process ollama
```

---

## Appendix A: Expected Performance Benchmarks

Based on AMD Ryzen with 20GB RAM, CPU-only:

| Model | Quantization | Tokens/Second | RAM Usage | Quality |
|-------|--------------|---------------|-----------|---------|
| Llama 3.2 3B | Q4_K_M | 15-25 tok/s | ~2GB | ⭐⭐⭐ |
| Gemma 3 4B | Q4_K_M | 12-18 tok/s | ~3GB | ⭐⭐⭐ |
| Mistral 7B | Q4_K_M | 8-12 tok/s | ~4.5GB | ⭐⭐⭐⭐ |
| Qwen2.5 8B | Q4_K_M | 8-12 tok/s | ~5.5GB | ⭐⭐⭐⭐ |
| Phi-4 14B | Q4_K_M | 4-7 tok/s | ~9GB | ⭐⭐⭐⭐⭐ |
| Qwen2.5 14B | Q4_K_M | 5-8 tok/s | ~9GB | ⭐⭐⭐⭐⭐ |
| BitNet 2B | 1.58-bit | 20-40 tok/s | ~0.5GB | ⭐⭐⭐ |

---

## Appendix B: Complete Setup Verification Script

```powershell
# Save as verify-setup.ps1 and run to verify everything works

Write-Host "=== OpenClaw Local Setup Verification ===" -ForegroundColor Green
Write-Host ""

# 1. Check Windows version
$os = Get-WmiObject Win32_OperatingSystem
Write-Host "✓ Windows Version: $($os.Caption) $($os.Version)"

# 2. Check RAM
$totalRAM = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
Write-Host "✓ Total RAM: $totalRAM GB"
if ($totalRAM -lt 16) { Write-Host "  ⚠ WARNING: Less than 16GB RAM detected" -ForegroundColor Yellow }

# 3. Check CPU
$cpu = Get-WmiObject Win32_Processor
Write-Host "✓ CPU: $($cpu.Name)"
Write-Host "  Cores: $($cpu.NumberOfCores), Logical: $($cpu.NumberOfLogicalProcessors)"

# 4. Check Ollama
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✓ Ollama installed: $ollamaVersion"
} catch {
    Write-Host "✗ Ollama not found in PATH" -ForegroundColor Red
}

# 5. Check Ollama service
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Ollama service running on port 11434"
    $models = ($response.Content | ConvertFrom-Json).models
    Write-Host "  Models available: $($models.Count)"
    foreach ($model in $models) {
        Write-Host "    - $($model.name)"
    }
} catch {
    Write-Host "✗ Ollama service not responding" -ForegroundColor Red
}

# 6. Check OpenClaw
if (Get-Command openclaw -ErrorAction SilentlyContinue) {
    Write-Host "✓ OpenClaw installed"
} else {
    Write-Host "✗ OpenClaw not found in PATH" -ForegroundColor Red
}

# 7. Check environment variables
Write-Host ""
Write-Host "Environment Configuration:"
$envVars = @("OLLAMA_NUM_THREADS", "OLLAMA_CONTEXT_LENGTH", "OLLAMA_MAX_LOADED_MODELS", "OLLAMA_CPU_ONLY")
foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var, "User")
    if ($value) {
        Write-Host "  $var = $value"
    } else {
        Write-Host "  $var = (not set)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Verification Complete ===" -ForegroundColor Green
```

---

## Summary

This guide provides a complete, fully local OpenClaw setup for a 20GB RAM Windows 11 AMD Ryzen system without a GPU. Key takeaways:

1. **Use Q4_K_M quantization** for best quality/size balance
2. **Limit threads to physical cores - 1** to maintain system responsiveness
3. **8K context length** is the sweet spot for 20GB RAM
4. **Qwen2.5 14B** or **Phi-4 14B** are recommended primary models
5. **BitNet 1.58** provides maximum efficiency for simple tasks
6. **Disable Windows memory compression** for better performance
7. **Always have a fallback model** configured

**Estimated setup time:** 2-3 hours  
**Expected tokens/second:** 5-12 tok/s with 14B models, 15-25 tok/s with 3B models  
**Offline capability:** 100% - no cloud dependencies required

---

*Guide generated: 2026-04-15*  
*For updates and community support: https://github.com/OpenClaw/openclaw*