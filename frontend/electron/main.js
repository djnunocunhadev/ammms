const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const isDev = process.env.NODE_ENV === 'development'

// Keep a global reference of the window object
let mainWindow

async function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 768,
    backgroundColor: '#1a1a1a',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  // Load the app
  if (isDev) {
    await mainWindow.loadURL('http://localhost:3000')
    mainWindow.webContents.openDevTools()
  } else {
    await mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // Emitted when the window is closed
  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// This method will be called when Electron has finished initialization
app.whenReady().then(createWindow)

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})

// Handle IPC messages
ipcMain.handle('get-app-path', () => {
  return app.getPath('userData')
})

// Handle Python backend process
let backendProcess = null

function startBackend() {
  const python = isDev ? 'python' : path.join(process.resourcesPath, 'backend/venv/bin/python')
  const scriptPath = isDev
    ? path.join(__dirname, '../../backend/main.py')
    : path.join(process.resourcesPath, 'backend/main.py')

  backendProcess = require('child_process').spawn(python, [scriptPath])

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`)
  })

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend stderr: ${data}`)
  })

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`)
  })
}

// Start backend when app is ready
app.on('ready', () => {
  startBackend()
})

// Clean up backend process on app quit
app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill()
  }
})