"""
結果表示パネルの定数定義
"""
from typing import Dict, List

# 基本となる色相値のリスト（0-360の値）
BASE_HUES: List[int] = [0, 120, 240, 60, 180, 300, 30, 150, 270, 90, 210, 330]

# デフォルトのフォント設定
FONT_SETTINGS = {
    "debug": {
        "family": "Menlo",
        "size": 11
    },
    "result": {
        "family": "Helvetica",
        "size": 11
    }
}

# HTMLスタイル設定
HTML_STYLES = {
    "body": "font-family: Helvetica, sans-serif;",
    "speaker": "margin-top: 20px;",
    "content": "margin: 5px 0 5px 20px;",
    "timestamp": "color: #666666; font-size: 0.9em;",
    "text": "margin-left: 10px;"
}

# JSONバリデーション設定
REQUIRED_KEYS = {"start", "end", "text"}

# ファイル保存設定
FILE_FILTERS = {
    "json": "JSONファイル (*.json);;すべてのファイル (*.*)",
    "text": "テキストファイル (*.txt);;すべてのファイル (*.*)"
}

# タブインデックス
TAB_INDICES = {
    "result": 0,
    "ai_result": 1
}

# タブタイトル
TAB_TITLES = {
    "result": "文字起こし結果",
    "ai_result": "AI処理結果"
}
