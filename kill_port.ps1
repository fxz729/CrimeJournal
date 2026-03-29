$proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId = 53324" -ErrorAction SilentlyContinue
if ($proc) {
    Stop-Process -Id 53324 -Force -ErrorAction SilentlyContinue
    Write-Host "Killed PID 53324"
} else {
    Write-Host "Process 53324 not found"
}
Start-Sleep -Seconds 3
$remaining = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess
if ($remaining) {
    Write-Host "Still running: $remaining"
} else {
    Write-Host "Port 8000 is free"
}
