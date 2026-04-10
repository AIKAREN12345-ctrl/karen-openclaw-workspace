Write-Host "=== EXTERNAL CLUTTER SCAN ===" -ForegroundColor Cyan

function Scan-Folder($path, $label, $minSizeMB = 1) {
    Write-Host ""
    Write-Host "${label}:" -ForegroundColor Yellow
    if (-not (Test-Path $path)) {
        Write-Host "  Path not found"
        return
    }
    $files = Get-ChildItem -Path $path -File -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Length / 1MB -gt $minSizeMB } | Sort-Object Length -Descending | Select-Object -First 20
    if (-not $files) {
        Write-Host "  No large files found"
        return
    }
    $total = 0
    foreach ($f in $files) {
        $mb = [math]::Round($f.Length / 1MB, 2)
        $total += $mb
        Write-Host "  $mb MB`t$($f.FullName)"
    }
    Write-Host "  Top 20 total: $total MB"
}

Scan-Folder "C:\Users\Karen\Downloads" "Downloads" 10
Scan-Folder "C:\Users\Karen\Desktop" "Desktop" 10
Scan-Folder "C:\Users\Karen\Documents" "Documents" 50
Scan-Folder "C:\Program Files" "Program Files" 100
Scan-Folder "C:\Program Files (x86)" "Program Files (x86)" 100

Write-Host ""
Write-Host "=== OLD INSTALLERS ===" -ForegroundColor Yellow
$installerPaths = @("C:\Users\Karen\Downloads","C:\Users\Karen\Desktop")
$exts = @("*.exe","*.msi","*.zip","*.rar","*.7z","*.dmg","*.pkg","*.deb","*.rpm")
foreach ($p in $installerPaths) {
    if (Test-Path $p) {
        $installers = Get-ChildItem -Path $p -Include $exts -Recurse -File -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 10
        foreach ($i in $installers) {
            $mb = [math]::Round($i.Length / 1MB, 2)
            Write-Host "  $mb MB`t$($i.FullName)"
        }
    }
}
