"""
文字起こし結果のファイル操作を担当するモジュール
"""
import json
import os
from typing import Optional, Tuple
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

from .constants import FILE_FILTERS

class TranscriptFileManager:
    """文字起こし結果のファイル管理クラス"""
    
    def __init__(self, parent: QWidget):
        self.parent = parent
        self.current_file = None
        
    def save_transcript(self, text: str, file_path: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """文字起こし結果を保存"""
        try:
            # 保存先を取得
            if not file_path:
                file_path, _ = QFileDialog.getSaveFileName(
                    self.parent,
                    "文字起こし結果を保存",
                    "",
                    FILE_FILTERS["json"]
                )
                if not file_path:
                    return False, None
            
            # JSONとしてパース（検証）
            data = json.loads(text)
            
            # ファイルに保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.current_file = file_path
            return True, file_path
            
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self.parent,
                "保存エラー",
                f"無効なJSONフォーマットです:\n{str(e)}"
            )
            return False, None
            
        except Exception as e:
            QMessageBox.warning(
                self.parent,
                "保存エラー",
                f"ファイルの保存に失敗しました:\n{str(e)}"
            )
            return False, None
            
    def load_transcript(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """文字起こし結果を読み込み"""
        try:
            # ファイルを選択
            file_path, _ = QFileDialog.getOpenFileName(
                self.parent,
                "文字起こし結果を開く",
                "",
                FILE_FILTERS["json"]
            )
            if not file_path:
                return False, None, None
                
            # ファイルを読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            # JSONとしてパース（検証）
            data = json.loads(text)
            formatted_text = json.dumps(data, ensure_ascii=False, indent=2)
            
            self.current_file = file_path
            return True, formatted_text, file_path
            
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self.parent,
                "読み込みエラー",
                f"無効なJSONフォーマットです:\n{str(e)}"
            )
            return False, None, None
            
        except Exception as e:
            QMessageBox.warning(
                self.parent,
                "読み込みエラー",
                f"ファイルの読み込みに失敗しました:\n{str(e)}"
            )
            return False, None, None
            
    def get_current_file(self) -> Optional[str]:
        """現在のファイルパスを取得"""
        return self.current_file
        
    def clear(self):
        """状態をクリア"""
        self.current_file = None
