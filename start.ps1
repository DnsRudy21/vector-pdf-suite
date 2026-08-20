$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Start-Process -FilePath (Join-Path $ProjectRoot '.venv\Scripts\python.exe') -ArgumentList '-m','uvicorn','app.main:app','--reload','--port','8000' -WorkingDirectory (Join-Path $ProjectRoot 'backend') -PassThru -WindowStyle Hidden
try {
  Push-Location $ProjectRoot
  corepack pnpm --filter vector-pdf-suite dev
} finally {
  Pop-Location
  Stop-Process -Id $Backend.Id -ErrorAction SilentlyContinue
}
