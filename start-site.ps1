$ErrorActionPreference = "Stop"

$backendDir = Join-Path $PSScriptRoot "backend"
$frontendDir = Join-Path $PSScriptRoot "frontend"
$python = Join-Path $backendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Backend virtual environment was not found. Create backend\.venv first."
}
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    throw "Frontend dependencies are missing. Run 'npm install' in the frontend folder first."
}

$quotedBackend = $backendDir.Replace("'", "''")
$quotedPython = $python.Replace("'", "''")
$backendCommand = "Set-Location -LiteralPath '$quotedBackend'; & '$quotedPython' manage.py runserver 127.0.0.1:8000"

Start-Process -FilePath "powershell.exe" `
    -WorkingDirectory $backendDir `
    -ArgumentList @("-NoExit", "-Command", $backendCommand) | Out-Null

Start-Process -FilePath "powershell.exe" `
    -WorkingDirectory $frontendDir `
    -ArgumentList @("-NoExit", "-Command", "npm.cmd run dev") | Out-Null

Write-Host "Started the backend and frontend in separate PowerShell windows (without running migrations or seed)."
Write-Host "Frontend: http://localhost:3500/fa"
Write-Host "Backend:  http://127.0.0.1:8000"
