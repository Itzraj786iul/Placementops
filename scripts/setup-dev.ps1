#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$ApiDir = Join-Path $Root "apps\api"
$Venv = Join-Path $ApiDir ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
$Pip = Join-Path $Venv "Scripts\pip.exe"

Write-Host "==> PlacementOS native development setup" -ForegroundColor Cyan

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  Write-Error "Node.js is required. Install Node.js 20+."
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Error "Python is required. Install Python 3.12+."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  Write-Error "npm is required."
}

Write-Host "==> Installing Node dependencies"
Set-Location $Root
npm install

Write-Host "==> Setting up Python virtual environment"
if (-not (Test-Path $Venv)) {
  python -m venv $Venv
}
& $Pip install --upgrade pip
& $Pip install -r (Join-Path $ApiDir "requirements.txt")
& $Pip install pytest

Write-Host "==> Checking environment files"
$ApiEnv = Join-Path $ApiDir ".env"
if (-not (Test-Path $ApiEnv)) {
  Copy-Item (Join-Path $ApiDir ".env.example") $ApiEnv
  Write-Host 'Created apps/api/.env from example - update credentials before running.'
}
$WebEnv = Join-Path $Root "apps\web\.env.local"
if (-not (Test-Path $WebEnv)) {
  Copy-Item (Join-Path $Root "apps\web\.env.example") $WebEnv
  Write-Host "Created apps/web/.env.local from example."
}

Write-Host "==> Verifying PostgreSQL connection"
& $Python (Join-Path $Root "scripts\verify-postgres.py")
if ($LASTEXITCODE -ne 0) {
  Write-Host "WARNING: PostgreSQL check failed. Start PostgreSQL and run migrations manually:" -ForegroundColor Yellow
  Write-Host "  cd apps/api; .venv\Scripts\activate; alembic upgrade head"
  exit 1
}

Write-Host "==> Running database migrations"
Set-Location $ApiDir
& $Python -m alembic upgrade head

Write-Host "==> Seeding development login accounts"
& $Python (Join-Path $Root "scripts\seed-dev-users.py")

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "  Start API:  .\scripts\start-api.ps1"
Write-Host "  Start Web:  .\scripts\start-web.ps1"
Write-Host '  Or both:    npm run dev (from repo root)'
