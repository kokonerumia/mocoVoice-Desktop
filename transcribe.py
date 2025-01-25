import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import requests
import os
from datetime import datetime
import time

class MocoVoiceClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.mocomoco.ai'
        self.headers = {'X-API-KEY': api_key}

    def transcribe(self, file_path, options=None):
        if options is None:
            options = {}

        # 1. アップロードURLを取得
        filename = os.path.basename(file_path)
        upload_data = {
            'filename': filename,
            'language': options.get('language', 'ja'),
            'transcription_model': 'timestamp' if options.get('timestamp') else 'default',
            'words': []
        }

        if options.get('speaker_diarization'):
            upload_data['words'].append({'word': '[SPEAKER_DIARIZATION]', 'reading': 'ON'})
        if options.get('punctuation'):
            upload_data['words'].append({'word': '[AUTO_PUNCTUATION]', 'reading': 'ON'})

        response = requests.post(
            f'{self.base_url}/api/v1/transcriptions/upload',
            headers=self.headers,
            json=upload_data
        )
        response.raise_for_status()
        data = response.json()

        # 2. 音声ファイルをアップロード
        with open(file_path, 'rb') as f:
            response = requests.put(
                data['audio_upload_url'],
                data=f,
                headers={'Content-Type': 'application/octet-stream'}
            )
            response.raise_for_status()

        # 3. 書き起こし開始
        response = requests.post(
            f'{self.base_url}/api/v1/transcriptions/{data["transcription_id"]}/transcribe',
            headers=self.headers
        )
        response.raise_for_status()

        return data['transcription_id']

    def get_transcription(self, transcription_id):
        response = requests.get(
            f'{self.base_url}/api/v1/transcriptions/{transcription_id}',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def wait_for_completion(self, transcription_id, progress_callback=None):
        while True:
            result = self.get_transcription(transcription_id)
            status = result['status']

            if progress_callback:
                progress_callback(status)

            if status == 'COMPLETED':
                return result
            elif status in ['FAILED', 'CANCELLED']:
                raise Exception(f'Transcription {status.lower()}')

            time.sleep(5)

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title('MocoVoice 文字起こし')
        self.root.geometry('1200x800')
        
        # メインフレームの作成
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 左右のパネルを作成
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ファイル選択部分
        self.file_frame = ttk.LabelFrame(self.left_panel, text='ファイル選択', padding=5)
        self.file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path, width=40)
        self.file_entry.grid(row=0, column=0, padx=5)
        
        self.browse_button = ttk.Button(self.file_frame, text='参照', command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=5)
        
        # オプション部分
        self.options_frame = ttk.LabelFrame(self.left_panel, text='オプション', padding=5)
        self.options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.speaker_diarization = tk.BooleanVar()
        self.timestamp = tk.BooleanVar()
        self.punctuation = tk.BooleanVar()
        
        ttk.Checkbutton(self.options_frame, text='話者分離', variable=self.speaker_diarization).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(self.options_frame, text='タイムスタンプ', variable=self.timestamp).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(self.options_frame, text='句読点の自動挿入', variable=self.punctuation).grid(row=2, column=0, sticky=tk.W)
        
        # 実行ボタン
        self.start_button = ttk.Button(self.left_panel, text='文字起こし開始', command=self.start_transcription)
        self.start_button.grid(row=2, column=0, pady=10)
        
        # ステータス表示
        self.status_label = ttk.Label(self.left_panel, text='状態: 待機中')
        self.status_label.grid(row=3, column=0, pady=5)
        
        # 結果表示部分
        self.result_frame = ttk.LabelFrame(self.right_panel, text='文字起こし結果', padding=5)
        self.result_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, width=60, height=40)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # スクロールバー
        self.scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text['yscrollcommand'] = self.scrollbar.set
        
        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)
        self.result_frame.columnconfigure(0, weight=1)
        self.result_frame.rowconfigure(0, weight=1)

        # APIキーの読み込み
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.api_key = config.get('apiKey')
                if not self.api_key or self.api_key == 'YOUR_API_KEY_HERE':
                    raise ValueError('APIキーが設定されていません')
        except Exception as e:
            messagebox.showerror('エラー', f'設定エラー: {str(e)}')
            self.root.destroy()
            return

    def browse_file(self):
        filetypes = (
            ('メディアファイル', '*.mp3 *.wav *.mov *.mp4 *.m4a *.aac *.wma *.ogg'),
            ('すべてのファイル', '*.*')
        )
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_path.set(filename)

    def update_status(self, status):
        status_messages = {
            'PENDING': '準備中...',
            'CONVERTING': '変換中...',
            'IN_PROGRESS': '文字起こし中...',
            'COMPLETED': '完了',
            'FAILED': 'エラー',
            'CANCELLED': 'キャンセル'
        }
        self.status_label['text'] = f'状態: {status_messages.get(status, status)}'
        self.root.update()

    def start_transcription(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror('エラー', 'ファイルを選択してください')
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror('エラー', 'ファイルが見つかりません')
            return

        self.start_button['state'] = 'disabled'
        self.result_text.delete('1.0', tk.END)
        self.update_status('アップロード中...')

        try:
            client = MocoVoiceClient(self.api_key)
            options = {
                'speaker_diarization': self.speaker_diarization.get(),
                'timestamp': self.timestamp.get(),
                'punctuation': self.punctuation.get()
            }

            transcription_id = client.transcribe(file_path, options)
            result = client.wait_for_completion(transcription_id, self.update_status)

            # 結果を保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(
                os.path.dirname(file_path),
                f'{os.path.splitext(os.path.basename(file_path))[0]}_{timestamp}.txt'
            )

            # 結果を取得してファイルに保存
            response = requests.get(result['transcription_path'])
            response.raise_for_status()
            transcription_text = response.text

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(transcription_text)

            # 結果を表示
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert('1.0', transcription_text)
            self.update_status('完了')
            messagebox.showinfo('完了', f'文字起こしが完了しました\n結果は {output_path} に保存されました')

        except Exception as e:
            messagebox.showerror('エラー', str(e))
            self.update_status('エラー')
        finally:
            self.start_button['state'] = 'normal'

def main():
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    root.withdraw()  # 初期化中は非表示
    
    try:
        app = TranscriptionApp(root)
        root.deiconify()  # 初期化完了後に表示
        root.mainloop()
    except Exception as e:
        print(f"Error: {str(e)}")
        messagebox.showerror('エラー', str(e))
        root.destroy()

if __name__ == '__main__':
    main()
