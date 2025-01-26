"""
メディア変換モジュール
"""
import os
import tempfile
import subprocess
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

class MediaConverter(QObject):
    """メディアファイル変換クラス"""
    # 進捗通知用シグナル
    progress_updated = pyqtSignal(str, int)  # メッセージ, 進捗率(0-100)
    
    def __init__(self):
        super().__init__()
    
    @classmethod
    def check_ffmpeg(cls):
        """ffmpegが利用可能かチェック

        Returns:
            bool: ffmpegが利用可能な場合はTrue
        """
        try:
            subprocess.run(['/opt/homebrew/bin/ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def convert_to_audio(self, input_path: str) -> str:
        """動画ファイルを音声ファイルに変換

        Args:
            input_path (str): 入力ファイルのパス

        Returns:
            str: 変換後の音声ファイルのパス

        Raises:
            RuntimeError: ffmpegが見つからない場合やメディア変換に失敗した場合
        """
        # ffmpegの存在チェック
        if not self.__class__.check_ffmpeg():
            raise RuntimeError(
                "ffmpegが見つかりません。以下のコマンドでインストールしてください：\n\n"
                "macOSの場合：\n"
                "brew install ffmpeg\n\n"
                "Windowsの場合：\n"
                "1. https://www.ffmpeg.org/download.html からダウンロード\n"
                "2. 解凍したファイルをC:\\ffmpegに配置\n"
                "3. システム環境変数のPATHにC:\\ffmpeg\\binを追加"
            )

        # 入力ファイルの拡張子を確認
        _, ext = os.path.splitext(input_path)
        if ext.lower() in ['.mp3', '.m4a', '.aac']:
            # すでに効率的な音声形式の場合は変換不要
            return input_path
            
        # 出力ファイルのパスを生成（元の動画と同じディレクトリ）
        dirname = os.path.dirname(input_path)
        basename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(dirname, f"{basename}_audio.mp3")
        
        try:
            # 進捗通知開始
            self.progress_updated.emit("メディアファイルを読み込んでいます...", 0)
            
            # ffmpegを使用して音声を抽出
            process = subprocess.Popen([
                '/opt/homebrew/bin/ffmpeg',
                '-i', input_path,  # 入力ファイル
                '-vn',  # 映像を無効化
                '-acodec', 'libmp3lame',  # MP3コーデック
                '-ar', '44100',  # サンプリングレート
                '-ac', '1',  # モノラル
                '-b:a', '128k',  # ビットレート
                '-y',  # 既存ファイルを上書き
                '-progress', 'pipe:1',  # 進捗情報をパイプに出力
                output_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            # 進捗情報の処理
            duration = None
            time = 0
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                    
                if 'Duration' in line:
                    # 動画の長さを取得
                    time_str = line.split('Duration: ')[1].split(',')[0]
                    h, m, s = map(float, time_str.split(':'))
                    duration = h * 3600 + m * 60 + s
                elif 'time=' in line:
                    # 現在の処理時間を取得
                    time_str = line.split('time=')[1].split()[0]
                    h, m, s = map(float, time_str.split(':'))
                    time = h * 3600 + m * 60 + s
                    
                    if duration:
                        progress = int((time / duration) * 100)
                        self.progress_updated.emit("音声を抽出しています...", progress)
            
            # プロセスの終了を待機
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args)
                
            self.progress_updated.emit("音声の抽出が完了しました", 100)
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"音声抽出エラー: {e.stderr.decode()}")
        except Exception as e:
            raise RuntimeError(f"予期せぬエラー: {str(e)}")
