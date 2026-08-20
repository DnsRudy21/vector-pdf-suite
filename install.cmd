@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python no esta instalado o no aparece en PATH.
  echo Instala Python 3.11 o posterior y vuelve a intentarlo.
  exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
  echo ERROR: Node.js no esta instalado o no aparece en PATH.
  echo Instala Node.js 20 o posterior y vuelve a intentarlo.
  exit /b 1
)

echo [1/3] Creando entorno virtual...
python -m venv .venv || exit /b 1

echo [2/3] Instalando backend...
".venv\Scripts\python.exe" -m pip install --upgrade pip || exit /b 1
".venv\Scripts\python.exe" -m pip install -r backend\requirements-dev.txt || exit /b 1

echo [3/3] Instalando frontend...
call corepack pnpm install --frozen-lockfile || exit /b 1

echo.
echo Instalacion completa. Ejecuta start.cmd
endlocal
