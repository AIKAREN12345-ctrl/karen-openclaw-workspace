$workspace = "C:\Users\Karen\.openclaw\workspace"
$openclaw = "C:\Users\Karen\.openclaw"
$deleted = @()
$errors = @()

function Remove-Safe($path, $desc) {
    if (Test-Path $path) {
        try {
            Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
            $script:deleted += "$desc"
            Write-Host "DELETED: $desc" -ForegroundColor Green
        } catch {
            $script:errors += "FAILED: $desc - $($_.Exception.Message)"
            Write-Host "FAILED: $desc" -ForegroundColor Red
        }
    }
}

Write-Host "=== CLEANUP STARTED ===" -ForegroundColor Cyan

# 1. Workspace root junk
Remove-Safe "$workspace\1" "misnamed file '1' (26MB)"
Remove-Safe "$workspace\cloudflared-windows-amd64.exe" "cloudflared exe (16MB)"
Remove-Safe "$workspace\vnc_test_1914.png" "VNC test screenshot 1"
Remove-Safe "$workspace\vnc_after_click.png" "VNC test screenshot 2"
Remove-Safe "$workspace\vnc_screenshot.png" "VNC test screenshot 3"
Remove-Safe "$workspace\test.db" "test SQLite db"
Remove-Safe "$workspace\`$null" "null artifact"
Remove-Safe "$workspace\test-exec.txt" "test exec txt"
Remove-Safe "$workspace\test-subagent.txt" "test subagent txt"
Remove-Safe "$workspace\test-tool-check.txt" "test tool check"
Remove-Safe "$workspace\test-isolated-session.txt" "test isolated session"

# 2. Old project artifacts in workspace root
$oldPatterns = @(
    "analyze_excel.py","Butcher_Shop_Culture_Presentation.pptx","butcher_shop_culture_script.md",
    "butcher_shop_culture_script_v2.md","butcher_shop_presentation_outline.txt",
    "butcher_shop_slide_content_guide.md","butcher_shop_word_for_word_script.md",
    "Chocolate_Sales_Analysis.xlsx","Chocolate_Sales_Analysis_Complete.xlsx","Chocolate_Sales_Presentation.pptx",
    "condense_presentation.py","course_content.txt","create_analysis.py","create_analysis_formatted.py",
    "create_complete_workbook.py","create_essay.py","create_full_workbook.py","create_ppt.py",
    "create_presentation.py","create_script.py","enable-vnc-final.ps1","enable-vnc-screen.bat",
    "enable-vnc-screen.ps1","extracted_notes.txt","extract_notes.py","group_work.txt",
    "inspect_files.py","modelfile-qwen3.5-fixed","modelfile-qwen3.5-v2","new_doc_content.txt",
    "ollama-agent.yaml","organizational_culture_complete_notes.md","organizational_culture_notes.md",
    "Paddy_Power_IMC_Essay.docx","Paddy_Power_IMC_Presentation.pptx","Paddy_Power_IMC_Script.docx",
    "read_docx.py","read_excel.py","read_group_doc.py","read_new_doc.py","read_pptx_files.py",
    "restart-openclaw-with-screen.ps1","setup-memory-search.py","simple-heartbeat.ps1",
    "vnc-control.py","vnc-recorder-robust.py","vnc-screenshot-robust.py"
)
foreach ($p in $oldPatterns) {
    $fp = Join-Path $workspace $p
    if (Test-Path $fp) {
        Remove-Safe $fp $p
    }
}

# 3. .openclaw bloat
Remove-Safe "$openclaw\browser" "old browser directory (1.1GB)"
Remove-Safe "$openclaw\chrome-cdp-profile" "chrome CDP profile (191MB)"
Remove-Safe "$openclaw\qqbot" "unused qqbot directory"
Remove-Safe "$openclaw\temp-skills" "temp-skills directory"

# 4. Temp files older than 7 days
$openclawTemp = "C:\Users\Karen\AppData\Local\Temp\openclaw"
if (Test-Path $openclawTemp) {
    $oldTemp = Get-ChildItem -Path $openclawTemp -File -Recurse | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
    foreach ($f in $oldTemp) {
        Remove-Safe $f.FullName "old temp: $($f.Name)"
    }
}

# 5. node-red (if Ken confirms unused)
# Skipping for now — ask first

Write-Host ""
Write-Host "=== CLEANUP COMPLETE ===" -ForegroundColor Cyan
Write-Host "Deleted: $($deleted.Count) items"
if ($errors.Count -gt 0) {
    Write-Host "Errors: $($errors.Count)" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host $_ -ForegroundColor Red }
}
