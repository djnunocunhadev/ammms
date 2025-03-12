const { contextBridge, ipcRenderer } = require('electron')

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // App info
    getAppPath: () => ipcRenderer.invoke('get-app-path'),
    
    // File system operations
    openFile: async () => {
      return await ipcRenderer.invoke('dialog:openFile')
    },
    openDirectory: async () => {
      return await ipcRenderer.invoke('dialog:openDirectory')
    },
    saveFile: async (data) => {
      return await ipcRenderer.invoke('dialog:saveFile', data)
    },
    
    // Settings
    getSettings: async () => {
      return await ipcRenderer.invoke('settings:get')
    },
    saveSettings: async (settings) => {
      return await ipcRenderer.invoke('settings:save', settings)
    },
    
    // Audio operations
    analyzeAudio: async (filePath) => {
      return await ipcRenderer.invoke('audio:analyze', filePath)
    },
    playAudio: async (filePath) => {
      return await ipcRenderer.invoke('audio:play', filePath)
    },
    pauseAudio: async () => {
      return await ipcRenderer.invoke('audio:pause')
    },
    stopAudio: async () => {
      return await ipcRenderer.invoke('audio:stop')
    },
    
    // Event listeners
    on: (channel, callback) => {
      // Whitelist channels
      const validChannels = [
        'audio:progress',
        'audio:complete',
        'audio:error',
        'settings:changed'
      ]
      if (validChannels.includes(channel)) {
        const subscription = (event, ...args) => callback(...args)
        ipcRenderer.on(channel, subscription)
        
        // Return a function to remove the event listener
        return () => {
          ipcRenderer.removeListener(channel, subscription)
        }
      }
    }
  }
)