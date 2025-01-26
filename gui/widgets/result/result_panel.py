"""
結果表示パネルのメインモジュール
"""
import json
import markdown
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QTextEdit, QTextBrowser, QPushButton, QMessageBox,
    QScrollArea, QLabel, QDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from .constants import FONT_SETTINGS, TAB_INDICES, TAB_TITLES
from .transcript_formatter import TranscriptFormatter
from .file_handler import FileHandler
from .conversation_analyzer import ConversationAnalysisWidget
from .speaker_manager import SpeakerManagerDialog

class ResultPanel(QFrame):
    """結果表示パネルクラス"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.formatter = TranscriptFormatter()
        self.file_handler = FileHandler(self)
        self.raw_text = ""
        self.current_file = None  # 現在開いているファイルのパス
        self.initUI()

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
        
        self.speaker_button = QPushButton("話者の管理")
        self.speaker_button.clicked.connect(self.manage_speakers)
        self.speaker_button.setVisible(False)  # 初期状態では非表示
        left_buttons.addWidget(self.speaker_button)
        
        # 右側のボタン
        right_buttons = QHBoxLayout()
        self.markdown_toggle = QPushButton("プレーンテキスト")
        self.markdown_toggle.setCheckable(True)
        self.markdown_toggle.clicked.connect(self.toggle_markdown_view)
        self.markdown_toggle.setVisible(False)
        right_buttons.addWidget(self.markdown_toggle)
        
        button_layout.addLayout(left_buttons)
        button_layout.addStretch()
        button_layout.addLayout(right_buttons)
        main_layout.addLayout(button_layout)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 結果タブ（編集可能）
        self.result_text = QTextEdit()
        self.result_text.setFont(QFont(
            FONT_SETTINGS["result"]["family"],
            FONT_SETTINGS["result"]["size"]
        ))
        self.result_text.textChanged.connect(self.on_result_text_changed)
        self.tab_widget.addTab(self.result_text, TAB_TITLES["result"])
        
        # 結果表示モード切り替えボタン
        self.view_mode_button = QPushButton("編集モード")
        self.view_mode_button.setCheckable(True)
        self.view_mode_button.clicked.connect(self.toggle_view_mode)
        self.view_mode_button.setVisible(False)
        right_buttons.addWidget(self.view_mode_button)
        
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
        self.current_file = file_path
        self.overwrite_button.setEnabled(bool(file_path))
        self.raw_text = text
        
        try:
            # JSONとしてパースを試みる
            data = json.loads(text)
            # 整形されたJSONを保存
            self.raw_text = json.dumps(data, ensure_ascii=False, indent=2)
            # HTML形式で表示
            formatted_text = self.formatter.format_transcript(text)
            self.result_text.setHtml(formatted_text)
            # 表示モード切り替えボタンと話者管理ボタンを表示
            self.view_mode_button.setVisible(True)
            self.view_mode_button.setChecked(False)
            self.view_mode_button.setText("編集モード")
            self.speaker_button.setVisible(True)
            
            # 会話分析を更新
            self.analysis_widget.update_analysis(text)
        except json.JSONDecodeError:
            # JSONでない場合はそのまま表示
            self.result_text.setPlainText(text)
            self.view_mode_button.setVisible(False)
            self.speaker_button.setVisible(False)

    def set_ai_result(self, text: str):
        """AI処理結果を設定"""
        self.raw_text = text
        self.markdown_toggle.setVisible(True)
        self.show_markdown_view()

    def show_markdown_view(self):
        """マークダウン表示に切り替え"""
        html = markdown.markdown(self.raw_text, extensions=['tables', 'fenced_code'])
        self.ai_result_text.setHtml(html)
        self.markdown_toggle.setText("プレーンテキスト")
        self.markdown_toggle.setChecked(False)

    def show_plain_text(self):
        """プレーンテキスト表示に切り替え"""
        self.ai_result_text.setPlainText(self.raw_text)
        self.markdown_toggle.setText("マークダウン")
        self.markdown_toggle.setChecked(True)

    def toggle_markdown_view(self):
        """マークダウン表示とプレーンテキスト表示を切り替え"""
        if self.markdown_toggle.isChecked():
            self.show_plain_text()
        else:
            self.show_markdown_view()

    def get_result(self) -> str:
        """文字起こし結果を取得"""
        return self.result_text.toPlainText()

    def get_ai_result(self) -> str:
        """AI処理結果を取得"""
        return self.ai_result_text.toPlainText()

    def switch_to_tab(self, index: int):
        """指定したタブに切り替え"""
        self.tab_widget.setCurrentIndex(index)

    def validate_json_text(self, show_error: bool = True) -> bool:
        """文字起こし結果のJSONを検証"""
        text = self.result_text.toPlainText()
        try:
            # JSONとしてパース
            data = json.loads(text)
            # 文字起こし結果の形式を検証
            if self.formatter.validate_transcript_json(text):
                return True
                
            if show_error:
                QMessageBox.warning(
                    self,
                    "検証エラー",
                    "文字起こし結果の形式が正しくありません。\n\n" +
                    "以下の形式である必要があります:\n" +
                    "[\n" +
                    "  {\n" +
                    '    "start": 0.0,\n' +
                    '    "end": 1.0,\n' +
                    '    "text": "発話内容",\n' +
                    '    "speaker": "SPEAKER_01"\n' +
                    "  },\n" +
                    "  ...\n" +
                    "]"
                )
            return False
            
        except json.JSONDecodeError as e:
            if show_error:
                QMessageBox.warning(
                    self,
                    "JSONエラー",
                    f"無効なJSONフォーマットです:\n{str(e)}"
                )
            return False

    def save_current_tab(self):
        """現在のタブの内容を保存"""
        current_index = self.tab_widget.currentIndex()
        
        if current_index == TAB_INDICES["result"]:
            text = self.result_text.toPlainText()
            if text and self.validate_json_text():
                file_path = self.file_handler.save_transcript(text)
                if file_path:
                    self.current_file = file_path
                    self.overwrite_button.setEnabled(True)
                
        elif current_index == TAB_INDICES["ai_result"]:
            text = self.ai_result_text.toPlainText()
            if text:
                self.file_handler.save_text(text, "AI処理結果を保存")

    def overwrite_current_tab(self):
        """現在のタブの内容を上書き保存"""
        if not self.current_file:
            return
            
        current_index = self.tab_widget.currentIndex()
        if current_index == TAB_INDICES["result"]:
            text = self.result_text.toPlainText()
            if text and self.validate_json_text():
                try:
                    # JSONとしてパースしてフォーマット
                    data = json.loads(text)
                    with open(self.current_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    QMessageBox.information(self, "保存完了", "ファイルを上書き保存しました。")
                except Exception as e:
                    QMessageBox.warning(self, "保存エラー", f"ファイルの保存に失敗しました:\n{str(e)}")

    def toggle_view_mode(self):
        """表示モードの切り替え"""
        if self.view_mode_button.isChecked():
            # 編集モードに切り替え
            self.result_text.setPlainText(self.raw_text)
            self.view_mode_button.setText("表示モード")
        else:
            # 表示モードに切り替え
            try:
                # 編集内容をJSONとしてパース
                data = json.loads(self.result_text.toPlainText())
                self.raw_text = json.dumps(data, ensure_ascii=False, indent=2)
                # HTML形式で表示
                formatted_text = self.formatter.format_transcript(self.raw_text)
                self.result_text.setHtml(formatted_text)
                self.view_mode_button.setText("編集モード")
            except json.JSONDecodeError:
                # JSONが無効な場合は編集モードのまま
                self.view_mode_button.setChecked(True)
                QMessageBox.warning(
                    self,
                    "JSONエラー",
                    "無効なJSON形式です。編集内容を確認してください。"
                )

    def on_result_text_changed(self):
        """文字起こし結果のテキストが変更された時の処理"""
        if self.view_mode_button.isChecked():
            # 編集モード時のみ検証
            is_valid = self.validate_json_text(show_error=False)
            self.save_button.setEnabled(is_valid)
            if self.current_file:
                self.overwrite_button.setEnabled(is_valid)

    def on_tab_changed(self, index: int):
        """タブ切り替え時の処理"""
        text = ""
        if index == TAB_INDICES["result"]:
            text = self.result_text.toPlainText()
            self.save_button.setText("名前を付けて保存")
            # JSONの検証（エラーメッセージは表示しない）
            is_valid = self.validate_json_text(show_error=False)
            self.save_button.setEnabled(is_valid)
            self.overwrite_button.setEnabled(bool(self.current_file) and is_valid)
        else:
            text = self.ai_result_text.toPlainText()
            self.save_button.setText("名前を付けて保存")
            self.overwrite_button.setEnabled(False)
        
        self.save_button.setEnabled(bool(text))

    def clear_all(self):
        """全てのテキストをクリア"""
        self.result_text.clear()
        self.ai_result_text.clear()
        self.markdown_toggle.setVisible(False)
        self.view_mode_button.setVisible(False)
        self.speaker_button.setVisible(False)
        self.current_file = None
        self.overwrite_button.setEnabled(False)
        
        # 会話分析をクリア
        self.analysis_widget.update_analysis("[]")
        
    def manage_speakers(self):
        """話者管理ダイアログを表示"""
        dialog = SpeakerManagerDialog(self.raw_text, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            modified_json = dialog.get_modified_json()
            if modified_json != self.raw_text:
                try:
                    # JSONを更新
                    self.raw_text = modified_json
                    
                    # 表示を更新
                    if self.view_mode_button.isChecked():
                        # 編集モードの場合はプレーンテキストを更新
                        self.result_text.setPlainText(self.raw_text)
                    else:
                        # 表示モードの場合はHTML形式で表示
                        formatted_text = self.formatter.format_transcript(self.raw_text)
                        self.result_text.setHtml(formatted_text)
                    
                    # 会話分析を更新
                    self.analysis_widget.update_analysis(self.raw_text)
                    
                    # ファイルが開かれている場合は自動で保存
                    if self.current_file:
                        with open(self.current_file, 'w', encoding='utf-8') as f:
                            json.dump(json.loads(self.raw_text), f, ensure_ascii=False, indent=2)
                except Exception as e:
                    QMessageBox.warning(self, "エラー", f"話者の変更に失敗しました: {str(e)}")
