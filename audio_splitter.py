import os
from pydub import AudioSegment
from mutagen import File
from typing import List, Tuple

class AudioSplitter:
    MAX_DURATION_MINUTES = 55  # 余裕を持って55分に設定

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """音声ファイルの長さを分単位で取得（メタデータから高速に取得）"""
        try:
            audio = File(file_path)
            if audio is None:
                # mutagenで読めない場合はpydubにフォールバック
                audio_segment = AudioSegment.from_file(file_path)
                return len(audio_segment) / (1000 * 60)
            
            if hasattr(audio.info, 'length'):
                return audio.info.length / 60  # 秒から分に変換
            
            # pydubにフォールバック
            audio_segment = AudioSegment.from_file(file_path)
            return len(audio_segment) / (1000 * 60)
        except Exception as e:
            # エラーが発生した場合はpydubにフォールバック
            audio_segment = AudioSegment.from_file(file_path)
            return len(audio_segment) / (1000 * 60)

    @staticmethod
    def split_audio(file_path: str, output_dir: str = None) -> List[Tuple[str, float]]:
        """音声ファイルを指定された長さで分割"""
        if output_dir is None:
            output_dir = os.path.dirname(file_path)

        # 入力ファイルを読み込み
        audio = AudioSegment.from_file(file_path)
        total_duration = len(audio)
        max_duration_ms = AudioSplitter.MAX_DURATION_MINUTES * 60 * 1000

        # 分割が必要ない場合は元のファイルを返す
        if total_duration <= max_duration_ms:
            return [(file_path, total_duration / (1000 * 60))]

        # ファイル名の生成
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        ext = os.path.splitext(file_path)[1]

        # 分割処理
        chunks = []
        start = 0
        chunk_number = 1

        while start < total_duration:
            end = min(start + max_duration_ms, total_duration)
            chunk = audio[start:end]
            
            # 分割ファイルの保存
            chunk_path = os.path.join(output_dir, f"{base_name}_part{chunk_number}{ext}")
            chunk.export(chunk_path, format=ext.lstrip('.'))
            
            # 結果を記録
            chunk_duration = len(chunk) / (1000 * 60)  # 分単位
            chunks.append((chunk_path, chunk_duration))
            
            start = end
            chunk_number += 1

        return chunks

    @staticmethod
    def cleanup_chunks(chunk_files: List[str]) -> None:
        """分割ファイルを削除"""
        for file_path in chunk_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: Failed to delete {file_path}: {e}")
