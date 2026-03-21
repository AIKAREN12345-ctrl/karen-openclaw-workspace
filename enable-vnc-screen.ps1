# Enable VNC Screen Recording for OpenClaw Node
# Run this script to update the scheduled task with VNC environment variables

$taskName = "OpenClaw Node"
$vncPass = $env:VNC_PASS

# Get the existing task
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if (-not $task) {
    Write-Error "Task '$taskName' not found!"
    exit 1
}

# Get the current action
$action = $task.Actions[0]

# Create new action with environment variables
$newAction = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-WindowStyle Hidden -Command `"`$env:OPENCLAW_NODE_SCREEN_ENABLED='true'; `$env:OPENCLAW_NODE_VNC_HOST='localhost'; `$env:OPENCLAW_NODE_VNC_PORT='5900'; `$env:OPENCLAW_NODE_VNC_PASSWORD='$vncPass'; node '$($action.Execute)' node`""

# Update the task
Set-ScheduledTask -TaskName $taskName -Action $newAction -Force

Write-Host "✅ OpenClaw Node task updated with VNC screen support"
Write-Host "Restarting task..."

# Restart the task
Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-ScheduledTask -TaskName $taskName

Write-Host "✅ Task restarted. Screen recording should be available in ~10 seconds"
