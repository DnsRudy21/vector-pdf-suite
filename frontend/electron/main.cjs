const { app, BrowserWindow, dialog, Menu } = require('electron')
const { spawn } = require('child_process')
const path = require('path')
const http = require('http')
const net = require('net')
const crypto = require('crypto')

let backend
let port
const shutdownToken = crypto.randomBytes(32).toString('hex')
function availablePort() { return new Promise(resolve => { const server = net.createServer(); server.listen(0, '127.0.0.1', () => { const selected = server.address().port; server.close(() => resolve(selected)) }) }) }
function waitForBackend(attempts = 120) {
  return new Promise((resolve, reject) => {
    const check = () => http.get(`http://127.0.0.1:${port}/api/health`, response => { response.resume(); resolve() }).on('error', () => attempts-- > 0 ? setTimeout(check, 150) : reject(new Error('El backend no pudo iniciar')))
    check()
  })
}
async function createWindow() {
  port = await availablePort()
  const executable = path.join(process.resourcesPath, 'backend', 'vector-pdf-backend.exe')
  const frontend = path.join(process.resourcesPath, 'frontend')
  backend = spawn(executable, [], { windowsHide: true, env: { ...process.env, PDFSUITE_PORT: String(port), PDFSUITE_SHUTDOWN_TOKEN: shutdownToken, PDFSUITE_FRONTEND_DIR: frontend, PDFSUITE_DATA_DIR: path.join(app.getPath('userData'), 'data') } })
  backend.on('error', error => dialog.showErrorBox('Vector PDF Suite', error.message))
  try { await waitForBackend() } catch (error) { dialog.showErrorBox('Error al iniciar', error.message); app.quit(); return }
  const window = new BrowserWindow({ width: 1280, height: 840, minWidth: 900, minHeight: 650, backgroundColor: '#070b14', show: false, webPreferences: { contextIsolation: true, sandbox: true } })
  window.once('ready-to-show', () => window.show())
  await window.loadURL(`http://127.0.0.1:${port}`)
}
Menu.setApplicationMenu(null)
app.whenReady().then(createWindow)
app.on('window-all-closed', () => app.quit())
app.on('before-quit', () => {
  if (port) { const request = http.request({ hostname: '127.0.0.1', port, path: `/api/desktop/shutdown?token=${shutdownToken}`, method: 'POST' }); request.on('error', () => {}); request.end() }
  if (backend) backend.kill()
})
