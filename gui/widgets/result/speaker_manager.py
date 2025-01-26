"""
話者管理モジュール
"""
import json
from typing import Dict, List, Set, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QWidget, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class SpeakerMergeWidget(QWidget):
    """話者統合ウィジェット"""
    
    merge_requested = pyqtSignal(list, str)  # (from_speakers, to_speaker)
    
    def __init__(self, speakers: List[str], parent=None):
        super().__init__(parent)
        self.speakers = speakers
        self.initUI()
        
    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        
        # 説明
        description = QLabel("統合したい話者を選択し、統合先の話者を選んでください")
        layout.addWidget(description)
        
        # 話者リスト
        self.list_widget = QListWidget()
        for speaker in self.speakers:
            item = QListWidgetItem(speaker)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        
        # 統合先の話者
        merge_layout = QHBoxLayout()
        merge_layout.addWidget(QLabel("統合先の話者:"))
        self.merge_to = QComboBox()
        self.merge_to.addItems(self.speakers)
        merge_layout.addWidget(self.merge_to)
        layout.addLayout(merge_layout)
        
        # 統合ボタン
        merge_button = QPushButton("統合")
        merge_button.clicked.connect(self.merge_speakers)
        layout.addWidget(merge_button)
        
    def merge_speakers(self):
        """選択された話者を統合"""
        # 選択された話者を取得
        selected_speakers = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_speakers.append(item.text())
        
        if len(selected_speakers) == 0:
            QMessageBox.warning(self, "エラー", "統合する話者を選択してください")
            return
            
        merge_to = self.merge_to.currentText()
        if merge_to in selected_speakers:
            QMessageBox.warning(self, "エラー", "統合先の話者は選択された話者に含まれていません")
            return
            
        # 統合を実行
        self.merge_requested.emit(selected_speakers, merge_to)
            
        # 選択をクリア
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.CheckState.Unchecked)

