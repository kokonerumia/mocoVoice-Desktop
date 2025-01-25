"""
オプションパネルモジュール
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QCheckBox

class OptionsPanel(QFrame):
    """オプションパネルクラス"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        
        self.speaker_checkbox = QCheckBox("話者分離")
        self.speaker_checkbox.setChecked(True)  # デフォルトでオン
        
        self.timestamp_checkbox = QCheckBox("タイムスタンプ")
        self.timestamp_checkbox.setChecked(True)  # デフォルトでオン
        
        self.punctuation_checkbox = QCheckBox("句読点の自動挿入")
        self.punctuation_checkbox.setChecked(True)  # デフォルトでオン
        
        layout.addWidget(self.speaker_checkbox)
        layout.addWidget(self.timestamp_checkbox)
        layout.addWidget(self.punctuation_checkbox)

    def get_options(self) -> dict:
        """オプション設定を取得"""
        return {
            'speaker_diarization': self.speaker_checkbox.isChecked(),
            'timestamp': self.timestamp_checkbox.isChecked(),
            'punctuation': self.punctuation_checkbox.isChecked()
        }
