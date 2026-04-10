# Session Archive System - PowerShell version for better Windows reliability
$ErrorActionPreference = "Stop"

# Paths
$archiveRoot = "C:\Users\Karen\.openclaw\workspace\memory\session-archive"
$sessionsDir = "C:\Users\Karen\.openclaw\agents\main\sessions"
$logFile = "C:\Users\Karen\.openclaw\workspace\memory\session-archives.md"

# Date components
$today = Get-Date
$dateStr = $today.ToString("yyyy-MM-dd")
$year = $today.ToString("yyyy")
$monthName = $today.ToString("MM-MMMM")
$timestamp = $today.ToString("yyyy-MM-dd HH:mm:ss")

# Create directory structure
$archiveDir = Join-Path $archiveRoot "$year\$monthName\$dateStr"
$sessionsArchiveDir = Join-Path $archiveDir "sessions"
New-Item -ItemType Directory -Path $sessionsArchiveDir -Force | Out-Null

Write-Host "Archiving sessions for $dateStr to $archiveDir"

# Copy session files (.jsonl format)
$sessionsCopied = 0
$sessionsSize = 0

if (Test-Path $sessionsDir) {
    $jsonlFiles = Get-ChildItem -Path $sessionsDir -Filter "*.jsonl" | Where-Object { $_.Name -notlike "*.deleted.*" -and $_.Name -notlike "*.lock" }
    
    foreach ($file in $jsonlFiles) {
        $targetFile = Join-Path $sessionsArchiveDir $file.Name
        Copy-Item -Path $file.FullName -Destination $targetFile -Force
        $sessionsCopied++
        $sessionsSize += $file.Length
    }
    
    if ($sessionsCopied -gt 0) {
        $sizeKb = [math]::Round($sessionsSize / 1024, 2)
        Write-Host "  $sessionsCopied session files ($sizeKb KB)"
    } else {
        Write-Host "  No session files found"
    }
} else {
    Write-Host "  Sessions directory not found"
}

# Create human-readable summary
$summaryFile = Join-Path $archiveDir "conversations.md"

$headerLines = @(
    "# Conversation Archive - $dateStr"
    ""
    "**Generated:** $timestamp"
    "**System:** OpenClaw on DESKTOP-M8AO8LN"
    "**Sessions archived:** $sessionsCopied"
    ""
    "## Sessions Summary"
    ""
)

Set-Content -Path $summaryFile -Value $headerLines -Encoding UTF8

# Extract session info from the copied files
if ($sessionsCopied -gt 0 -and (Test-Path $sessionsArchiveDir)) {
    $archivedFiles = Get-ChildItem -Path $sessionsArchiveDir -Filter "*.jsonl" | Sort-Object Name
    foreach ($file in $archivedFiles) {
        $sessionTime = $file.LastWriteTime.ToString("HH:mm")
        $sessionId = $file.BaseName
        $shortId = if ($sessionId.Length -gt 8) { $sessionId.Substring(0, 8) } else { $sessionId }
        Add-Content -Path $summaryFile -Value "- **$sessionTime** - Session ${shortId}..." -Encoding UTF8
    }
}

Add-Content -Path $summaryFile -Value "" -Encoding UTF8
Add-Content -Path $summaryFile -Value "---" -Encoding UTF8
Add-Content -Path $summaryFile -Value "*Full session data in sessions/ directory*" -Encoding UTF8
Write-Host "  conversations.md created"

# Create search index
$indexFile = Join-Path $archiveDir "search-index.json"
$index = @{
    date = $dateStr
    timestamp = $today.ToString("o")
    sessions_copied = $sessionsCopied
    sessions_size_kb = [math]::Round($sessionsSize / 1024, 2)
    topics = @()
    projects = @()
    files_modified = @()
    keywords = @()
} | ConvertTo-Json -Depth 3

Set-Content -Path $indexFile -Value $index -Encoding UTF8
Write-Host "  search-index.json created"

# Calculate totals
$archiveFiles = Get-ChildItem -Path $archiveDir -Recurse -File
$archiveSize = ($archiveFiles | Measure-Object -Property Length -Sum).Sum
$archiveSizeKb = [math]::Round($archiveSize / 1024, 2)
Write-Host "Archive complete: $archiveSizeKb KB"

# Update master log file
$logEntry = @"

---

## Archive - $dateStr

**Archive path:** `memory/session-archive/$year/$monthName/$dateStr/`
**Cleanup time:** $timestamp
**Action:** $sessionsCopied session .jsonl files backed up, conversations.md and search-index.json created
**Archive size:** $archiveSizeKb KB
"@

if (-not (Test-Path $logFile)) {
    Set-Content -Path $logFile -Value "# Session Archives" -Encoding UTF8
}

Add-Content -Path $logFile -Value $logEntry -Encoding UTF8
Write-Host "  session-archives.md updated"

# Show storage summary
$totalFiles = Get-ChildItem -Path $archiveRoot -Recurse -File
$totalUsed = ($totalFiles | Measure-Object -Property Length -Sum).Sum
$totalGb = [math]::Round($totalUsed / [math]::Pow(1024, 3), 3)
Write-Host "Total archive usage: $totalGb GB / ~1000 GB available"
