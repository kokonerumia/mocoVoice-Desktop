"""
メインウィンドウモジュール
"""
import os
import json
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QFrame, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from moco_client import MocoVoiceClient
from gpt_processor import GPTProcessor
from .widgets import (
    FilePanel,
    OptionsPanel,
    ControlPanel,
    AIPanel,
    ResultPanel
)
from .widgets.log_dialog import LogDialog
from .transcription_worker import TranscriptionWorker

class TranscriptionGUI(QMainWindow):
    """文字起こしGUIクラス"""
    def __init__(self):
        super().__init__()
        self.worker = None
        self.is_dark_mode = True
        self.log_dialog = LogDialog(self)
        self.initUI()

    def initUI(self):
        """UIの初期化"""
        self.setWindowTitle("mocoVoice Desktop")
        self.setMinimumWidth(1200)
        self.setMinimumHeight(800)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # 左パネル (操作パネル)
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        
        # 各パネルを追加
        self.file_panel = FilePanel()
        self.options_panel = OptionsPanel()
        self.control_panel = ControlPanel()
        self.ai_panel = AIPanel()
        
        left_layout.addWidget(self.file_panel)
        left_layout.addWidget(self.options_panel)
        left_layout.addWidget(self.control_panel)
        left_layout.addWidget(self.ai_panel)
        left_layout.addStretch()
        
        # 右パネル (結果表示パネル)
        self.result_panel = ResultPanel()
        self.result_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        
        # 左パネル下部のボタンエリア
        bottom_buttons = QHBoxLayout()
        
        # ログ表示ボタン
        log_button = QPushButton("ログを表示")
        log_button.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #888888;
            }
        """)
        log_button.clicked.connect(self.show_log_dialog)
        bottom_buttons.addWidget(log_button)
        
        # テーマ切り替えボタン
        theme_button = QPushButton("🌓")
        theme_button.setFixedSize(30, 30)
        theme_button.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 15px;
                background-color: #666666;
                color: white;
            }
            QPushButton:hover {
                background-color: #888888;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)
        theme_button.clicked.connect(self.toggle_theme)
        bottom_buttons.addWidget(theme_button)
        
        # 左パネルにボタンエリアを追加
        left_layout.addLayout(bottom_buttons)
        
        # レイアウトの追加
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(self.result_panel, 2)
        
        # スタイル設定
        self.setStyle()
        
        # シグナル接続
        self.connectSignals()
        
        # APIキーの読み込みとクライアントの初期化
        self.initClients()

    def setStyle(self):
        """スタイルの設定"""
        palette = QPalette()
        if self.is_dark_mode:
            # ダークモードパレット
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            self.setPalette(palette)
        else:
            # ライトモードパレット
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
            
            self.setPalette(palette)

    def toggle_theme(self):
        """テーマの切り替え"""
        self.is_dark_mode = not self.is_dark_mode
        self.setStyle()

    def connectSignals(self):
        """シグナルの接続"""
        # ファイルパネルのシグナル
        self.file_panel.file_selected.connect(lambda _: self.result_panel.clear_all())
        self.file_panel.text_loaded.connect(self.on_text_loaded)
        self.file_panel.transcription_ready.connect(self.start_transcription)
        
        # コントロールパネルのシグナル
        self.control_panel.start_clicked.connect(self.prepare_transcription)
        self.control_panel.cancel_clicked.connect(self.cancel_transcription)
        
        # AIパネルのシグナル
        self.ai_panel.process_clicked.connect(self.process_with_ai)

    def initClients(self):
        """クライアントの初期化"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                api_key = config.get('mocoVoiceApiKey')
                if not api_key or api_key == 'YOUR_MOCO_VOICE_API_KEY':
                    raise ValueError('APIキーが設定されていません')
                self.client = MocoVoiceClient(api_key)
        except Exception as e:
            self.control_panel.set_status(f'設定エラー: {str(e)}')
            self.control_panel.set_running(False)
            return

        # GPTProcessorの初期化
        self.gpt_processor = None
        try:
            self.gpt_processor = GPTProcessor()
            # 保存されているプロンプトを読み込む
            self.ai_panel.prompt_edit.setText(self.gpt_processor.prompt)
        except Exception as e:
            self.control_panel.set_status(f'AI設定エラー: {str(e)}')

    def prepare_transcription(self):
        """文字起こしの準備を開始"""
        input_path = self.file_panel.get_input_path()
        
        if input_path == "ファイルが選択されていません":
            self.control_panel.set_status("入力ファイルを選択してください")
            return
            
        if not os.path.exists(input_path):
            self.control_panel.set_status("入力ファイルが見つかりません")
            return
            
        self.control_panel.set_running(True)
        self.result_panel.clear_all()
        self.log_dialog.clear_log()
        
        try:
            # 音声ファイルの準備を開始
            self.file_panel.prepare_audio_for_transcription()
        except Exception as e:
            self.control_panel.set_status(f"エラー: {str(e)}")
            self.control_panel.set_running(False)
        
    def start_transcription(self, audio_path: str):
        """音声ファイルの準備が完了したら文字起こしを開始"""
        if not audio_path:
            self.control_panel.set_status("音声ファイルの準備に失敗しました")
            self.control_panel.set_running(False)
            return
            
        try:
            options = self.options_panel.get_options()
            self.worker = TranscriptionWorker(self.client, audio_path, options)
            self.worker.status.connect(self.control_panel.set_status)
            self.worker.debug.connect(self.log_dialog.append_log)
            self.worker.progress.connect(self.control_panel.set_progress)
            self.worker.finished.connect(self.on_transcription_complete)
            self.worker.error.connect(self.on_transcription_error)
            self.worker.start()
        except Exception as e:
            self.control_panel.set_status(f"文字起こしの開始に失敗しました: {str(e)}")
            self.control_panel.set_running(False)

    def cancel_transcription(self):
        """文字起こしを中止"""
        if self.worker:
            self.worker.cancel()
            self.control_panel.set_running(False)

    def on_transcription_complete(self, text: str):
        """文字起こし完了時の処理"""
        # 文字起こし結果はJSONファイルとして保存されないため、ファイルパスはNone
        self.result_panel.set_result(text, None)
        self.result_panel.switch_to_tab(1)  # 結果タブに切り替え
        self.control_panel.set_running(False)

    def on_transcription_error(self, error_message: str):
        """文字起こしエラー時の処理"""
        error_guidance = """
エラーが発生しました:
{error_message}

考えられる原因:
1. サーバーが一時的に混雑している
2. サーバーがメンテナンス中
3. ネットワーク接続に問題がある

対処方法:
1. しばらく時間をおいて再試行してください
2. ネットワーク接続を確認してください
3. 問題が続く場合は、サポートにお問い合わせください
"""
        self.log_dialog.append_log(error_guidance.format(error_message=error_message))
        self.control_panel.set_status("エラーが発生しました。詳細はログを確認してください。")
        self.show_log_dialog()  # エラー時は自動的にログを表示
        self.control_panel.set_running(False)

    def on_text_loaded(self, data: tuple):
        """テキスト読み込み時の処理"""
        text, file_path = data
        self.result_panel.set_result(text, file_path)
        self.result_panel.switch_to_tab(0)  # 結果タブに切り替え
        self.control_panel.set_status("テキストファイルを読み込みました")

    def process_with_ai(self, prompt: str):
        """AI処理を実行"""
        if not self.gpt_processor:
            self.control_panel.set_status("AI処理機能が初期化されていません")
            return

        # 文字起こし結果のテキストを取得
        text = self.result_panel.get_result()
        if not text:
            self.control_panel.set_status("文字起こし結果のテキストがありません")
            return

        if not prompt:
            self.control_panel.set_status("プロンプトを入力してください")
            return

        try:
            # プロンプトを保存してからAI処理を実行
            self.gpt_processor.save_prompt(prompt)
            processed_text = self.gpt_processor.process_text(text)
            
            # 結果を表示
            self.result_panel.set_ai_result(processed_text)
            self.result_panel.switch_to_tab(1)  # AI処理結果タブに切り替え
            self.control_panel.set_status("AI処理完了")
            
        except Exception as e:
            error_message = f"AI処理エラー: {str(e)}"
            self.control_panel.set_status(error_message)
            self.log_dialog.append_log(error_message)
            self.show_log_dialog()

    def show_log_dialog(self):
        """ログダイアログを表示"""
        self.log_dialog.exec()
