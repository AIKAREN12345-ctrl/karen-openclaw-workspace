$sessionsDir = "C:\Users\Karen\.openclaw\agents\main\sessions"
if (Test-Path $sessionsDir) {
    Write-Output "Sessions directory exists"
    Get-ChildItem -Path $sessionsDir | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
} else {
    Write-Output "Sessions directory NOT FOUND"
}

$archiveRoot = "C:\Users\Karen\.openclaw\workspace\memory\session-archive"
if (Test-Path $archiveRoot) {
    Write-Output "---"
    Write-Output "Archive root exists"
    Get-ChildItem -Path $archiveRoot -Recurse -Directory | Select-Object FullName | Format-Table -AutoSize
} else {
    Write-Output "Archive root NOT FOUND"
}
