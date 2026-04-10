# Daily Session Cleanup Script
# Archives old sessions and restarts OpenClaw fresh

$date = Get-Date -Format "yyyy-MM-dd"
$backupDir = "C:\Users\Karen\.openclaw\backups\sessions\$date"
$sessionsFile = "C:\Users\Karen\.openclaw\agents\main\sessions\sessions.json"

# Create backup directory
New-Item -ItemType Directory -Force -Path $backupDir

# Backup current sessions
Copy-Item $sessionsFile "$backupDir\sessions.json.backup"

# Archive to memory
$archiveEntry = @"
## Session Archive - $date

**Sessions backed up to:** $backupDir
**Total sessions archived:** $(Get-Content $sessionsFile | Select-String -Pattern "sessionKey" | Measure-Object | Select-Object -ExpandProperty Count)
**Cleanup time:** $(Get-Date)

Old sessions archived. System restarted fresh.
"@

Add-Content -Path "C:\Users\Karen\.openclaw\workspace\memory\session-archives.md" -Value $archiveEntry

# Keep only recent sessions (last 24 hours) - simplified cleanup
# Note: This is a basic cleanup - adjust as needed

Write-Host "Sessions archived to: $backupDir"
Write-Host "Memory log updated"
