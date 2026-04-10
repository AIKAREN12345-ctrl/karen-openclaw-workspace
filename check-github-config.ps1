$workspace = "C:\Users\Karen\.openclaw\workspace"
$gitDirs = Get-ChildItem -Path $workspace -Directory -Recurse -Filter ".git" -ErrorAction SilentlyContinue
if ($gitDirs) {
    $gitDirs | ForEach-Object { 
        $repoRoot = $_.Parent.FullName
        Push-Location $repoRoot
        $remote = git remote get-url origin 2>$null
        Pop-Location
        [PSCustomObject]@{
            Path = $repoRoot
            Remote = $remote
        }
    } | Format-Table -AutoSize
} else {
    Write-Output "No git repositories found in workspace"
}

$envFile = "$workspace\.env"
if (Test-Path $envFile) {
    Write-Output "---"
    Write-Output ".env file exists"
    Get-Content $envFile | Where-Object { $_ -like "*GITHUB*" -or $_ -like "*github*" }
}

$ghConfig = "$env:LOCALAPPDATA\GitHub\*"
if (Test-Path $ghConfig) {
    Write-Output "---"
    Write-Output "GitHub CLI config may exist"
}

try {
    $ghUser = gh api user -q .login 2>$null
    if ($ghUser) {
        Write-Output "---"
        Write-Output "GitHub CLI authenticated as: $ghUser"
    }
} catch {
    Write-Output "---"
    Write-Output "GitHub CLI not authenticated or not installed"
}
