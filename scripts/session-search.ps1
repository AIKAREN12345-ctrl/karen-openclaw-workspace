# Session Archive Search Tool
# Search across all archived conversations
# Usage: powershell -File scripts/session-search.ps1 -Query "backup"

param(
    [Parameter(Mandatory=$true)]
    [string]$Query,
    
    [string]$DateFrom,
    [string]$DateTo,
    [int]$Limit = 20
)

$ArchiveRoot = "C:\Users\Karen\.openclaw\workspace\memory\session-archive"

Write-Host "🔍 Searching archives for: '$Query'"
Write-Host ""

$results = @()
$archives = Get-ChildItem $ArchiveRoot -Recurse -Filter "conversations.md" | Sort-Object FullName -Descending

$count = 0
foreach ($archive in $archives) {
    if ($count -ge $Limit) { break }
    
    $content = Get-Content $archive.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -match $Query) {
        $date = $archive.Directory.Name
        $results += [PSCustomObject]@{
            Date = $date
            Path = $archive.FullName
            Preview = if ($content.Length -gt 200) { $content.Substring(0, 200) + "..." } else { $content }
        }
        $count++
    }
}

if ($results.Count -eq 0) {
    Write-Host "No results found for '$Query'"
} else {
    Write-Host "Found $($results.Count) matches:`n"
    foreach ($r in $results) {
        Write-Host "📅 $($r.Date)" -ForegroundColor Cyan
        Write-Host "   $($r.Path)" -ForegroundColor Gray
        Write-Host ""
    }
}
