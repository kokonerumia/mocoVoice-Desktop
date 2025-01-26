"""
文字起こし結果の整形を担当するモジュール
"""
from typing import Dict, List, Optional
import json

from .constants import HTML_STYLES, REQUIRED_KEYS
from .utils import format_time, generate_speaker_color, parse_json_safely, convert_plain_text_to_json

class TranscriptFormatter:
    """文字起こし結果の整形クラス"""
    
    def __init__(self):
        self.speaker_colors: Dict[str, str] = {}
        
    def clear_speaker_colors(self):
        """話者の色情報をクリア"""
        self.speaker_colors.clear()

    def validate_transcript_json(self, text: str) -> bool:
        """文字起こし結果のJSONを検証"""
        success, data, _ = parse_json_safely(text)
        if not success or not isinstance(data, list):
            return False
        
        # 各要素が必要なキーを持っているか確認
        for item in data:
            if not isinstance(item, dict):
                return False
            if not all(key in item for key in REQUIRED_KEYS):
                return False
            
            # 数値型の検証
            if not isinstance(item["start"], (int, float)):
                return False
            if not isinstance(item["end"], (int, float)):
                return False
            
            # テキストの検証
            if not isinstance(item["text"], str):
                return False
        
        return True

    def _get_speaker_color(self, speaker: str) -> str:
        """話者の色を取得（未設定の場合は生成）"""
        if speaker not in self.speaker_colors:
            self.speaker_colors[speaker] = generate_speaker_color(speaker)
        return self.speaker_colors[speaker]

    def _format_speaker_section(self, speaker: str, index: int) -> str:
        """話者セクションのHTML生成"""
        color = self._get_speaker_color(speaker)
        # 話者名を表示用に整形（HTMLエスケープを行う）
        display_speaker = speaker.replace('<', '&lt;').replace('>', '&gt;')
        return (
            f'<div class="speaker" id="speaker_{index}" '
            f'data-speaker="{display_speaker}" '
            f'style="color: {color}; background-color: {color}10;">'
            f'<span style="display: inline-block; padding: 2px 8px;">{display_speaker}</span>'
            f'</div>'
        )

    def _format_content_section(self, start_time: str, end_time: str, text: str) -> str:
        """発話内容セクションのHTML生成"""
        return (
            '<div class="content">'
            f'<div class="timestamp">[{start_time} - {end_time}]</div>'
            f'<div class="text">{text}</div>'
            '</div>'
        )

    def format_transcript(self, text: str) -> str:
        """文字起こし結果を整形"""
        try:
            # JSONとして解析
            success, data, error = parse_json_safely(text)
            if not success:
                return error
            
            # プレーンテキストの場合はJSONに変換
            if isinstance(data, str):
                data = [convert_plain_text_to_json(data)]
            
            # スタイル定義
            styles = f"""
            <style>
                body {{ {HTML_STYLES["body"]} }}
                .speaker {{ {HTML_STYLES["speaker"]} border-radius: 4px; }}
                .speaker span {{ border-radius: 2px; }}
                .content {{ {HTML_STYLES["content"]} }}
                .timestamp {{ {HTML_STYLES["timestamp"]} }}
                .text {{ {HTML_STYLES["text"]} }}
            </style>
            """
            
            # HTML形式で整形
            html = ['<html><head><meta charset="utf-8">', styles, '</head><body>']
            current_speaker = None
            speaker_index = 0
            
            for item in data:
                start_time = format_time(item["start"])
                end_time = format_time(item["end"])
                speaker = item.get("speaker", "SPEAKER_01")
                text = item["text"]
                
                # 話者が変わった場合は話者名を表示
                if speaker != current_speaker:
                    html.append(self._format_speaker_section(speaker, speaker_index))
                    current_speaker = speaker
                    speaker_index += 1
                
                # 発話内容を表示
                html.append(self._format_content_section(start_time, end_time, text))
            
            html.append("</body></html>")
            return "\n".join(html)
            
        except Exception as e:
            return f"エラー: 文字起こし結果の整形に失敗しました。\n{str(e)}"
