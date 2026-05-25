$ErrorActionPreference = "Stop"

$Distro = "Ubuntu-24.04"
$ProjectWinPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Drive = $ProjectWinPath.Substring(0, 1).ToLowerInvariant()
$ProjectWslPath = "/mnt/$Drive" + $ProjectWinPath.Substring(2).Replace("\", "/")

Write-Host "Project: $ProjectWinPath"
Write-Host "WSL: $Distro"

Write-Host "Stopping existing bot..."
& wsl.exe -d $Distro -- bash -lc "pkill -f 'python -m app.main' || true"

Write-Host "Starting PostgreSQL..."
& wsl.exe -d $Distro -- bash -lc "service postgresql status >/dev/null 2>&1 || sudo -n service postgresql start || true"

Write-Host "Running database migrations..."
& wsl.exe -d $Distro -- bash -lc "cd '$ProjectWslPath' && .venv-wsl/bin/python -m app.storage.migrate"

Write-Host "Starting bot..."
$botProcess = Start-Process `
    -FilePath "wsl.exe" `
    -ArgumentList @("-d", $Distro, "--", "bash", "-lc", "cd '$ProjectWslPath' && exec .venv-wsl/bin/python -m app.main") `
    -WorkingDirectory $ProjectWinPath `
    -WindowStyle Hidden `
    -PassThru

Start-Sleep -Seconds 5

Write-Host "Current WSL processes:"
& wsl.exe -d $Distro -- bash -lc "pgrep -af 'python -m app.main' || true"
