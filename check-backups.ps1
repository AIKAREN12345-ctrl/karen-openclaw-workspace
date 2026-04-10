$backupPath = "C:\Users\Karen\.openclaw\backups\sessions"
if (Test-Path $backupPath) {
    Get-ChildItem $backupPath | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime -First 5 | Format-Table -AutoSize
} else {
    Write-Output "BACKUP PATH NOT FOUND"
}

Write-Output "---"

$cronPath = "C:\Users\Karen\.openclaw\cron\jobs.json"
if (Test-Path $cronPath) {
    $jobs = Get-Content $cronPath | ConvertFrom-Json
    $jobs.jobs | Where-Object { $_.enabled -eq $true } | Select-Object name, schedule | Format-Table -AutoSize
    Write-Output "---"
    Write-Output "Total enabled jobs: $($jobs.jobs | Where-Object { $_.enabled -eq $true } | Measure-Object | Select-Object -ExpandProperty Count)"
} else {
    Write-Output "CRON JOBS NOT FOUND"
}