class SpeakerRenameWidget(QWidget):
    """話者名変更ウィジェット"""
    
    rename_requested = pyqtSignal(str, str)  # (old_name, new_name)
    rename_pattern_requested = pyqtSignal(str, str)  # (pattern, new_name)
    
    def __init__(self, speakers: List[str], parent=None):
        super().__init__(parent)
        self.speakers = speakers
        self.initUI()
        
    def initUI(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        
        # 説明
        description = QLabel("話者IDを変更できます")
        layout.addWidget(description)
        
        # 変更対象の話者
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("変更する話者:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(self.speakers)
        self.target_combo.currentTextChanged.connect(self.on_target_changed)
        target_layout.addWidget(self.target_combo)
        layout.addLayout(target_layout)
        
        # 変更後の話者ID
        new_name_layout = QHBoxLayout()
        new_name_layout.addWidget(QLabel("新しい話者ID:"))
        self.new_name_edit = QLineEdit()
        new_name_layout.addWidget(self.new_name_edit)
        layout.addLayout(new_name_layout)
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        
        # 個別変更ボタン
        rename_button = QPushButton("変更")
        rename_button.clicked.connect(self.rename_speaker)
        button_layout.addWidget(rename_button)
        
        # 一括変更ボタン
        rename_all_button = QPushButton("同じパターンをすべて変更")
        rename_all_button.clicked.connect(self.rename_pattern)
        button_layout.addWidget(rename_all_button)
        
        layout.addLayout(button_layout)
        
        # プレビュー
        layout.addWidget(QLabel("同じパターンの話者:"))
        self.preview_list = QListWidget()
        layout.addWidget(self.preview_list)
        
    def on_target_changed(self, speaker: str):
        """選択された話者が変更された時の処理"""
        self.preview_list.clear()
        pattern = speaker.rstrip("0123456789")  # 数字を除いたパターン
        for s in self.speakers:
            if s != speaker and s.startswith(pattern):
                self.preview_list.addItem(s)
        
    def rename_speaker(self):
        """話者名を変更"""
        old_name = self.target_combo.currentText()
        new_name = self.new_name_edit.text().strip()
        
        if not new_name:
            QMessageBox.warning(self, "エラー", "新しい話者IDを入力してください")
            return
            
        # 変更を実行
        self.rename_requested.emit(old_name, new_name)
        
        # 入力をクリア
        self.new_name_edit.clear()
        self.preview_list.clear()
        
    def rename_pattern(self):
        """同じパターンの話者をすべて変更"""
        speaker = self.target_combo.currentText()
        new_name = self.new_name_edit.text().strip()
        
        if not new_name:
            QMessageBox.warning(self, "エラー", "新しい話者IDを入力してください")
            return
            
        pattern = speaker.rstrip("0123456789")  # 数字を除いたパターン
        if not pattern:
            QMessageBox.warning(self, "エラー", "選択された話者からパターンを抽出できません")
            return
            
        # 変更を実行
        self.rename_pattern_requested.emit(pattern, new_name)
        
        # 入力をクリア
        self.new_name_edit.clear()
        self.preview_list.clear()

class SpeakerManagerDialog(QDialog):
    """話者管理ダイアログ"""
    
    def __init__(self, json_text: str, parent=None):
        super().__init__(parent)
        self.json_text = json_text
        self.modified_json = json_text
        self.initUI()
        
    def initUI(self):
        """UIの初期化"""
        self.setWindowTitle("話者の管理")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        # 話者リストを取得
        try:
            data = json.loads(self.json_text)
            speakers = sorted(list({utterance["speaker"] for utterance in data}))
        except:
            speakers = []
        
        # タブのようなボタン配置
        button_layout = QHBoxLayout()
        self.merge_widget = SpeakerMergeWidget(speakers)
        self.rename_widget = SpeakerRenameWidget(speakers)
        self.rename_widget.hide()
        
        merge_button = QPushButton("話者の統合")
        merge_button.setCheckable(True)
        merge_button.setChecked(True)
        merge_button.clicked.connect(lambda: self.switch_view("merge"))
        
        rename_button = QPushButton("話者IDの変更")
        rename_button.setCheckable(True)
        rename_button.clicked.connect(lambda: self.switch_view("rename"))
        
        self.view_buttons = {
            "merge": merge_button,
            "rename": rename_button
        }
        
        button_layout.addWidget(merge_button)
        button_layout.addWidget(rename_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addWidget(self.merge_widget)
        layout.addWidget(self.rename_widget)
        
        # 閉じるボタン
        close_button = QPushButton("閉じる")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        # シグナルの接続
        self.merge_widget.merge_requested.connect(self.merge_speakers)
        self.rename_widget.rename_requested.connect(self.rename_speaker)
        self.rename_widget.rename_pattern_requested.connect(self.rename_pattern)
        
    def switch_view(self, view: str):
        """表示を切り替え"""
        self.merge_widget.hide()
        self.rename_widget.hide()
        
        if view == "merge":
            self.merge_widget.show()
            self.view_buttons["merge"].setChecked(True)
            self.view_buttons["rename"].setChecked(False)
        else:
            self.rename_widget.show()
            self.view_buttons["merge"].setChecked(False)
            self.view_buttons["rename"].setChecked(True)
            
    def _update_widgets(self, speakers: List[str]):
        """ウィジェットを更新"""
        # 現在の選択状態を保存
        current_merge_to = self.merge_widget.merge_to.currentText() if hasattr(self.merge_widget, 'merge_to') else None
        current_target = self.rename_widget.target_combo.currentText() if hasattr(self.rename_widget, 'target_combo') else None
        current_new_name = self.rename_widget.new_name_edit.text() if hasattr(self.rename_widget, 'new_name_edit') else None

        # ウィジェットを再作成
        merge_widget = SpeakerMergeWidget(speakers)
        rename_widget = SpeakerRenameWidget(speakers)
        
        # レイアウトから古いウィジェットを削除
        self.layout().removeWidget(self.merge_widget)
        self.layout().removeWidget(self.rename_widget)
        self.merge_widget.deleteLater()
        self.rename_widget.deleteLater()
        
        # 新しいウィジェットを設定
        self.merge_widget = merge_widget
        self.rename_widget = rename_widget
        self.layout().insertWidget(2, self.merge_widget)
        self.layout().insertWidget(3, self.rename_widget)
        
        # シグナルを再接続
        self.merge_widget.merge_requested.connect(self.merge_speakers)
        self.rename_widget.rename_requested.connect(self.rename_speaker)
        self.rename_widget.rename_pattern_requested.connect(self.rename_pattern)
        
        # 選択状態を復元
        if current_merge_to in speakers:
            self.merge_widget.merge_to.setCurrentText(current_merge_to)
        if current_target in speakers:
            self.rename_widget.target_combo.setCurrentText(current_target)
        if current_new_name:
            self.rename_widget.new_name_edit.setText(current_new_name)
        
        # 現在のビューを維持
        if self.view_buttons["merge"].isChecked():
            self.merge_widget.show()
            self.rename_widget.hide()
        else:
            self.merge_widget.hide()
            self.rename_widget.show()

    def merge_speakers(self, from_speakers: List[str], to_speaker: str):
        """話者を統合"""
        try:
            # JSONをパースして変更を適用
            data = json.loads(self.modified_json)
            count = 0
            for utterance in data:
                if utterance["speaker"] in from_speakers:
                    utterance["speaker"] = to_speaker
                    count += 1
            
            # 変更を保存
            self.modified_json = json.dumps(data, ensure_ascii=False, indent=2)
            
            # 話者リストを更新
            speakers = sorted(list({utterance["speaker"] for utterance in data}))
            self._update_widgets(speakers)
            
            QMessageBox.information(self, "完了", f"{', '.join(from_speakers)} を {to_speaker} に統合しました（{count}件）")
            
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"統合に失敗しました: {str(e)}")
            
    def rename_speaker(self, old_name: str, new_name: str):
        """話者名を変更"""
        try:
            # JSONをパースして変更を適用
            data = json.loads(self.modified_json)
            count = 0
            for utterance in data:
                if utterance["speaker"] == old_name:
                    utterance["speaker"] = new_name
                    count += 1
            
            # 変更を保存
            self.modified_json = json.dumps(data, ensure_ascii=False, indent=2)
            
            # 話者リストを更新
            speakers = sorted(list({utterance["speaker"] for utterance in data}))
            self._update_widgets(speakers)
            
            QMessageBox.information(self, "完了", f"{old_name} を {new_name} に変更しました（{count}件）")
            
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"変更に失敗しました: {str(e)}")
            
    def rename_pattern(self, pattern: str, new_name: str):
        """同じパターンの話者をすべて変更"""
        try:
            # JSONをパースして変更を適用
            data = json.loads(self.modified_json)
            speakers = sorted(list({utterance["speaker"] for utterance in data}))
            count = 0
            
            # パターンにマッチする話者を変更
            for utterance in data:
                speaker = utterance["speaker"]
                if speaker.startswith(pattern):
                    # 元の数字部分を保持（数字がない場合は空文字）
                    suffix = speaker[len(pattern):] if speaker[len(pattern):].isdigit() else ""
                    # 新しい話者名を生成
                    new_speaker = new_name + suffix if suffix else new_name
                    utterance["speaker"] = new_speaker
                    count += 1
            
            # 変更を保存
            self.modified_json = json.dumps(data, ensure_ascii=False, indent=2)
            
            # 話者リストを更新
            speakers = sorted(list({utterance["speaker"] for utterance in data}))
            self._update_widgets(speakers)
            
            QMessageBox.information(self, "完了", f"{pattern}* を {new_name}* に一括変更しました（{count}件）")
            
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"一括変更に失敗しました: {str(e)}")
            
    def get_modified_json(self) -> str:
        """変更後のJSONを取得"""
        return self.modified_json
