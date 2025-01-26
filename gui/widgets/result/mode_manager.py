"""
表示/編集モードの管理を担当するモジュール
"""
from PyQt6.QtWidgets import QStackedWidget, QPushButton
from PyQt6.QtCore import pyqtSignal
from .transcript_viewer import TranscriptViewWidget
from .transcript_editor import TranscriptEditWidget

class TranscriptModeManager(QStackedWidget):
    """表示/編集モードの管理クラス"""
    
    # シグナル定義
    content_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_widgets()
        
    def setup_widgets(self):
        """ウィジェットの初期化"""
        # 編集モード
        self.editor = TranscriptEditWidget()
        self.editor.textChanged.connect(self.content_changed.emit)
        self.addWidget(self.editor)
        
        # 表示モード
        self.viewer = TranscriptViewWidget()
        self.addWidget(self.viewer)
        
    def set_mode_button(self, button: QPushButton):
        """モード切り替えボタンを設定"""
        self.mode_button = button
        self.mode_button.clicked.connect(self.toggle_mode)
        
    def set_content(self, text: str):
        """内容を設定"""
        # 編集モードのテキストを設定
        self.editor.setPlainText(text)
        
        # 表示モードのHTMLを設定
        self.viewer.set_html(text)
        
        # 表示モードに切り替え
        self.mode_button.setChecked(False)
        self.mode_button.setText("編集モード")
        self.setCurrentWidget(self.viewer)
        
    def get_content(self) -> str:
        """内容を取得"""
        return self.editor.toPlainText()
        
    def toggle_mode(self):
        """モードを切り替え"""
        if self.mode_button.isChecked():
            # 編集モードに切り替え
            self.setCurrentWidget(self.editor)
            self.mode_button.setText("表示モード")
        else:
            # 表示モードに切り替え
            self.viewer.set_html(self.editor.toPlainText())
            self.setCurrentWidget(self.viewer)
            self.mode_button.setText("編集モード")
            
    def cleanup(self):
        """終了処理"""
        self.viewer.cleanup()
