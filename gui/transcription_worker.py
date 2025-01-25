"""
文字起こしワーカーモジュール
"""
import os
import json
import time
import traceback
from datetime import datetime
from typing import List, Optional
from PyQt6.QtCore import QThread, pyqtSignal
from moco_client import MocoVoiceClient, MocoVoiceError
from audio_splitter import AudioSplitter
from result_merger import TranscriptionMerger

class TranscriptionWorker(QThread):
    """文字起こしワーカークラス"""
    status = pyqtSignal(str)
    debug = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client: MocoVoiceClient, file_path: str, options: dict):
        super().__init__()
        self.client = client
        self.file_path = file_path
        self.options = options
        self._is_cancelled = False
        self.chunk_files: List[str] = []

    def cancel(self):
        """処理をキャンセル"""
        self._is_cancelled = True
        self.debug.emit("\n処理を中止しています...")

    def cleanup(self):
        """一時ファイルの削除"""
        if self.chunk_files:
            self.debug.emit("\n一時ファイルを削除中...")
            AudioSplitter.cleanup_chunks(self.chunk_files)
            self.chunk_files = []

    def process_chunk(self, chunk_path: str, chunk_duration: float, total_progress: int, chunk_weight: int) -> Optional[str]:
        """1つのチャンクを処理"""
        try:
            # 1. 文字起こしジョブを作成
            self.debug.emit(f"\nチャンク処理開始: {os.path.basename(chunk_path)}")
            self.debug.emit(f"- 長さ: {chunk_duration:.1f}分")
            
            filename = os.path.basename(chunk_path)
            job_data = self.client.create_transcription_job(filename, self.options)
            self.debug.emit(f"ジョブ作成結果: {json.dumps(job_data, indent=2, ensure_ascii=False)}")

            if self._is_cancelled:
                return None

            transcription_id = job_data['transcription_id']
            upload_url = job_data['audio_upload_url']

            # 2. 音声ファイルをアップロード
            self.status.emit("ファイルをアップロード中...")
            self.debug.emit("音声ファイルをアップロード中...")
            
            upload_status = self.client.upload_audio_file(upload_url, chunk_path)
            self.debug.emit(f"アップロード結果: ステータスコード {upload_status}")

            if self._is_cancelled:
                return None

            # 3. 書き起こし開始
            self.debug.emit("書き起こしを開始...")
            try:
                self.client.start_transcription(transcription_id)
                self.debug.emit("書き起こしリクエスト送信完了")
            except MocoVoiceError as e:
                self.debug.emit(f"書き起こし開始時にエラーが発生: {str(e)}")
                self.debug.emit("5秒後に再試行します...")
                time.sleep(5)
                self.client.start_transcription(transcription_id)
                self.debug.emit("書き起こしリクエスト送信完了（再試行成功）")

            if self._is_cancelled:
                return None

            # 4. 結果待機
            self.debug.emit("結果待機中...")
            retry_count = 0
            max_retries = 3

            while True:
                if self._is_cancelled:
                    return None

                try:
                    result = self.client.get_transcription_status(transcription_id)
                    retry_count = 0  # 成功したらリトライカウントをリセット
                except MocoVoiceError as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        raise
                    self.debug.emit(f"ステータス取得時にエラーが発生: {str(e)}")
                    self.debug.emit(f"{retry_count}回目の再試行...")
                    time.sleep(5)
                    continue

                status = result['status']

                status_messages = {
                    'PENDING': '準備中...',
                    'CONVERTING': '変換中...',
                    'IN_PROGRESS': '文字起こし中...',
                    'COMPLETED': '完了',
                    'FAILED': 'エラー',
                    'CANCELLED': 'キャンセル'
                }
                current_status = status_messages.get(status, status)
                self.status.emit(f"状態: {current_status}")
                self.debug.emit(f"現在の状態: {current_status}")

                # プログレスバーの更新
                if status == 'IN_PROGRESS':
                    # IN_PROGRESS状態の間、徐々にプログレスバーを進める
                    progress = min(total_progress + int(chunk_weight * 0.8), total_progress + chunk_weight)
                    self.progress.emit(progress)

                if status == 'COMPLETED':
                    self.progress.emit(total_progress + chunk_weight)
                    break
                elif status in ['FAILED', 'CANCELLED']:
                    raise Exception(f'Transcription {status.lower()}')

                time.sleep(5)

            # 5. 結果を取得
            self.debug.emit("結果を取得中...")
            transcription_text = self.client.get_transcription_result(result['transcription_path'])
            return transcription_text

        except Exception as e:
            self.debug.emit(f"チャンク処理中にエラーが発生: {str(e)}")
            raise

    def run(self):
        """文字起こし処理を実行"""
        try:
            # ファイル情報を表示
            file_size = os.path.getsize(self.file_path)
            self.debug.emit(f"ファイル情報:")
            self.debug.emit(f"- パス: {self.file_path}")
            self.debug.emit(f"- サイズ: {file_size:,} bytes")
            self.debug.emit(f"- 形式: {os.path.splitext(self.file_path)[1]}")
            self.debug.emit(f"- MIMEタイプ: {self.client.get_mime_type(self.file_path)}")
            
            # ファイルの長さを確認
            self.debug.emit("\n音声ファイルを解析中...")
            self.progress.emit(5)
            duration = AudioSplitter.get_audio_duration(self.file_path)
            self.debug.emit(f"音声の長さ: {duration:.1f}分")

            # 必要に応じてファイルを分割
            self.debug.emit("\nファイル分割の準備...")
            self.progress.emit(10)
            chunks = AudioSplitter.split_audio(self.file_path)
            total_chunks = len(chunks)
            self.debug.emit(f"分割数: {total_chunks}")

            # 分割ファイルのパスを保存（後で削除するため）
            if total_chunks > 1:
                self.chunk_files = [chunk[0] for chunk in chunks]
                # 元ファイルが分割ファイルリストに含まれている場合のみ削除
                if self.file_path in self.chunk_files:
                    self.chunk_files.remove(self.file_path)

            # 各チャンクを処理
            results = []
            total_progress = 10  # ファイル分析で10%使用
            chunk_weight = 90 // total_chunks  # 残り90%を各チャンクに分配

            for i, (chunk_path, chunk_duration) in enumerate(chunks, 1):
                if self._is_cancelled:
                    break

                self.debug.emit(f"\n=== チャンク {i}/{total_chunks} の処理を開始 ===")
                result = self.process_chunk(chunk_path, chunk_duration, total_progress, chunk_weight)
                if result:
                    results.append(result)
                total_progress += chunk_weight

            if self._is_cancelled:
                raise Exception("処理が中止されました")

            # 結果を統合
            if results:
                self.debug.emit("\n結果を統合中...")
                if self.options.get('timestamp'):
                    final_text = TranscriptionMerger.merge_json_results(results)
                else:
                    final_text = TranscriptionMerger.merge_results(
                        results,
                        include_speaker=self.options.get('speaker_diarization', False)
                    )

                # 結果を保存
                self.debug.emit("\n結果を保存...")
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = os.path.join(
                    os.path.dirname(self.file_path),
                    f'{os.path.splitext(os.path.basename(self.file_path))[0]}_{timestamp}.txt'
                )

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(final_text)
                self.debug.emit(f"結果を保存しました: {output_path}")

                self.progress.emit(100)
                self.status.emit("完了")
                self.finished.emit(final_text)

        except Exception as e:
            error_details = traceback.format_exc()
            self.debug.emit(f"\nエラーが発生しました:\n{error_details}")
            self.error.emit(str(e))
            self.status.emit("エラーが発生しました")
        
        finally:
            self.cleanup()
