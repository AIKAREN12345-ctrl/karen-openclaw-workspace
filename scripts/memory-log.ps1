#!/usr/bin/env pwsh
# Memory Log Script - Logs system status to daily memory file
# Runs hourly via cron

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$date = Get-Date -Format "yyyy-MM-dd"
$hostname = $env:COMPUTERNAME
$platform = "Windows $((Get-CimInstance Win32_OperatingSystem).Version)"

# Check Ollama
$ollamaStatus = "unknown"
try {
    $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
    $ollamaStatus = "running"
    $modelCount = $ollamaResponse.models.Count
} catch {
    $ollamaStatus = "not running"
    $modelCount = 0
}

# Check OpenClaw Gateway
try {
    $gatewayResponse = Invoke-RestMethod -Uri "http://127.0.0.1:18788/status" -TimeoutSec 5 -ErrorAction Stop
    $openclawStatus = "running"
} catch {
    $openclawStatus = "not running"
}

# Get disk info
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeGB = [math]::Round($disk.FreeSpace / 1GB, 1)
$totalGB = [math]::Round($disk.Size / 1GB, 1)
$usedPercent = [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 1)

# Build log entry
$logEntry = @"

## $(Get-Date -Format "HH:mm") - Hourly Memory Log

**Timestamp:** $timestamp
**Hostname:** $hostname
**Platform:** $platform
**Ollama:** $ollamaStatus ($modelCount models)
**OpenClaw:** $openclawStatus
**Disk:** $freeGB GB free / $totalGB GB total ($usedPercent% used)

System operational.

---
"@

# Ensure memory directory exists
$memoryDir = "$env:USERPROFILE\.openclaw\workspace\memory"
if (-not (Test-Path $memoryDir)) {
    New-Item -ItemType Directory -Path $memoryDir -Force | Out-Null
}

# Write to daily memory file
$memoryFile = "$memoryDir\$date.md"
if (-not (Test-Path $memoryFile)) {
    # Create new file with header
    $header = "# Memory Log - $date`n`n"
    Set-Content -Path $memoryFile -Value $header -Encoding UTF8
}

# Append log entry
Add-Content -Path $memoryFile -Value $logEntry -Encoding UTF8

Write-Host "Memory log updated: $memoryFile"
