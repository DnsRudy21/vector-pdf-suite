$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
python -m venv (Join-Path $ProjectRoot '.venv')
& (Join-Path $ProjectRoot '.venv\Scripts\python.exe') -m pip install --upgrade pip
& (Join-Path $ProjectRoot '.venv\Scripts\pip.exe') install -r (Join-Path $ProjectRoot 'backend\requirements-dev.txt')
corepack pnpm install --frozen-lockfile
Write-Host 'Instalación completa. Ejecuta .\start.ps1'
