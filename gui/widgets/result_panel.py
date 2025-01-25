"""
結果表示パネルモジュール
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QTabWidget, QTextEdit
from PyQt6.QtGui import QFont

class ResultPanel(QFrame):
    """結果表示パネルクラス"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        
        # ログタブ
        self.debug_text = QTextEdit()
        self.debug_text.setReadOnly(True)
        self.debug_text.setFont(QFont("Menlo", 11))
        self.tab_widget.addTab(self.debug_text, "ログ")
        
        # 結果タブ
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Helvetica", 11))
        self.tab_widget.addTab(self.result_text, "文字起こし結果")
        
        # AI処理結果タブ
        self.ai_result_text = QTextEdit()
        self.ai_result_text.setReadOnly(True)
        self.ai_result_text.setFont(QFont("Helvetica", 11))
        self.tab_widget.addTab(self.ai_result_text, "AI処理結果")
        
        layout.addWidget(self.tab_widget)

    def log_debug(self, message: str):
        """デバッグログを追加"""
        self.debug_text.append(message)
        # 自動スクロール
        scrollbar = self.debug_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_result(self, text: str):
        """文字起こし結果を設定"""
        self.result_text.setText(text)

    def set_ai_result(self, text: str):
        """AI処理結果を設定"""
        self.ai_result_text.setText(text)

    def get_result(self) -> str:
        """文字起こし結果を取得"""
        return self.result_text.toPlainText()

    def get_ai_result(self) -> str:
        """AI処理結果を取得"""
        return self.ai_result_text.toPlainText()

    def switch_to_tab(self, index: int):
        """指定したタブに切り替え"""
        self.tab_widget.setCurrentIndex(index)

    def clear_all(self):
        """全てのテキストをクリア"""
        self.debug_text.clear()
        self.result_text.clear()
        self.ai_result_text.clear()
