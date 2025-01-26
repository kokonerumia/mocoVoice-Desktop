"""
文字起こし結果の編集を担当するモジュール
"""
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QFont, QTextOption
from PyQt6.QtCore import Qt

from .constants import FONT_SETTINGS

class TranscriptEditWidget(QPlainTextEdit):
    """文字起こし結果の編集ウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_editor()
        
    def setup_editor(self):
        """エディタの設定"""
        # フォント設定
        self.setFont(QFont(
            FONT_SETTINGS["result"]["family"],
            FONT_SETTINGS["result"]["size"]
        ))
        
        # 折り返し設定
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapMode.WordWrap)
        self.document().setDefaultTextOption(option)
        
        # タブ設定
        self.setTabStopDistance(20)
        
        # 行番号の余白
        self.setViewportMargins(5, 0, 5, 0)
        
        # プレースホルダーテキスト
        self.setPlaceholderText("ここに文字起こし結果が表示されます")
        
        # 背景色を少し明るく
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #fafafa;
                selection-background-color: #c2e0ff;
                selection-color: #000000;
            }
        """)
