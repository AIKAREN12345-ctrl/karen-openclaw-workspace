$ErrorActionPreference = "Stop"
$workspace = "C:\Users\Karen\.openclaw\workspace"
$logFile = "C:\Users\Karen\.openclaw\workspace\memory\github-backups.md"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$dateStr = Get-Date -Format "yyyy-MM-dd"

Push-Location $workspace

try {
    # Check if git repo exists
    if (-not (Test-Path ".git")) {
        throw "Not a git repository"
    }

    # Check for changes
    git update-index --refresh | Out-Null
    $status = git status --short

    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Host "No changes to commit"
        $logEntry = @"

## Backup - $dateStr

**Time:** $timestamp
**Status:** No changes to commit
**Action:** Nothing to push
"@
    } else {
        # Stage all changes
        git add -A
        $commitMsg = "Daily backup - $dateStr"
        git commit -m "$commitMsg"
        git push origin HEAD
        Write-Host "Backup committed and pushed: $commitMsg"
        $logEntry = @"

## Backup - $dateStr

**Time:** $timestamp
**Status:** Committed and pushed
**Commit message:** $commitMsg
"@
    }

    # Update log
    if (-not (Test-Path $logFile)) {
        Set-Content -Path $logFile -Value "# GitHub Backups" -Encoding UTF8
    }
    Add-Content -Path $logFile -Value $logEntry -Encoding UTF8
    Write-Host "  github-backups.md updated"

} catch {
    Write-Host "ERROR: $_"
    $logEntry = @"

## Backup - $dateStr

**Time:** $timestamp
**Status:** FAILED
**Error:** $_
"@
    if (Test-Path $logFile) {
        Add-Content -Path $logFile -Value $logEntry -Encoding UTF8
    }
} finally {
    Pop-Location
}
