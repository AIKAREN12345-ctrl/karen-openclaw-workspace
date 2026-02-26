# Karen Monitoring Service Installer
# Run as Administrator

$serviceName = "KarenMonitor"
$serviceDisplayName = "Karen Monitoring Agent"
$serviceDescription = "Autonomous monitoring and alerting for Karen AI system"
$pythonPath = "C:\Users\Karen\AppData\Local\Programs\Python\Python311\python.exe"
$scriptPath = "C:\Users\Karen\.openclaw\workspace\monitoring\karen_monitor.py"

Write-Host "Installing Karen Monitoring Service..." -ForegroundColor Green

# Check if running as admin
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "Please run as Administrator"
    exit 1
}

# Remove existing service if present
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Removing existing service..."
    Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
    sc.exe delete $serviceName | Out-Null
    Start-Sleep -Seconds 2
}

# Create service
Write-Host "Creating Windows service..."
$binPath = "`"$pythonPath`" `"$scriptPath`""
sc.exe create $serviceName binPath= $binPath start= auto DisplayName= $serviceDisplayName | Out-Null

# Set description
sc.exe description $serviceName $serviceDescription | Out-Null

# Start service
Write-Host "Starting service..."
Start-Service -Name $serviceName

# Check status
$service = Get-Service -Name $serviceName
Write-Host "Service status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq 'Running') { 'Green' } else { 'Red' })

Write-Host "`nKaren Monitoring Agent installed!" -ForegroundColor Green
Write-Host "Logs: C:\Users\Karen\.openclaw\workspace\monitoring\monitor.log"
Write-Host "Alerts: C:\Users\Karen\.openclaw\workspace\monitoring\alerts.log"
Write-Host "`nDon't forget to configure Telegram in config.json!"
