const {app, BrowserWindow,ipcMain}= require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');
//const fs = require('fs');


function createwindow (){
    const win = new BrowserWindow({
        title: 'A.S.H',
        width: 700,
        height: 500,
        autoHideMenuBar: true,
        icon: path.join(__dirname, 'src/icon.png'),
        resizable: false,
        transparent: false,
        fullscreen: true,
        webPreferences: {
          nodeIntegration: true,
          preload: path.join(__dirname, 'preload.js'),
        },
    });

  
    win.loadFile('src/index.html');


    let pythonRunning = false;
    let python;
    let message="";
    
    ipcMain.on('execute-ash-ai', () => {
      pythonRunning = true;
      python = new PythonShell('src/ash_ai/main.py');
    
      python.on('message', (message) => {
        win.webContents.send('python-message', message);
      });
    
      python.on('close', () => {
        pythonRunning = false;
      });
    });
    
    ipcMain.on('send-python-message', (event, message) => {
      if (!pythonRunning) {
        win.webContents.send('execute-ash-ai');
      }
      message=mess
    });
    while(pythonRunning && message!==""){
      python.send(message);
      message="";
    }
  
  
}

app.whenReady().then(createwindow);


app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });
  