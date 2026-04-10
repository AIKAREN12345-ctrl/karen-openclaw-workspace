# Deep System Audit & Cleanup Script
$report = @()

function Add-Report($Category, $Item, $SizeMB, $Action) {
    $report += [PSCustomObject]@{
        Category = $Category
        Item = $Item
        SizeMB = $SizeMB
        Action = $Action
    }
}

Write-Host "=== DEEP SYSTEM AUDIT ===" -ForegroundColor Cyan
Write-Host ""

# 1. .openclaw workspace root clutter
Write-Host "1. Workspace root clutter:" -ForegroundColor Yellow
$workspace = "C:\Users\Karen\.openclaw\workspace"
$junk = @(
    @{Name="misnamed file '1'"; Path="$workspace\1"; Size=$((Get-Item "$workspace\1" -ErrorAction SilentlyContinue).Length / 1MB)},
    @{Name="cloudflared exe"; Path="$workspace\cloudflared-windows-amd64.exe"; Size=$((Get-Item "$workspace\cloudflared-windows-amd64.exe" -ErrorAction SilentlyContinue).Length / 1MB)},
    @{Name="VNC test screenshot 1"; Path="$workspace\vnc_test_1914.png"; Size=$((Get-Item "$workspace\vnc_test_1914.png" -ErrorAction SilentlyContinue).Length / 1MB)},
    @{Name="VNC test screenshot 2"; Path="$workspace\vnc_after_click.png"; Size=$((Get-Item "$workspace\vnc_after_click.png" -ErrorAction SilentlyContinue).Length / 1MB)},
    @{Name="VNC test screenshot 3"; Path="$workspace\vnc_screenshot.png"; Size=$((Get-Item "$workspace\vnc_screenshot.png" -ErrorAction SilentlyContinue).Length / 1MB)},
    @{Name="test SQLite db"; Path="$workspace\test.db"; Size=$((Get-Item "$workspace\test.db" -ErrorAction SilentlyContinue).Length / 1MB)},
    @{Name="null artifact"; Path="$workspace\`$null"; Size=0},
    @{Name="test exec txt"; Path="$workspace\test-exec.txt"; Size=0},
    @{Name="test subagent txt"; Path="$workspace\test-subagent.txt"; Size=0},
    @{Name="test tool check"; Path="$workspace\test-tool-check.txt"; Size=0},
    @{Name="test isolated session"; Path="$workspace\test-isolated-session.txt"; Size=0}
)
foreach ($j in $junk) {
    if (Test-Path $j.Path) {
        Write-Host "  REMOVE: $($j.Name) ($([math]::Round($j.Size,2)) MB)" -ForegroundColor Red
        Add-Report "Workspace Junk" $j.Name $j.Size "DELETE"
    }
}

# 2. Old college/project artifacts from March (scattered in root)
Write-Host ""
Write-Host "2. Old project artifacts in workspace root:" -ForegroundColor Yellow
$oldFiles = Get-ChildItem -Path $workspace -File | Where-Object {
    $_.Name -match "^(Chocolate_Sales|Butcher_Shop|create_.*\.py|read_.*\.py|analyze_.*\.py|condense_.*\.py|extract_.*\.py|inspect_.*\.py|Paddy_Power)" -or
    $_.Name -match "^(course_content|group_work|new_doc_content|extracted_notes|organizational_culture|butcher_shop_.*)" -or
    $_.Name -match "^(vnc-screenshot-robust\.py|vnc-recorder-robust\.py|vnc-control\.py|enable-vnc.*|restart-openclaw.*|setup-memory-search\.py|simple-heartbeat\.ps1|ollama-agent\.yaml|modelfile-qwen.*)"
}
foreach ($f in $oldFiles) {
    Write-Host "  ARCHIVE/REMOVE: $($f.Name) ($([math]::Round($f.Length/1MB,2)) MB)" -ForegroundColor DarkYellow
    Add-Report "Old Project Files" $f.Name ($f.Length/1MB) "ARCHIVE"
}

# 3. .openclaw directory bloat
Write-Host ""
Write-Host "3. .openclaw directory sizes:" -ForegroundColor Yellow
$openclaw = "C:\Users\Karen\.openclaw"
$dirs = @("browser","canvas","chrome-cdp-profile","completions","credentials","devices","extensions","flows","identity","logs","media","memory","nodes","qqbot","sandboxes","skills","subagents","tasks","telegram","temp-skills")
foreach ($d in $dirs) {
    $p = Join-Path $openclaw $d
    if (Test-Path $p) {
        $size = (Get-ChildItem -Path $p -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "  $d : $([math]::Round($size,2)) MB"
        if ($size -gt 10) {
            Add-Report ".openclaw Bloat" $d $size "REVIEW"
        }
    }
}

# 4. Temp logs
Write-Host ""
Write-Host "4. Temp folder sizes:" -ForegroundColor Yellow
$tempPath = "C:\Users\Karen\AppData\Local\Temp"
$openclawTemp = Join-Path $tempPath "openclaw"
$tempSize = (Get-ChildItem -Path $tempPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
$openclawTempSize = 0
if (Test-Path $openclawTemp) {
    $openclawTempSize = (Get-ChildItem -Path $openclawTemp -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
}
Write-Host "  Total Temp: $([math]::Round($tempSize,2)) MB"
Write-Host "  OpenClaw Temp: $([math]::Round($openclawTempSize,2)) MB"
Add-Report "Temp Files" "Total Temp" $tempSize "REVIEW"
Add-Report "Temp Files" "OpenClaw Temp" $openclawTempSize "REVIEW"

# 5. Ollama models
Write-Host ""
Write-Host "5. Ollama model blobs:" -ForegroundColor Yellow
$ollamaBlobs = "C:\Users\Karen\.ollama\models\blobs"
if (Test-Path $ollamaBlobs) {
    $ollamaSize = (Get-ChildItem -Path $ollamaBlobs -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  Ollama blobs: $([math]::Round($ollamaSize,2)) MB"
    Add-Report "Ollama Models" "Model Blobs" $ollamaSize "REVIEW"
} else {
    Write-Host "  No Ollama blobs found"
}

# 6. npm global bloat
Write-Host ""
Write-Host "6. npm global packages:" -ForegroundColor Yellow
$npmGlobal = "C:\Users\Karen\AppData\Roaming\npm\node_modules"
if (Test-Path $npmGlobal) {
    $pkgs = Get-ChildItem -Path $npmGlobal -Directory | Select-Object -ExpandProperty Name
    foreach ($pkg in $pkgs) {
        $pkgPath = Join-Path $npmGlobal $pkg
        $pkgSize = (Get-ChildItem -Path $pkgPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "  $pkg : $([math]::Round($pkgSize,2)) MB"
        Add-Report "npm Global" $pkg $pkgSize "REVIEW"
    }
}

Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
$totalJunk = ($report | Where-Object { $_.Action -eq "DELETE" } | Measure-Object -Property SizeMB -Sum).Sum
$totalArchive = ($report | Where-Object { $_.Action -eq "ARCHIVE" } | Measure-Object -Property SizeMB -Sum).Sum
Write-Host "Immediate deletions: $([math]::Round($totalJunk,2)) MB"
Write-Host "Items to review/archive: $([math]::Round($totalArchive,2)) MB"

# Save report
$report | Format-Table -AutoSize | Out-String | Set-Content -Path "$workspace\audit-report.txt"
Write-Host ""
Write-Host "Full report saved to: $workspace\audit-report.txt"
