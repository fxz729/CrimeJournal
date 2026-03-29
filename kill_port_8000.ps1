$pids = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess
foreach ($pid in $pids) {
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
}
Write-Host "Killed PIDs: $pids"
Start-Sleep -Seconds 3
$remaining = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess
if ($remaining) {
    Write-Host "Still running: $remaining"
} else {
    Write-Host "Port 8000 is now free"
}
