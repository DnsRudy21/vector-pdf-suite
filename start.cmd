@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: No se encontro el entorno virtual. Ejecuta install.cmd primero.
  exit /b 1
)

if not exist "frontend\node_modules" (
  echo ERROR: Faltan las dependencias del frontend. Ejecuta install.cmd primero.
  exit /b 1
)

echo Iniciando Vector PDF Suite...
start "Vector PDF Suite API" /D "%~dp0backend" "%~dp0.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port 8000
call corepack pnpm --filter vector-pdf-suite dev
endlocal
