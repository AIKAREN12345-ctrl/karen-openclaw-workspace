# Ollama Heartbeat Script
# Runs hourly memory logging using local Ollama model
# Saves to memory/YYYY-MM-DD.md

$date = Get-Date -Format "yyyy-MM-dd"
$time = Get-Date -Format "HH:mm"
$memoryFile = "$env:USERPROFILE\.openclaw\workspace\memory\$date.md"

# Check system status
$openclawVersion = "2026.3.2"  # Static for now
$ollamaStatus = & ollama ps 2>$null
if ($LASTEXITCODE -eq 0 -and $ollamaStatus) {
    $ollamaLine = ($ollamaStatus | Select-Object -Skip 1 | Select-Object -First 1)
    $ollamaInfo = if ($ollamaLine) { "running ($($ollamaLine.Split()[0]))" } else { "installed, no model loaded" }
} else {
    $ollamaInfo = "not responding"
}

# Get disk usage
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$diskFree = [math]::Round($disk.FreeSpace / 1GB, 1)
$diskTotal = [math]::Round($disk.Size / 1GB, 1)
$diskUsed = $diskTotal - $diskFree
$diskPercent = if ($diskTotal -gt 0) { [math]::Round(($diskUsed / $diskTotal) * 100, 0) } else { "N/A" }

# Create memory entry
$entry = @"

## $time - Hourly System Check (Ollama)

**System Status:**
- OpenClaw: $openclawVersion
- Ollama: $ollamaInfo
- Disk: $diskPercent% used ($diskFree GB free / $diskTotal GB total)

**Notes:**
- Automated heartbeat via Ollama script
- No API tokens used

---
"@

# Append to memory file
if (Test-Path $memoryFile) {
    Add-Content -Path $memoryFile -Value $entry
} else {
    Set-Content -Path $memoryFile -Value "# Memory Log - $date`n`n$entry"
}

Write-Host "Memory log updated: $memoryFile"
