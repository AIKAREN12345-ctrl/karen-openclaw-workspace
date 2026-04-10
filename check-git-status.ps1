$workspace = "C:\Users\Karen\.openclaw\workspace"
Push-Location $workspace

try {
    $isGit = Test-Path ".git"
    if ($isGit) {
        Write-Output "Git repo exists"
        git remote -v
        Write-Output "---"
        git status --short
        Write-Output "---"
        git log --oneline -3
    } else {
        Write-Output "No git repo in workspace"
    }
} finally {
    Pop-Location
}
