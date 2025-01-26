"""
ログ表示ダイアログモジュール
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class LogDialog(QDialog):
    """ログ表示ダイアログクラス"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        """UIの初期化"""
        self.setWindowTitle("ログ")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout(self)
        
        # ログ表示エリア
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Menlo", 11))
        layout.addWidget(self.log_text)
        
        # 閉じるボタン
        close_button = QPushButton("閉じる")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("""
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
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        
    def append_log(self, message: str):
        """ログを追加"""
        self.log_text.append(message)
        # 自動スクロール
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_log(self):
        """ログをクリア"""
        self.log_text.clear()
