"""
話者名の管理を担当するモジュール
"""
import json
import re
from typing import List, Optional, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QMessageBox, QPlainTextEdit,
    QComboBox, QListWidget, QWidget, QTabWidget
)
from PyQt6.QtGui import QFont, QTextCharFormat, QSyntaxHighlighter
from PyQt6.QtCore import Qt

class JsonHighlighter(QSyntaxHighlighter):
    """JSONのシンタックスハイライト"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.speaker_format = QTextCharFormat()
        self.speaker_format.setBackground(Qt.GlobalColor.yellow)
        
    def highlightBlock(self, text: str):
        """話者名部分をハイライト"""
        pattern = r'"speaker":\s*"([^"]+)"'
        for match in re.finditer(pattern, text):
            # "speaker": の部分
            start = match.start()
            colon_pos = text.find(':', start) + 1
            self.setFormat(start, colon_pos - start, QTextCharFormat())
            
            # 話者名の部分
            name_start = text.find('"', colon_pos) + 1
            name_end = text.find('"', name_start)
            self.setFormat(name_start, name_end - name_start, self.speaker_format)

class SpeakerDialog(QDialog):
    """話者名の編集ダイアログ"""
    
    def __init__(self, json_text: str, parent=None):
        super().__init__(parent)
        self.json_text = json_text
        self.modified_json = json_text
        self.speakers = self._get_speakers()
        self.initUI()
        
    def _get_speakers(self) -> List[str]:
        """話者リストを取得"""
        try:
            data = json.loads(self.json_text)
            return sorted(list({utterance["speaker"] for utterance in data}))
        except:
            return []
            
    def initUI(self):
        """UIの初期化"""
        self.setWindowTitle("話者名の編集")
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout(self)
        
        # 説明
        layout.addWidget(QLabel("話者名を一括で置換できます"))
        
        # タブウィジェット
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 置換タブ
        replace_widget = QWidget()
        replace_layout = QVBoxLayout(replace_widget)
        
        # 置換設定
        replace_form = QHBoxLayout()
        replace_form.addWidget(QLabel("置換前の話者名:"))
        self.from_combo = QComboBox()
        self.from_combo.addItems(self.speakers)
        replace_form.addWidget(self.from_combo)
        
        replace_form.addWidget(QLabel("→"))
        
        self.to_edit = QLineEdit()
        self.to_edit.setPlaceholderText("新しい話者名")
        replace_form.addWidget(self.to_edit)
        
        replace_button = QPushButton("置換")
        replace_button.clicked.connect(self.replace_speaker)
        replace_form.addWidget(replace_button)
        
        replace_layout.addLayout(replace_form)
        
        # 現在の話者一覧
        replace_layout.addWidget(QLabel("現在の話者一覧:"))
        self.speakers_label = QLabel(", ".join(self.speakers))
        self.speakers_label.setWordWrap(True)
        replace_layout.addWidget(self.speakers_label)
        
        tab_widget.addTab(replace_widget, "置換")
        
        # 統合タブ
        merge_widget = QWidget()
        merge_layout = QVBoxLayout(merge_widget)
        
        # 統合元の話者選択
        merge_layout.addWidget(QLabel("統合する話者を選択:"))
        self.merge_list = QListWidget()
        self.merge_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for speaker in self.speakers:
            self.merge_list.addItem(speaker)
        merge_layout.addWidget(self.merge_list)
        
        # 統合先の話者名
        merge_form = QHBoxLayout()
        merge_form.addWidget(QLabel("統合後の話者名:"))
        self.merge_name = QLineEdit()
        self.merge_name.setPlaceholderText("新しい話者名")
        merge_form.addWidget(self.merge_name)
        
        merge_button = QPushButton("統合")
        merge_button.clicked.connect(self.merge_speakers)
        merge_form.addWidget(merge_button)
        
        merge_layout.addLayout(merge_form)
        
        tab_widget.addTab(merge_widget, "統合")
        
        # エディタ
        layout.addWidget(QLabel("JSONエディタ (黄色の部分が話者名です):"))
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Menlo", 11))
        self.editor.setPlainText(json.dumps(json.loads(self.json_text), indent=2, ensure_ascii=False))
        self.highlighter = JsonHighlighter(self.editor.document())
        layout.addWidget(self.editor)
        
        # ボタン
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
    def _update_speakers_list(self):
        """話者リストを更新"""
        try:
            data = json.loads(self.editor.toPlainText())
            self.speakers = sorted(list({utterance["speaker"] for utterance in data}))
            
            # 各ウィジェットを更新
            self.speakers_label.setText(", ".join(self.speakers))
            
            self.from_combo.clear()
            self.from_combo.addItems(self.speakers)
            
            self.merge_list.clear()
            self.merge_list.addItems(self.speakers)
            
        except:
            pass
            
    def replace_speaker(self):
        """話者名を置換"""
        old_name = self.from_combo.currentText()
        new_name = self.to_edit.text().strip()
        
        if not old_name or not new_name:
            QMessageBox.warning(self, "エラー", "置換前と置換後の話者名を入力してください")
            return
            
        try:
            # 現在のテキストを取得
            text = self.editor.toPlainText()
            
            # 正規表現で置換
            pattern = f'("speaker":\\s*"){old_name}(")'
            new_text = re.sub(pattern, f'\\1{new_name}\\2', text)
            
            if new_text == text:
                QMessageBox.warning(self, "エラー", f"話者名 {old_name} は見つかりませんでした")
                return
                
            # テキストを更新
            self.editor.setPlainText(new_text)
            
            # 話者リストを更新
            self._update_speakers_list()
                
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"置換に失敗しました: {str(e)}")
            
    def merge_speakers(self):
        """話者を統合"""
        selected_items = self.merge_list.selectedItems()
        if len(selected_items) < 2:
            QMessageBox.warning(self, "エラー", "統合する話者を2つ以上選択してください")
            return
            
        new_name = self.merge_name.text().strip()
        if not new_name:
            QMessageBox.warning(self, "エラー", "統合後の話者名を入力してください")
            return
            
        try:
            # 現在のテキストを取得
            text = self.editor.toPlainText()
            data = json.loads(text)
            
            # 選択された話者名を取得
            old_names = [item.text() for item in selected_items]
            
            # 話者名を統合
            count = 0
            for utterance in data:
                if utterance["speaker"] in old_names:
                    utterance["speaker"] = new_name
                    count += 1
                    
            if count == 0:
                QMessageBox.warning(self, "エラー", "統合対象の発話が見つかりませんでした")
                return
                
            # テキストを更新
            new_text = json.dumps(data, ensure_ascii=False, indent=2)
            self.editor.setPlainText(new_text)
            
            # 話者リストを更新
            self._update_speakers_list()
            
            # 入力フィールドをクリア
            self.merge_name.clear()
            self.merge_list.clearSelection()
            
            QMessageBox.information(
                self,
                "完了",
                f"{', '.join(old_names)} を {new_name} に統合しました（{count}件）"
            )
            
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"統合に失敗しました: {str(e)}")
            
    def get_modified_json(self) -> str:
        """変更後のJSONを取得"""
        try:
            # JSONとしてパースして整形
            data = json.loads(self.editor.toPlainText())
            return json.dumps(data, ensure_ascii=False, indent=2)
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "エラー", f"無効なJSON形式です: {str(e)}")
            return self.json_text
