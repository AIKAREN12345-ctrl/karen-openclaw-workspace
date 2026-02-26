# Karen Monitoring - Scheduled Task Setup
# Run as Administrator

$taskName = "KarenMonitor"
$pythonPath = "C:\Users\Karen\AppData\Local\Programs\Python\Python311\python.exe"
$scriptPath = "C:\Users\Karen\.openclaw\workspace\monitoring\karen_monitor.py"

Write-Host "Setting up Karen Monitoring as Scheduled Task..." -ForegroundColor Green

# Remove existing task
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath

# Create trigger (run at startup and every 5 minutes)
$trigger1 = New-ScheduledTaskTrigger -AtStartup
$trigger2 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($trigger1, $trigger2) -Settings $settings -Description "Karen AI Monitoring Agent" | Out-Null

# Start task
Start-ScheduledTask -TaskName $taskName

# Check status
$task = Get-ScheduledTask -TaskName $taskName
Write-Host "Task status: $($task.State)" -ForegroundColor $(if ($task.State -eq 'Ready') { 'Green' } else { 'Yellow' })

Write-Host "`nKaren Monitoring Agent scheduled!" -ForegroundColor Green
Write-Host "Runs every 5 minutes + at startup"
Write-Host "Logs: C:\Users\Karen\.openclaw\workspace\monitoring\monitor.log"
