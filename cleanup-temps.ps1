$temps = @(
    "check-apr9-archive.ps1",
    "check-backups.ps1",
    "check-git-status.ps1",
    "check-github-backup.ps1",
    "check-github-config.ps1",
    "check-jobs.ps1",
    "cleanup-audit.ps1",
    "cleanup-delete.ps1",
    "investigate-sessions.ps1",
    "reload-cron.ps1",
    "scan-externals.ps1",
    "start-node.ps1",
    "vnc-chrome-test.png",
    "vnc-test.png",
    "vnc-test-2.png",
    "vnc-test-3.png",
    "scripts/run-vnc-screenshot.ps1",
    "scripts/session-archive-fixed.ps1",
    "scripts/session-archive.py"
)

foreach ($file in $temps) {
    $path = Join-Path "C:\Users\Karen\.openclaw\workspace" $file
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force
        Write-Output "Removed: $file"
    } else {
        Write-Output "Already gone: $file"
    }
}
