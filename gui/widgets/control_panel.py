"""
コントロールパネルモジュール
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

class ControlPanel(QFrame):
    """コントロールパネルクラス"""
    start_clicked = pyqtSignal()  # 開始ボタンクリック時のシグナル
    cancel_clicked = pyqtSignal() # キャンセルボタンクリック時のシグナル

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        
        # ボタンを横に並べるレイアウト
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("文字起こし開始")
        self.run_button.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        self.run_button.clicked.connect(self.start_clicked.emit)
        button_layout.addWidget(self.run_button)
        
        self.cancel_button = QPushButton("中止")
        self.cancel_button.setFont(QFont("Helvetica", 12))
        self.cancel_button.clicked.connect(self.cancel_clicked.emit)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("ファイルを選択してください")
        layout.addWidget(self.status_label)

    def set_running(self, running: bool):
        """実行状態を設定"""
        self.run_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)
        if not running:
            self.progress_bar.setValue(0)

    def set_progress(self, value: int):
        """進捗を設定"""
        self.progress_bar.setValue(value)

    def set_status(self, text: str):
        """ステータスを設定"""
        self.status_label.setText(text)
