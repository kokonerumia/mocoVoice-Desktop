"""
メディア変換モジュール
"""
import os
import tempfile
import subprocess
from datetime import datetime

class MediaConverter:
    """メディアファイル変換クラス"""
    
    @staticmethod
    def convert_to_audio(input_path: str) -> str:
        """動画ファイルを音声ファイルに変換

        Args:
            input_path (str): 入力ファイルのパス

        Returns:
            str: 変換後の音声ファイルのパス
        """
        # 入力ファイルの拡張子を確認
        _, ext = os.path.splitext(input_path)
        if ext.lower() in ['.wav', '.mp3', '.m4a', '.aac']:
            # すでに音声ファイルの場合は変換不要
            return input_path
            
        # 一時ファイルのパスを生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"audio_{timestamp}.wav")
        
        try:
            # ffmpegを使用して音声を抽出
            subprocess.run([
                'ffmpeg',
                '-i', input_path,  # 入力ファイル
                '-vn',  # 映像を無効化
                '-acodec', 'pcm_s16le',  # 音声コーデック
                '-ar', '44100',  # サンプリングレート
                '-ac', '2',  # チャンネル数
                '-y',  # 既存ファイルを上書き
                output_path
            ], check=True, capture_output=True)
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"音声抽出エラー: {e.stderr.decode()}")
        except Exception as e:
            raise RuntimeError(f"予期せぬエラー: {str(e)}")
