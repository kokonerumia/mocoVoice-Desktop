"""
文字起こし結果の表示を担当するモジュール
"""
import json
import tempfile
import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import QUrl

from .transcript_formatter import TranscriptFormatter

class TranscriptViewWidget(QWebEngineView):
    """文字起こし結果の表示ウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.formatter = TranscriptFormatter()
        self.current_temp_file = None
        self.setup_settings()
        
    def setup_settings(self):
        """WebEngineの設定"""
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, False)
        self.setZoomFactor(1.0)
        
    def set_html(self, text: str):
        """HTMLを設定"""
        try:
            # 既存の一時ファイルを削除
            if self.current_temp_file:
                try:
                    os.unlink(self.current_temp_file)
                except:
                    pass
                    
            # JSONをパースしてHTML形式に変換
            data = json.loads(text)
            formatted_text = self.formatter.format_transcript(text)
            
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(formatted_text)
                self.current_temp_file = f.name
                
            # HTMLを表示
            self.load(QUrl.fromLocalFile(self.current_temp_file))
            
        except json.JSONDecodeError:
            # JSONでない場合はプレーンテキストとして表示
            html = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: Helvetica, sans-serif;
                        line-height: 1.6;
                        padding: 20px;
                        white-space: pre-wrap;
                    }}
                </style>
            </head>
            <body>
                {text}
            </body>
            </html>
            """
            self.setHtml(html)
            
    def cleanup(self):
        """終了処理"""
        if self.current_temp_file:
            try:
                os.unlink(self.current_temp_file)
            except:
                pass
