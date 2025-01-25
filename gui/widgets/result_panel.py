"""
結果表示パネルモジュール
"""
import markdown
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QTextEdit, QTextBrowser, QPushButton, QFileDialog
)
from PyQt6.QtGui import QFont

class ResultPanel(QFrame):
    """結果表示パネルクラス"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """UIの初期化"""
        main_layout = QVBoxLayout(self)
        
        # 上部のボタンエリア
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("結果を保存")
        self.save_button.clicked.connect(self.save_current_tab)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
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
        self.ai_result_text = QTextBrowser()
        self.ai_result_text.setOpenExternalLinks(True)  # 外部リンクを開けるように
        self.ai_result_text.setFont(QFont("Helvetica", 11))
        self.tab_widget.addTab(self.ai_result_text, "AI処理結果")
        
        main_layout.addWidget(self.tab_widget)

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
        # マークダウンをHTMLに変換
        html = markdown.markdown(text, extensions=['tables', 'fenced_code'])
        self.ai_result_text.setHtml(html)

    def get_result(self) -> str:
        """文字起こし結果を取得"""
        return self.result_text.toPlainText()

    def get_ai_result(self) -> str:
        """AI処理結果を取得"""
        return self.ai_result_text.toPlainText()

    def switch_to_tab(self, index: int):
        """指定したタブに切り替え"""
        self.tab_widget.setCurrentIndex(index)

    def save_current_tab(self):
        """現在のタブの内容を保存"""
        current_index = self.tab_widget.currentIndex()
        if current_index == 0:  # ログタブ
            text = self.debug_text.toPlainText()
            title = "ログを保存"
        elif current_index == 1:  # 文字起こし結果タブ
            text = self.result_text.toPlainText()
            title = "文字起こし結果を保存"
        else:  # AI処理結果タブ
            text = self.ai_result_text.toPlainText()
            title = "AI処理結果を保存"

        if not text:
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            title,
            "",
            "テキストファイル (*.txt);;すべてのファイル (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(text)
            except Exception as e:
                print(f"保存エラー: {str(e)}")

    def on_tab_changed(self, index: int):
        """タブ切り替え時の処理"""
        # 保存ボタンの有効/無効を切り替え
        text = ""
        if index == 0:
            text = self.debug_text.toPlainText()
        elif index == 1:
            text = self.result_text.toPlainText()
        else:
            text = self.ai_result_text.toPlainText()
        
        self.save_button.setEnabled(bool(text))

    def clear_all(self):
        """全てのテキストをクリア"""
        self.debug_text.clear()
        self.result_text.clear()
        self.ai_result_text.clear()
