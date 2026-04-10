$researchPath = "C:\Users\Karen\.openclaw\workspace\memory\research"
if (Test-Path $researchPath) {
    Get-ChildItem $researchPath | Select-Object Name, LastWriteTime | Format-Table -AutoSize
    Write-Output "---"
    Write-Output "Total files: $((Get-ChildItem $researchPath).Count)"
} else {
    Write-Output "DIRECTORY NOT FOUND: $researchPath"
}

$archivePath = "C:\Users\Karen\.openclaw\workspace\memory\session-archives.md"
if (Test-Path $archivePath) {
    Write-Output "Session archive exists. Last 5 lines:"
    Get-Content $archivePath -Tail 5
} else {
    Write-Output "Archive file not found"
}
