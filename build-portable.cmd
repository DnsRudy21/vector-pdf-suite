@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call install.cmd
if errorlevel 1 exit /b 1
echo [1/3] Compilando interfaz...
call corepack pnpm install --frozen-lockfile
call corepack pnpm --filter vector-pdf-suite build
if errorlevel 1 exit /b 1
echo [2/3] Empaquetando motor PDF...
pushd backend
"..\.venv\Scripts\python.exe" -m PyInstaller --clean --noconfirm vector-pdf-backend.spec
if errorlevel 1 (popd & exit /b 1)
popd
echo [3/3] Creando ejecutable portable...
call corepack pnpm --filter vector-pdf-suite portable:build
if errorlevel 1 exit /b 1
echo Portable creado en frontend\release-portable
endlocal
