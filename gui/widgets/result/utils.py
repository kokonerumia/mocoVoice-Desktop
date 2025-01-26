"""
結果表示パネルのユーティリティ関数
"""
import json
import colorsys
from datetime import timedelta
from typing import Dict, Any, Tuple

from .constants import BASE_HUES

def format_time(seconds: float) -> str:
    """秒数を時:分:秒.ミリ秒の形式に変換"""
    time = timedelta(seconds=seconds)
    hours = int(time.total_seconds() // 3600)
    minutes = int((time.total_seconds() % 3600) // 60)
    seconds = time.total_seconds() % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def generate_speaker_color(speaker_id: str) -> str:
    """話者IDから色を動的に生成"""
    try:
        # 話者IDから数値を抽出
        speaker_num = int(''.join(filter(str.isdigit, speaker_id)))
    except ValueError:
        speaker_num = hash(speaker_id)
    
    # 話者番号に基づいて色相を選択
    hue = BASE_HUES[speaker_num % len(BASE_HUES)]
    
    # HSLからRGBに変換（彩度70%、明度60%で固定）
    rgb = colorsys.hls_to_rgb(hue/360, 0.6, 0.7)
    
    # RGBを16進数形式に変換
    return '#{:02x}{:02x}{:02x}'.format(
        int(rgb[0]*255),
        int(rgb[1]*255),
        int(rgb[2]*255)
    )

def parse_json_safely(text: str) -> Tuple[bool, Any, str]:
    """JSONを安全にパースし、結果とエラーメッセージを返す"""
    try:
        data = json.loads(text)
        return True, data, ""
    except json.JSONDecodeError as e:
        return False, None, f"JSONの解析に失敗しました: {str(e)}"
    except Exception as e:
        return False, None, f"予期せぬエラーが発生しました: {str(e)}"

def ensure_json_extension(file_path: str) -> str:
    """ファイルパスの拡張子が.jsonでない場合は追加"""
    if not file_path.lower().endswith('.json'):
        return file_path + '.json'
    return file_path

def convert_plain_text_to_json(text: str) -> Dict:
    """プレーンテキストを最小限のJSON形式に変換"""
    return {
        "start": 0,
        "end": 0,
        "text": text,
        "speaker": "SPEAKER_01"
    }
