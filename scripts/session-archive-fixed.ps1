# Session Archive System
# Archives complete session history before daily cleanup
# Run: powershell -File scripts/session-archive.ps1

$ArchiveRoot = "C:\Users\Karen\.openclaw\workspace\memory\session-archive"
$SessionFile = "C:\Users\Karen\.openclaw\agents\main\sessions\sessions.json"
$Date = Get-Date -Format "yyyy-MM-dd"
$Year = Get-Date -Format "yyyy"
$MonthName = Get-Date -Format "MM-MMMM"

# Create directory structure
$ArchiveDir = Join-Path $ArchiveRoot "$Year\$MonthName\$Date"
New-Item -ItemType Directory -Path $ArchiveDir -Force | Out-Null

Write-Host "Archiving sessions for $Date to $ArchiveDir"

# Copy raw session data
if (Test-Path $SessionFile) {
    Copy-Item $SessionFile (Join-Path $ArchiveDir "sessions.json") -Force
    $sessionSize = (Get-Item $SessionFile).Length
    Write-Host "  [OK] sessions.json ($([math]::Round($sessionSize/1KB, 2)) KB)"
} else {
    Write-Host "  [WARN] No sessions.json found at $SessionFile"
}

# Create human-readable summary
$summaryFile = Join-Path $ArchiveDir "conversations.md"
$header = @"
# Conversation Archive - $Date

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**System:** OpenClaw on DESKTOP-M8AO8LN

## Sessions Summary

"@

$header | Out-File $summaryFile -Encoding UTF8

# Extract conversation topics if sessions exist
if (Test-Path $SessionFile) {
    try {
        $sessions = Get-Content $SessionFile | ConvertFrom-Json -ErrorAction SilentlyContinue
        foreach ($session in $sessions) {
            $sessionTime = if ($session.created_at) { 
                [datetime]::Parse($session.created_at).ToString("HH:mm") 
            } else { "unknown" }
            $sessionId = if ($session.id) { $session.id.Substring(0,[Math]::Min(8, $session.id.Length)) } else { "unknown" }
            "- **$sessionTime** - Session ${sessionId}..." | Add-Content $summaryFile
        }
    } catch {
        "- Raw session data archived (parse error)" | Add-Content $summaryFile
    }
} else {
    "- No session data available" | Add-Content $summaryFile
}

"`n---`n*Full session data available in sessions.json*" | Add-Content $summaryFile

Write-Host "  [OK] conversations.md created"

# Create search index
$indexFile = Join-Path $ArchiveDir "search-index.json"
$index = @{
    date = $Date
    timestamp = Get-Date -Format "o"
    topics = @()
    projects = @()
    files_modified = @()
    keywords = @()
}

$index | ConvertTo-Json -Depth 3 | Out-File $indexFile -Encoding UTF8
Write-Host "  [OK] search-index.json created"

# Calculate totals
$archiveSize = (Get-ChildItem $ArchiveDir -Recurse | Measure-Object -Property Length -Sum).Sum
Write-Host "`nArchive complete: $([math]::Round($archiveSize/1KB, 2)) KB"

# Show storage summary
$totalUsed = (Get-ChildItem $ArchiveRoot -Recurse -File | Measure-Object -Property Length -Sum).Sum
$totalGB = [math]::Round($totalUsed / 1GB, 3)
Write-Host "Total archive usage: $totalGB GB / ~1000 GB available"
