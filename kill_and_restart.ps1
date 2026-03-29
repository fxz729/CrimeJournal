$conn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($conn) {
    $pids = $conn.OwningProcess | Select-Object -Unique
    foreach ($p in $pids) {
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        Write-Host "Killed PID $p"
    }
    Start-Sleep -Seconds 3
    $remaining = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($remaining) {
        Write-Host "FAILED - Still running: $($remaining.OwningProcess)"
    } else {
        Write-Host "SUCCESS - Port 8000 is now free"
    }
} else {
    Write-Host "Port 8000 already free"
}
