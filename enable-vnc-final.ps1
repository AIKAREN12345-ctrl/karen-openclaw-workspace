# Enable VNC Screen Recording for OpenClaw Node
# Run this to update the scheduled task with VNC environment variables

$taskName = "OpenClaw Node"
$vncPass = "Karen1234$"

Write-Host "Stopping OpenClaw Node task..."
Stop-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 3

Write-Host "Getting current task..."
$task = Get-ScheduledTask -TaskName $taskName

Write-Host "Creating new action with VNC environment variables..."
$argument = "-WindowStyle Hidden -Command `"`$env:OPENCLAW_NODE_SCREEN_ENABLED='true'; `$env:OPENCLAW_NODE_VNC_HOST='localhost'; `$env:OPENCLAW_NODE_VNC_PORT='5900'; `$env:OPENCLAW_NODE_VNC_PASSWORD='$vncPass'; node 'C:\Users\Karen\AppData\Roaming\npm\node_modules\openclaw\dist\index.js' node`""

$newAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argument

Write-Host "Updating scheduled task..."
Set-ScheduledTask -TaskName $taskName -Action $newAction

Write-Host "Starting task..."
Start-ScheduledTask -TaskName $taskName

Write-Host "Done! Waiting 10 seconds for node to connect..."
Start-Sleep -Seconds 10

Write-Host "Checking node capabilities..."
# This would need to be run separately after node connects
