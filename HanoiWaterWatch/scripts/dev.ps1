param(
  [string]$Python = "python",
  [switch]$SkipInstall,
  [switch]$SkipBuild
)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
function New-DemoSecret {
  $secretBytes = New-Object byte[] 32
  $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
  try { $generator.GetBytes($secretBytes) } finally { $generator.Dispose() }
  return ([System.BitConverter]::ToString($secretBytes)).Replace("-", "").ToLowerInvariant()
}
if (-not (Test-Path -LiteralPath '.env.local')) {
  $databasePath = (Join-Path $projectRoot '.local/waterwatch.db').Replace('\','/')
  New-Item -ItemType Directory -Force -Path '.local' | Out-Null
  $localSettings = @(
    "DATABASE_URL=sqlite:///$databasePath",
    "JWT_SECRET=$(New-DemoSecret)",
    'COOKIE_SECURE=false',
    'DEMO_MODE=true',
    'REPLAY_TLH_ENABLED=true',
    'DEMO_OPERATOR_USERNAME=demo.operator',
    "DEMO_OPERATOR_PASSWORD=$(New-DemoSecret)",
    'DEMO_REVIEWER_USERNAME=demo.reviewer',
    "DEMO_REVIEWER_PASSWORD=$(New-DemoSecret)",
    'DEMO_ADMIN_USERNAME=demo.admin',
    "DEMO_ADMIN_PASSWORD=$(New-DemoSecret)"
  )
  [System.IO.File]::WriteAllLines((Join-Path $projectRoot '.env.local'), $localSettings)
  Write-Host 'Created local demo accounts. Read .env.local for your private sign-in details.'
}
foreach ($settingLine in Get-Content -LiteralPath '.env.local') {
  if ($settingLine -match '^([A-Z_]+)=(.*)$') {
    [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], 'Process')
  }
}
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
  & $Python -m venv .venv
  if ($LASTEXITCODE -ne 0) { throw 'Python 3.10 or later is required. Supply -Python with its full executable path.' }
}
$projectPython = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not $SkipInstall) {
  & $projectPython -m pip install -r backend/requirements.txt
  if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed.' }
}
if (-not $SkipBuild) {
  Push-Location frontend
  try {
    & npm.cmd ci
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
  } finally { Pop-Location }
}
$env:PYTHONPATH = Join-Path $projectRoot 'backend'
$env:FRONTEND_DIST = Join-Path $projectRoot 'frontend/dist'
Push-Location backend
try {
  & $projectPython -m alembic upgrade head
  if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
  & $projectPython -m app.cli seed
  if ($LASTEXITCODE -ne 0) { throw 'Database seeding failed.' }
  Write-Host 'Hanoi WaterWatch: http://127.0.0.1:8000'
  & $projectPython -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
} finally { Pop-Location }

