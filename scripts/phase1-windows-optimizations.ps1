# OpenClaw Local Setup - Phase 1: Windows Optimizations
# Run these commands in PowerShell as Administrator

# 1. Set High Performance Power Plan
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# 2. Disable Memory Compression (frees RAM for models)
Disable-MMAgent -MemoryCompression

# 3. Configure Pagefile (fixed size for stability)
$computer = Get-WmiObject -Class Win32_ComputerSystem
$computer.AutomaticManagedPagefile = $false
$computer.Put()

$pagefile = Get-WmiObject -Class Win32_PageFileSetting
$pagefile.InitialSize = 8192
$pagefile.MaximumSize = 8192
$pagefile.Put()

# 4. Disable Windows Search indexing (reduces disk/CPU load)
Stop-Service WSearch
Set-Service WSearch -StartupType Disabled

# 5. Set process priority for Ollama/llama.cpp
# (Will be done after installation)

Write-Host "Phase 1 Complete! Restart required for some changes."
