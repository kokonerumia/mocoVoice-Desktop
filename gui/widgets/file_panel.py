"""
ファイル選択パネルモジュール
"""
import os
import wave
import tempfile
import webbrowser
import pyaudio
from datetime import datetime
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from moco_client import MIME_TYPES
from ..media_converter import MediaConverter

class AudioRecorder(QThread):
    """音声録音スレッドクラス"""
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.is_recording = True
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        
    def run(self):
        """録音を実行"""
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )
        
        while self.is_recording:
            data = self.stream.read(1024)
            self.frames.append(data)
            
        self.stream.stop_stream()
        self.stream.close()
        
        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))
            
        self.audio.terminate()
        
    def stop(self):
        """録音を停止"""
        self.is_recording = False

class FilePanel(QFrame):
    recording_started = pyqtSignal()  # 録音開始時のシグナル
    recording_stopped = pyqtSignal()  # 録音停止時のシグナル
    """ファイル選択パネルクラス"""
    file_selected = pyqtSignal(str)  # ファイル選択時のシグナル
    text_loaded = pyqtSignal(str)    # テキスト読み込み時のシグナル

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recorder = None
        self.is_recording = False
        self.temp_dir = tempfile.gettempdir()
        self.initUI()

    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # ロゴ部分
        logo_frame = QFrame()
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        # ロゴラベル
        logo_label = QLabel()
        pixmap = QPixmap('mocovoice-logo.png')
        scaled_pixmap = pixmap.scaled(200, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # カーソルを手の形に
        logo_label.mousePressEvent = lambda _: webbrowser.open('https://docs.mocomoco.ai/')
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        layout.addWidget(logo_frame)

        # ファイル選択部分
        file_frame = QFrame()
        file_layout = QVBoxLayout(file_frame)
        
        self.input_path_label = QLabel("ファイルが選択されていません")
        file_layout.addWidget(self.input_path_label)
        
        button_layout = QHBoxLayout()
        
        browse_button = QPushButton("音声ファイルを選択")
        browse_button.clicked.connect(self.browse_input_file)
        button_layout.addWidget(browse_button)
        
        self.record_button = QPushButton("録音")
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.record_button)
        
        load_text_button = QPushButton("テキストを読み込む")
        load_text_button.clicked.connect(self.load_text_file)
        button_layout.addWidget(load_text_button)
        
        file_layout.addLayout(button_layout)
        layout.addWidget(file_frame)

    def browse_input_file(self):
        """音声/動画ファイルを選択"""
        # 音声ファイルの拡張子
        audio_extensions = list(MIME_TYPES.keys())
        # 動画ファイルの拡張子
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv']
        
        # 全ての対応拡張子を結合
        all_extensions = audio_extensions + video_extensions
        extensions_filter = " ".join(f"*{ext}" for ext in all_extensions)
        
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "音声/動画ファイルを選択",
            "",
            f"メディアファイル ({extensions_filter});;すべてのファイル (*.*)"
        )
        
        if file_name:
            try:
                # 動画ファイルの場合は音声を抽出
                audio_path = MediaConverter.convert_to_audio(file_name)
                self.input_path_label.setText(audio_path)
                self.file_selected.emit(audio_path)
            except Exception as e:
                self.text_loaded.emit(f"メディア変換エラー: {str(e)}")

    def load_text_file(self):
        """テキストファイルを読み込む"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "テキストファイルを選択",
            "",
            "テキストファイル (*.txt);;すべてのファイル (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.input_path_label.setText(file_name)
                self.text_loaded.emit(text)
            except Exception as e:
                self.text_loaded.emit(f"テキストファイル読み込みエラー: {str(e)}")

    def toggle_recording(self):
        """録音の開始/停止を切り替え"""
        if not self.is_recording:
            # 録音開始
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.temp_dir, f"recording_{timestamp}.wav")
            
            self.recorder = AudioRecorder(filename)
            self.recorder.finished.connect(self.on_recording_finished)
            self.recorder.start()
            
            self.is_recording = True
            self.record_button.setText("録音停止")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.recording_started.emit()
        else:
            # 録音停止
            if self.recorder:
                self.recorder.stop()
                self.is_recording = False
                self.record_button.setText("録音")
                self.record_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                self.recording_stopped.emit()

    def on_recording_finished(self):
        """録音完了時の処理"""
        if self.recorder:
            self.input_path_label.setText(self.recorder.filename)
            self.file_selected.emit(self.recorder.filename)
            self.recorder = None

    def get_input_path(self) -> str:
        """入力パスを取得"""
        return self.input_path_label.text()
