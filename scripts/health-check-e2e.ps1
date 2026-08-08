# End-to-End Health Check for OpenClaw
# This script actually TESTS functionality, doesn't just report status
# Run via: powershell C:\Users\Karen\.openclaw\workspace\scripts\health-check-e2e.ps1

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$logFile = "C:\Users\Karen\.openclaw\workspace\memory\health-checks.log"
$testFile = "C:\Users\Karen\.openclaw\workspace\.health-test-$([Guid]::NewGuid().ToString().Substring(0,8)).txt"

$results = @{
    timestamp = $timestamp
    tests = @()
    overall = "PASS"
}

function Test-ExecWorking {
    # Test 1: Can we actually write a file via exec?
    $testContent = "health-check-test-$timestamp"
    try {
        # This mimics what OpenClaw exec does
        $testContent | Out-File -FilePath $testFile -Encoding UTF8 -ErrorAction Stop
        $written = Get-Content $testFile -Raw
        if ($written.Trim() -eq $testContent) {
            return @{ name = "exec_write"; status = "PASS"; detail = "File write/read working" }
        } else {
            return @{ name = "exec_write"; status = "FAIL"; detail = "Content mismatch" }
        }
    } catch {
        return @{ name = "exec_write"; status = "FAIL"; detail = $_.Exception.Message }
    } finally {
        if (Test-Path $testFile) { Remove-Item $testFile -Force }
    }
}

function Test-PythonBlocked {
    # Test 2: Confirm Python is blocked (expected in 2026.3.2+)
    try {
        $output = python --version 2>&1
        return @{ name = "python_security"; status = "WARN"; detail = "Python unexpectedly allowed - security model changed?" }
    } catch {
        return @{ name = "python_security"; status = "PASS"; detail = "Python correctly blocked by security" }
    }
}

function Test-NodeConnection {
    # Test 3: Check if node is responding
    # We can't directly test this from PowerShell, but we can check the node.json
    $nodeConfig = "C:\Users\Karen\.openclaw\node.json"
    if (Test-Path $nodeConfig) {
        try {
            $config = Get-Content $nodeConfig | ConvertFrom-Json
            if ($config.id) {
                return @{ name = "node_config"; status = "PASS"; detail = "Node config present, ID: $($config.id.Substring(0,16))..." }
            }
        } catch {
            return @{ name = "node_config"; status = "FAIL"; detail = "Invalid node.json" }
        }
    }
    return @{ name = "node_config"; status = "FAIL"; detail = "node.json not found" }
}

function Test-OrphanedSessions {
    # Test 4: Check for orphaned sessions that could cause recovery loops
    $sessionsDir = "C:\Users\Karen\.openclaw\agents\main\sessions"
    if (Test-Path $sessionsDir) {
        # Count .jsonl files (excluding .deleted and .lock)
        $sessionFiles = Get-ChildItem $sessionsDir -Filter "*.jsonl" | Where-Object { 
            $_.Name -notlike "*.deleted.*" -and $_.Name -notlike "*.lock*"
        }
        $count = $sessionFiles.Count
        if ($count -gt 100) {
            return @{ name = "orphan_sessions"; status = "WARN"; detail = "High session count: $count (potential orphans)" }
        } else {
            return @{ name = "orphan_sessions"; status = "PASS"; detail = "Session count normal: $count" }
        }
    }
    return @{ name = "orphan_sessions"; status = "FAIL"; detail = "Sessions directory not found" }
}

function Test-DiskSpace {
    # Test 5: Check disk space
    $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
    $freePercent = [math]::Round(($disk.FreeSpace / $disk.Size) * 100, 1)
    if ($freePercent -lt 10) {
        return @{ name = "disk_space"; status = "FAIL"; detail = "Critical: $freePercent% free" }
    } elseif ($freePercent -lt 20) {
        return @{ name = "disk_space"; status = "WARN"; detail = "Low: $freePercent% free" }
    } else {
        return @{ name = "disk_space"; status = "PASS"; detail = "OK: $freePercent% free" }
    }
}

# Run all tests
$results.tests += Test-ExecWorking
$results.tests += Test-PythonBlocked
$results.tests += Test-NodeConnection
$results.tests += Test-OrphanedSessions
$results.tests += Test-DiskSpace

# Determine overall status
$failures = $results.tests | Where-Object { $_.status -eq "FAIL" }
$warnings = $results.tests | Where-Object { $_.status -eq "WARN" }

if ($failures.Count -gt 0) {
    $results.overall = "FAIL"
} elseif ($warnings.Count -gt 0) {
    $results.overall = "WARN"
}

# Format output
$output = @"
## Health Check - $timestamp

**Overall: $($results.overall)**

| Test | Status | Detail |
|------|--------|--------|
"@

foreach ($test in $results.tests) {
    $emoji = switch ($test.status) {
        "PASS" { "✅" }
        "WARN" { "⚠️" }
        "FAIL" { "❌" }
    }
    $output += "| $($test.name) | $emoji $($test.status) | $($test.detail) |`n"
}

$output += "`n---`n"

# Append to log
$output | Out-File -FilePath $logFile -Append -Encoding UTF8

# Also write latest result to a status file for easy checking
$statusFile = "C:\Users\Karen\.openclaw\workspace\.health-status.json"
$results | ConvertTo-Json -Depth 10 | Out-File -FilePath $statusFile -Encoding UTF8

# Output to console (will be swallowed by OpenClaw exec, but available if run manually)
Write-Output $output

# Return exit code for automation
if ($results.overall -eq "FAIL") { exit 1 }
exit 0
