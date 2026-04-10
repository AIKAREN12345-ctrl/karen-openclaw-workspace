$backupScript = "C:\Users\Karen\.openclaw\workspace\scripts\github-backup.ps1"
if (Test-Path $backupScript) {
    Write-Output "GitHub backup script exists"
    Get-Content $backupScript -Head 10
} else {
    Write-Output "No github-backup.ps1 found"
}
