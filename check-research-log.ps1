$files = Get-ChildItem -Path 'C:\Users\Karen\.openclaw\workspace\memory\research' -Filter '2026-04-10_*.md' | Sort-Object Name
foreach ($file in $files) {
    $sizeKb = [math]::Round($file.Length / 1KB, 2)
    Write-Output "$($file.Name) | ${sizeKb} KB | $($file.LastWriteTime)"
}
Write-Output "---"
Write-Output "Total files: $($files.Count)"
