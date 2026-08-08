# OpenClaw Daily Session Cleanup
# Run outside OpenClaw sandbox via Windows Task Scheduler
# Deletes old sessions, checkpoints, and lock files

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$logFile = "C:\Users\Karen\.openclaw\workspace\memory\session-cleanup.log"
$sessionsDir = "C:\Users\Karen\.openclaw\agents\main\sessions"
$archiveDir = "C:\Users\Karen\.openclaw\workspace\memory\session-archive"
$maxAgeDays = 7

$deletedSessions = 0
$deletedCheckpoints = 0
$deletedLocks = 0
$deletedOrphans = 0
$errors = @()

function Write-Log {
    param([string]$message)
    "$timestamp - $message" | Out-File -FilePath $logFile -Append -Encoding UTF8
    Write-Output "$timestamp - $message"
}

Write-Log "=== Session Cleanup Started ==="

# Ensure archive directory exists
if (!(Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
}

# 1. Delete old session files (not current main session)
$currentSession = "502042a9-e658-4650-8714-d962a859adda"
try {
    Get-ChildItem -Path $sessionsDir -Filter "*.jsonl" | Where-Object {
        $_.Name -notlike "*$currentSession*" -and
        $_.Name -notlike "*.deleted.*" -and
        $_.LastWriteTime -lt (Get-Date).AddDays(-$maxAgeDays)
    } | ForEach-Object {
        Remove-Item $_.FullName -Force
        $deletedSessions++
    }
} catch {
    $errors += "Session cleanup error: $($_.Exception.Message)"
}

# 2. Delete old checkpoint files
try {
    Get-ChildItem -Path $sessionsDir -Filter "*.checkpoint.*.jsonl" | Where-Object {
        $_.LastWriteTime -lt (Get-Date).AddDays(-$maxAgeDays)
    } | ForEach-Object {
        Remove-Item $_.FullName -Force
        $deletedCheckpoints++
    }
} catch {
    $errors += "Checkpoint cleanup error: $($_.Exception.Message)"
}

# 3. Delete stale lock files (older than 1 hour)
try {
    Get-ChildItem -Path $sessionsDir -Filter "*.lock" | Where-Object {
        $_.LastWriteTime -lt (Get-Date).AddHours(-1)
    } | ForEach-Object {
        Remove-Item $_.FullName -Force
        $deletedLocks++
    }
} catch {
    $errors += "Lock cleanup error: $($_.Exception.Message)"
}

# 4. Delete orphaned .deleted files (older than 1 day)
try {
    Get-ChildItem -Path $sessionsDir -Filter "*.deleted.*" | Where-Object {
        $_.LastWriteTime -lt (Get-Date).AddDays(-1)
    } | ForEach-Object {
        Remove-Item $_.FullName -Force
        $deletedOrphans++
    }
} catch {
    $errors += "Orphan cleanup error: $($_.Exception.Message)"
}

# 5. Count remaining sessions
$remainingSessions = (Get-ChildItem -Path $sessionsDir -Filter "*.jsonl" | Where-Object {
    $_.Name -notlike "*.deleted.*" -and $_.Name -notlike "*.lock*"
}).Count

# Log results
Write-Log "Deleted sessions: $deletedSessions"
Write-Log "Deleted checkpoints: $deletedCheckpoints"
Write-Log "Deleted locks: $deletedLocks"
Write-Log "Deleted orphans: $deletedOrphans"
Write-Log "Remaining sessions: $remainingSessions"

if ($errors.Count -gt 0) {
    foreach ($err in $errors) {
        Write-Log "ERROR: $err"
    }
}

Write-Log "=== Session Cleanup Complete ==="
Write-Log ""

# Return exit code for Task Scheduler
exit 0
