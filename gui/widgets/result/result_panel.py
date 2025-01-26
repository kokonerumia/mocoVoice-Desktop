"""
結果表示パネルのメインモジュール
"""
import json
import markdown
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QTextBrowser, QPushButton, QMessageBox,
    QScrollArea, QLabel, QDialog, QWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from .constants import FONT_SETTINGS, TAB_INDICES, TAB_TITLES
from .mode_manager import TranscriptModeManager
from .file_manager import TranscriptFileManager
from .conversation_analyzer import ConversationAnalysisWidget
from .speaker_manager import SpeakerDialog

class ResultPanel(QFrame):
    """結果表示パネルクラス"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.raw_text = ""
        self.setup_managers()
        self.initUI()
        
    def setup_managers(self):
        """各種マネージャーの初期化"""
        self.file_manager = TranscriptFileManager(self)
        self.mode_manager = TranscriptModeManager(self)
        self.mode_manager.content_changed.connect(self.on_content_changed)
        
    def initUI(self):
        """UIの初期化"""
        main_layout = QVBoxLayout(self)
        
        # 上部のボタンエリア
        button_layout = QHBoxLayout()
        
        # 左側のボタン
        left_buttons = QHBoxLayout()
        self.save_button = QPushButton("名前を付けて保存")
        self.save_button.clicked.connect(self.save_current_tab)
        left_buttons.addWidget(self.save_button)
        
        self.overwrite_button = QPushButton("上書き保存")
        self.overwrite_button.clicked.connect(self.overwrite_current_tab)
        self.overwrite_button.setEnabled(False)  # 初期状態では無効
        left_buttons.addWidget(self.overwrite_button)
        
        self.speaker_button = QPushButton("話者名の編集")
        self.speaker_button.clicked.connect(self.manage_speakers)
        self.speaker_button.setVisible(False)  # 初期状態では非表示
        left_buttons.addWidget(self.speaker_button)
        
        # 右側のボタン
        right_buttons = QHBoxLayout()
        self.view_mode_button = QPushButton("編集モード")
        self.view_mode_button.setCheckable(True)
        right_buttons.addWidget(self.view_mode_button)
        
        button_layout.addLayout(left_buttons)
        button_layout.addStretch()
        button_layout.addLayout(right_buttons)
        main_layout.addLayout(button_layout)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 文字起こし結果タブ
        result_widget = QWidget()
        result_layout = QVBoxLayout(result_widget)
        
        # モード管理ウィジェットを設定
        self.mode_manager.set_mode_button(self.view_mode_button)
        result_layout.addWidget(self.mode_manager)
        self.tab_widget.addTab(result_widget, TAB_TITLES["result"])
        
        # 会話分析タブ
        self.analysis_scroll = QScrollArea()
        self.analysis_widget = ConversationAnalysisWidget()
        self.analysis_scroll.setWidget(self.analysis_widget)
        self.analysis_scroll.setWidgetResizable(True)
        self.tab_widget.addTab(self.analysis_scroll, TAB_TITLES["analysis"])
        
        # AI処理結果タブ
        self.ai_result_text = QTextBrowser()
        self.ai_result_text.setOpenExternalLinks(True)
        self.ai_result_text.setFont(QFont(
            FONT_SETTINGS["result"]["family"],
            FONT_SETTINGS["result"]["size"]
        ))
        self.tab_widget.addTab(self.ai_result_text, TAB_TITLES["ai_result"])
        
        main_layout.addWidget(self.tab_widget)
        
    def set_result(self, text: str, file_path: str = None):
        """文字起こし結果を設定"""
        try:
            # JSONとしてパースを試みる
            data = json.loads(text)
            self.raw_text = json.dumps(data, ensure_ascii=False, indent=2)
            
            # モードマネージャーに内容を設定
            self.mode_manager.set_content(self.raw_text)
            
            # ファイル情報を更新
            if file_path:
                self.file_manager.current_file = file_path
                self.overwrite_button.setEnabled(True)
            
            # 表示モード切り替えボタンと話者管理ボタンを表示
            self.view_mode_button.setVisible(True)
            self.speaker_button.setVisible(True)
            
            # 会話分析を更新
            self.analysis_widget.update_analysis(self.raw_text)
            
        except json.JSONDecodeError:
            # JSONでない場合はそのまま表示
            self.mode_manager.set_content(text)
            self.view_mode_button.setVisible(False)
            self.speaker_button.setVisible(False)
            
    def set_ai_result(self, text: str):
        """AI処理結果を設定"""
        html = markdown.markdown(text, extensions=['tables', 'fenced_code'])
        self.ai_result_text.setHtml(html)
        
    def save_current_tab(self):
        """現在のタブの内容を保存"""
        current_index = self.tab_widget.currentIndex()
        
        if current_index == TAB_INDICES["result"]:
            text = self.mode_manager.get_content()
            success, file_path = self.file_manager.save_transcript(text)
            if success:
                self.overwrite_button.setEnabled(True)
                
    def overwrite_current_tab(self):
        """現在のタブの内容を上書き保存"""
        current_index = self.tab_widget.currentIndex()
        if current_index == TAB_INDICES["result"]:
            text = self.mode_manager.get_content()
            self.file_manager.save_transcript(text, self.file_manager.get_current_file())
            
    def manage_speakers(self):
        """話者名の編集ダイアログを表示"""
        dialog = SpeakerDialog(self.raw_text, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            modified_json = dialog.get_modified_json()
            if modified_json != self.raw_text:
                # JSONを更新
                self.raw_text = modified_json
                
                # ファイルに保存
                if self.file_manager.get_current_file():
                    try:
                        with open(self.file_manager.get_current_file(), 'w', encoding='utf-8') as f:
                            f.write(modified_json)
                            
                        # 保存成功メッセージ
                        QMessageBox.information(
                            self,
                            "保存完了",
                            "話者名の変更を保存しました。"
                        )
                        
                        # 表示を更新
                        self.mode_manager.set_content(self.raw_text)
                        self.analysis_widget.update_analysis(self.raw_text)
                        
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            "保存エラー",
                            f"ファイルの保存に失敗しました:\n{str(e)}"
                        )
                
    def on_content_changed(self):
        """内容が変更された時の処理"""
        if self.file_manager.get_current_file():
            self.overwrite_button.setEnabled(True)
            
    def on_tab_changed(self, index: int):
        """タブ切り替え時の処理"""
        # 保存ボタンの状態を更新
        self.save_button.setEnabled(index in [TAB_INDICES["result"], TAB_INDICES["ai_result"]])
        self.overwrite_button.setEnabled(
            index == TAB_INDICES["result"] and bool(self.file_manager.get_current_file())
        )
        
    def switch_to_tab(self, index: int):
        """指定したタブに切り替え"""
        self.tab_widget.setCurrentIndex(index)
        
    def cleanup(self):
        """終了処理"""
        self.mode_manager.cleanup()
