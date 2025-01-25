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
    process_clicked = pyqtSignal(str, str)  # 処理実行時のシグナル (プロンプト, 入力テキスト)

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
        
        # AI処理ボタンと保存ボタン
        ai_buttons = QHBoxLayout()
        
        process_button = QPushButton("AI処理実行")
        process_button.setFont(QFont("Helvetica", 11))
        process_button.clicked.connect(self.process_text)
        ai_buttons.addWidget(process_button)
        
        save_result_button = QPushButton("結果を保存")
        save_result_button.setFont(QFont("Helvetica", 11))
        save_result_button.clicked.connect(self.save_result)
        ai_buttons.addWidget(save_result_button)
        
        layout.addLayout(ai_buttons)

        # 結果表示エリア
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Helvetica", 11))
        self.result_text.setPlaceholderText("AI処理結果がここに表示されます")
        layout.addWidget(self.result_text)

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
        self.process_clicked.emit(prompt_text, self.result_text.toPlainText())

    def save_result(self):
        """処理結果を保存"""
        if not self.result_text.toPlainText():
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "AI処理結果を保存",
            "",
            "テキストファイル (*.txt);;すべてのファイル (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.toPlainText())
            except Exception as e:
                print(f"保存エラー: {str(e)}")

    def set_result(self, text: str):
        """処理結果を設定"""
        self.result_text.setText(text)

    def get_prompt(self) -> str:
        """現在のプロンプトを取得"""
        return self.prompt_edit.toPlainText()
