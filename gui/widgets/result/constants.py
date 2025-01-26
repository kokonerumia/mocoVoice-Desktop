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
    "body": """
        font-family: -apple-system, BlinkMacSystemFont, Helvetica, sans-serif;
        line-height: 1.6;
        padding: 20px;
        max-width: 800px;
        margin: 0 auto;
        background-color: #1e1e1e;
        color: #e0e0e0;
    """,
    "speaker": """
        margin-top: 20px;
        font-size: 1.1em;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 2px;
        background-color: rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
    """,
    "content": """
        margin: 0 0 12px 20px;
        padding: 8px 12px;
        background-color: #2d2d2d;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        position: relative;
    """,
    "timestamp": """
        color: #888888;
        font-size: 0.7em;
        font-family: ui-monospace, Menlo, monospace;
        display: inline-block;
        margin-bottom: 6px;
        opacity: 0.7;
        background-color: rgba(0, 0, 0, 0.2);
        padding: 1px 3px;
        border-radius: 2px;
        letter-spacing: -0.3px;
    """,
    "text": """
        font-size: 1em;
        line-height: 1.5;
        color: #e0e0e0;
        display: block;
        word-wrap: break-word;
    """
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
    "analysis": 1,
    "ai_result": 2
}

# タブタイトル
TAB_TITLES = {
    "result": "文字起こし結果",
    "analysis": "会話分析",
    "ai_result": "AI処理結果"
}
