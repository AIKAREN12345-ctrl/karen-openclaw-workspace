$extensionDirs = @(
    "C:\Users\Karen\.openclaw\extensions",
    "C:\Users\Karen\AppData\Local\Google\Chrome\User Data\Default\Extensions"
)

foreach ($dir in $extensionDirs) {
    if (Test-Path $dir) {
        Get-ChildItem -Path $dir -Recurse -Filter "*openclaw*" -ErrorAction SilentlyContinue | Select-Object FullName
    }
}

$ports = @(18792, 18793, 18800, 9222, 3456)
foreach ($port in $ports) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Output "PORT $port : LISTENING"
    } else {
        Write-Output "PORT $port : DOWN"
    }
}
