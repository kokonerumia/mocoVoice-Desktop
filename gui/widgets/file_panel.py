"""
ファイル選択パネルモジュール
"""
import webbrowser
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, pyqtSignal
from moco_client import MIME_TYPES

class FilePanel(QFrame):
    """ファイル選択パネルクラス"""
    file_selected = pyqtSignal(str)  # ファイル選択時のシグナル
    text_loaded = pyqtSignal(str)    # テキスト読み込み時のシグナル

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # ロゴ部分
        logo_frame = QFrame()
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        # ロゴラベル
        logo_label = QLabel()
        pixmap = QPixmap('mocovoice-logo.png')
        scaled_pixmap = pixmap.scaled(200, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # カーソルを手の形に
        logo_label.mousePressEvent = lambda _: webbrowser.open('https://docs.mocomoco.ai/')
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        layout.addWidget(logo_frame)

        # ファイル選択部分
        file_frame = QFrame()
        file_layout = QVBoxLayout(file_frame)
        
        self.input_path_label = QLabel("ファイルが選択されていません")
        file_layout.addWidget(self.input_path_label)
        
        button_layout = QHBoxLayout()
        
        browse_button = QPushButton("音声ファイルを選択")
        browse_button.clicked.connect(self.browse_input_file)
        button_layout.addWidget(browse_button)
        
        load_text_button = QPushButton("テキストを読み込む")
        load_text_button.clicked.connect(self.load_text_file)
        button_layout.addWidget(load_text_button)
        
        file_layout.addLayout(button_layout)
        layout.addWidget(file_frame)

    def browse_input_file(self):
        """音声ファイルを選択"""
        extensions = " ".join(f"*{ext}" for ext in MIME_TYPES.keys())
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "音声/動画ファイルを選択",
            "",
            f"メディアファイル ({extensions});;すべてのファイル (*.*)"
        )
        if file_name:
            self.input_path_label.setText(file_name)
            self.file_selected.emit(file_name)

    def load_text_file(self):
        """テキストファイルを読み込む"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "テキストファイルを選択",
            "",
            "テキストファイル (*.txt);;すべてのファイル (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.input_path_label.setText(file_name)
                self.text_loaded.emit(text)
            except Exception as e:
                self.text_loaded.emit(f"テキストファイル読み込みエラー: {str(e)}")

    def get_input_path(self) -> str:
        """入力パスを取得"""
        return self.input_path_label.text()
