const { contextBridge, ipcRenderer } = require('electron');

// Expose only the necessary parts of the Electron API to the renderer process
contextBridge.exposeInMainWorld('electron', {
  ipcRenderer: ipcRenderer,
  executeAshAi: () => {
    ipcRenderer.send('execute-ash-ai');
  },
  receivePythonMessage: (message) => {
    ipcRenderer.send('python-message', message);
  },
  sendpythonmessage: (message) => {
    ipcRenderer.send('send-python-message', message);
  },
  pythonsay: (func) => {
    ipcRenderer.on('python-message', (event, message) => func(message));
  }
});
