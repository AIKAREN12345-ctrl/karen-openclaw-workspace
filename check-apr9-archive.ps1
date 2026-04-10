$archiveDir = "C:\Users\Karen\.openclaw\workspace\memory\session-archive\2026\04-April\2026-04-09"
if (Test-Path $archiveDir) {
    Write-Output "April 9 archive exists"
    Get-ChildItem -Path $archiveDir -Recurse | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
} else {
    Write-Output "April 9 archive NOT FOUND"
}

Write-Output "---"

$logFile = "C:\Users\Karen\.openclaw\workspace\memory\session-archives.md"
if (Test-Path $logFile) {
    Write-Output "Archive log contents:"
    Get-Content $logFile
} else {
    Write-Output "Archive log NOT FOUND"
}
