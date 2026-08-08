# Setup Windows Scheduled Task for OpenClaw Session Cleanup
# Run this once to create the daily cleanup task

$taskName = "OpenClaw-Session-Cleanup"
$taskDescription = "Daily cleanup of old OpenClaw sessions, checkpoints, and lock files"
$scriptPath = "C:\Users\Karen\.openclaw\workspace\scripts\session-cleanup.ps1"
$logPath = "C:\Users\Karen\.openclaw\workspace\memory\session-cleanup.log"

# Ensure the script exists
if (!(Test-Path $scriptPath)) {
    Write-Error "Cleanup script not found: $scriptPath"
    exit 1
}

# Create the scheduled task action
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""

# Create trigger: Daily at 23:00
$trigger = New-ScheduledTaskTrigger -Daily -At "23:00"

# Create task settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description $taskDescription -Force
    Write-Output "✅ Scheduled task '$taskName' created successfully"
    Write-Output "   Runs daily at 23:00"
    Write-Output "   Logs to: $logPath"
} catch {
    Write-Error "Failed to create scheduled task: $($_.Exception.Message)"
    exit 1
}
