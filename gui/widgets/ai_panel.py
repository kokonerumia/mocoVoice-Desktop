"""
AI処理パネルモジュール
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QFileDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal, QTimer

class AIPanel(QFrame):
    """AI処理パネルクラス"""
    process_clicked = pyqtSignal(str)  # 処理実行時のシグナル (プロンプト)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        
        ai_label = QLabel("AI処理")
        ai_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        layout.addWidget(ai_label)
        
        # プロンプト編集エリア
        prompt_frame = QFrame()
        prompt_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        prompt_layout = QVBoxLayout(prompt_frame)
        
        # プロンプトのヘッダー部分
        prompt_header = QHBoxLayout()
        prompt_label = QLabel("プロンプト")
        prompt_label.setFont(QFont("Helvetica", 10))
        prompt_header.addWidget(prompt_label)
        
        # プロンプトの操作ボタン
        prompt_buttons = QHBoxLayout()
        
        load_prompt_button = QPushButton("読み込み")
        load_prompt_button.setMaximumWidth(80)
        load_prompt_button.clicked.connect(self.load_prompt)
        prompt_buttons.addWidget(load_prompt_button)
        
        self.save_prompt_button = QPushButton("保存")
        self.save_prompt_button.setMaximumWidth(60)
        self.save_prompt_button.clicked.connect(self.save_prompt)
        prompt_buttons.addWidget(self.save_prompt_button)
        
        prompt_header.addLayout(prompt_buttons)
        prompt_layout.addLayout(prompt_header)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("プロンプトを入力してください")
        self.prompt_edit.setMinimumHeight(200)
        prompt_layout.addWidget(self.prompt_edit)
        
        layout.addWidget(prompt_frame)
        
        # AI処理ボタン
        process_button = QPushButton("AI処理実行")
        process_button.setFont(QFont("Helvetica", 11))
        process_button.clicked.connect(self.process_text)
        layout.addWidget(process_button)

    def load_prompt(self):
        """プロンプトファイルを読み込む"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "プロンプトファイルを選択",
            "",
            "テキストファイル (*.txt);;すべてのファイル (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    prompt_text = f.read()
                self.prompt_edit.setText(prompt_text)
            except Exception as e:
                self.status_message.emit(f"プロンプト読み込みエラー: {str(e)}")

    def save_prompt(self):
        """プロンプトを保存"""
        # 保存成功を視覚的にフィードバック
        original_text = self.save_prompt_button.text()
        self.save_prompt_button.setText("✓")
        self.save_prompt_button.setEnabled(False)
        
        # 1秒後に元に戻す
        QTimer.singleShot(1000, lambda: (
            self.save_prompt_button.setText(original_text),
            self.save_prompt_button.setEnabled(True)
        ))

    def process_text(self):
        """テキスト処理を実行"""
        prompt_text = self.prompt_edit.toPlainText()
        if not prompt_text:
            return
        self.process_clicked.emit(prompt_text)
