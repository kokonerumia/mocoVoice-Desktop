"""
ファイル操作を担当するモジュール
"""
from typing import Tuple, Optional
import json
from PyQt6.QtWidgets import QWidget, QFileDialog

from .constants import FILE_FILTERS
from .utils import ensure_json_extension, parse_json_safely
from .transcript_formatter import TranscriptFormatter

class FileHandler:
    """ファイル操作クラス"""
    
    def __init__(self, parent: QWidget):
        self.parent = parent
        self.formatter = TranscriptFormatter()

    def save_transcript(self, text: str) -> Optional[str]:
        """文字起こし結果を保存"""
        file_name, _ = QFileDialog.getSaveFileName(
            self.parent,
            "文字起こし結果を保存",
            "",
            FILE_FILTERS["json"]
        )
        
        if not file_name:
            return None

        try:
            # 拡張子の確認と追加
            file_name = ensure_json_extension(file_name)
            
            # テキストをJSONとしてパース
            success, data, error = parse_json_safely(text)
            if not success:
                raise ValueError(error)
            
            # JSONとして保存
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return file_name
            
        except Exception as e:
            print(f"保存エラー: {str(e)}")
            return None

    def save_text(self, text: str, title: str) -> Optional[str]:
        """通常のテキストとして保存"""
        file_name, _ = QFileDialog.getSaveFileName(
            self.parent,
            title,
            "",
            FILE_FILTERS["text"]
        )
        
        if not file_name:
            return None

        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(text)
            return file_name
            
        except Exception as e:
            print(f"保存エラー: {str(e)}")
            return None

    def load_transcript(self, file_path: str) -> Tuple[bool, str]:
        """文字起こし結果ファイルを読み込み"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # JSONとして検証
            if not self.formatter.validate_transcript_json(content):
                return False, "ファイルの形式が正しくありません。文字起こし結果のJSONファイルを選択してください。"
            
            return True, content
            
        except Exception as e:
            return False, f"ファイルの読み込みに失敗しました: {str(e)}"
