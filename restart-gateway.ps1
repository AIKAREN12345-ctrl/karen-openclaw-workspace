Restart-Service -Name "OpenClawGateway" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Write-Output "Gateway restarted with new idle timeout"
