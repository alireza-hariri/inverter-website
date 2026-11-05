$ErrorActionPreference = "Stop"

$backendDir = Join-Path $PSScriptRoot "backend"
$frontendDir = Join-Path $PSScriptRoot "frontend"

if (-not (Get-Command "npm.cmd" -ErrorAction SilentlyContinue)) {
    throw "Node.js/npm was not found. Install Node.js, then run this script again."
}

$uv = Get-Command "uv" -ErrorAction SilentlyContinue
if ($uv) {
    $backendCommand = "uv run python manage.py runserver"
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $backendCommand = "python manage.py runserver"
} else {
    throw "Python was not found. Install Python 3.12+ (or uv), then run this script again."
}

if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    throw "Frontend dependencies are missing. Run 'npm install' in the frontend folder first."
}

Push-Location $backendDir
try {
    if ($uv) {
        & uv run python manage.py migrate --noinput
    } else {
        & python manage.py migrate --noinput
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Database migrations failed; services were not started."
    }

    if ($uv) {
        & uv run python manage.py seed
    } else {
        & python manage.py seed
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Database seeding failed; services were not started."
    }
} finally {
    Pop-Location
}

Start-Process -FilePath "powershell.exe" `
    -WorkingDirectory $backendDir `
    -ArgumentList @("-NoExit", "-Command", $backendCommand) | Out-Null

Start-Process -FilePath "powershell.exe" `
    -WorkingDirectory $frontendDir `
    -ArgumentList @("-NoExit", "-Command", "npm.cmd run dev") | Out-Null

Write-Host "Started the backend and frontend in separate PowerShell windows."
Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend:  http://127.0.0.1:8000"
