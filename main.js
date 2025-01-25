const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const moment = require('moment');
const { transcribeFile } = require('./transcribe');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// ファイル選択ダイアログを開く
ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Media Files', extensions: ['mp3', 'wav', 'mov', 'mp4', 'm4a', 'aac', 'wma', 'ogg'] }
    ]
  });
  return result.filePaths[0];
});

// 文字起こし処理
ipcMain.handle('transcribe', async (event, { filePath, options }) => {
  try {
    const config = JSON.parse(fs.readFileSync('config.json', 'utf8'));
    const result = await transcribeFile(config.apiKey, filePath, options);
    
    // 結果をファイルに保存
    const timestamp = moment().format('YYYYMMDD_HHmmss');
    const outputPath = path.join(
      path.dirname(filePath),
      `${path.basename(filePath, path.extname(filePath))}_${timestamp}.txt`
    );
    
    fs.writeFileSync(outputPath, result.transcription_path);
    return { success: true, result, outputPath };
  } catch (error) {
    return { success: false, error: error.message };
  }
});
