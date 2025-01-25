import os
import sys
import time
import json
import traceback
from datetime import datetime
from gpt_processor import GPTProcessor
from typing import List, Optional, Dict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar,
    QTextEdit, QFrame, QStyleFactory, QCheckBox, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from moco_client import MocoVoiceClient, MocoVoiceError, MIME_TYPES
from audio_splitter import AudioSplitter
from result_merger import TranscriptionMerger

class TranscriptionWorker(QThread):
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
            progress_start = total_progress
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

class TranscriptionGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker = None
        
    def initUI(self):
        self.setWindowTitle("MocoVoice 文字起こし")
        self.setMinimumWidth(1200)
        self.setMinimumHeight(800)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # 左パネル (操作パネル)
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        
        # ファイル選択部分
        file_frame = QFrame()
        file_layout = QVBoxLayout(file_frame)
        
        self.input_path_label = QLabel("ファイルが選択されていません")
        file_layout.addWidget(self.input_path_label)
        
        browse_button = QPushButton("ファイルを選択")
        browse_button.clicked.connect(self.browse_input_file)
        file_layout.addWidget(browse_button)
        
        left_layout.addWidget(file_frame)
        
        # オプション部分
        options_frame = QFrame()
        options_layout = QVBoxLayout(options_frame)
        
        self.speaker_checkbox = QCheckBox("話者分離")
        self.speaker_checkbox.setChecked(True)  # デフォルトでオン
        self.timestamp_checkbox = QCheckBox("タイムスタンプ")
        self.timestamp_checkbox.setChecked(True)  # デフォルトでオン
        self.punctuation_checkbox = QCheckBox("句読点の自動挿入")
        self.punctuation_checkbox.setChecked(True)  # デフォルトでオン
        
        options_layout.addWidget(self.speaker_checkbox)
        options_layout.addWidget(self.timestamp_checkbox)
        options_layout.addWidget(self.punctuation_checkbox)
        
        left_layout.addWidget(options_frame)
        
        # 実行ボタンとプログレスバー
        control_frame = QFrame()
        control_layout = QVBoxLayout(control_frame)
        
        # ボタンを横に並べるレイアウト
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("文字起こし開始")
        self.run_button.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        self.run_button.clicked.connect(self.run_transcription)
        button_layout.addWidget(self.run_button)
        
        self.cancel_button = QPushButton("中止")
        self.cancel_button.setFont(QFont("Helvetica", 12))
        self.cancel_button.clicked.connect(self.cancel_transcription)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
        control_layout.addLayout(button_layout)
        
        self.progress_bar = QProgressBar()
        control_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("ファイルを選択してください")
        control_layout.addWidget(self.status_label)
        
        left_layout.addWidget(control_frame)

        # GPT処理部分
        gpt_frame = QFrame()
        gpt_layout = QVBoxLayout(gpt_frame)
        
        gpt_label = QLabel("ChatGPT処理")
        gpt_label.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        gpt_layout.addWidget(gpt_label)
        
        # プロンプト編集エリア
        prompt_frame = QFrame()
        prompt_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        prompt_layout = QVBoxLayout(prompt_frame)
        
        prompt_header = QHBoxLayout()
        prompt_label = QLabel("プロンプト")
        prompt_label.setFont(QFont("Helvetica", 10))
        prompt_header.addWidget(prompt_label)
        
        save_prompt_button = QPushButton("保存")
        save_prompt_button.setMaximumWidth(60)
        save_prompt_button.clicked.connect(self.save_prompt)
        prompt_header.addWidget(save_prompt_button)
        prompt_layout.addLayout(prompt_header)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("プロンプトを入力してください")
        self.prompt_edit.setMinimumHeight(200)  # 高さをさらに増やす
        prompt_layout.addWidget(self.prompt_edit)
        
        gpt_layout.addWidget(prompt_frame)
        
        # GPT処理ボタン
        process_button = QPushButton("GPT処理実行")
        process_button.setFont(QFont("Helvetica", 11))
        process_button.clicked.connect(self.process_with_gpt)
        gpt_layout.addWidget(process_button)
        
        left_layout.addWidget(gpt_frame)
        left_layout.addStretch()
        
        # 右パネル (タブ付きパネル)
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        right_layout = QVBoxLayout(right_panel)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        
        # ログタブ
        self.debug_text = QTextEdit()
        self.debug_text.setReadOnly(True)
        self.debug_text.setFont(QFont("Menlo", 11))
        self.tab_widget.addTab(self.debug_text, "ログ")
        
        # 結果タブ
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Helvetica", 11))
        self.tab_widget.addTab(self.result_text, "結果")
        
        right_layout.addWidget(self.tab_widget)
        
        # レイアウトの追加
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        
        # スタイル設定
        self.setStyle()
        
        # APIキーの読み込みとクライアントの初期化
        self.gpt_processor = None
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                api_key = config.get('apiKey')
                if not api_key or api_key == 'YOUR_API_KEY_HERE':
                    raise ValueError('APIキーが設定されていません')
                self.client = MocoVoiceClient(api_key)
        except Exception as e:
            self.status_label.setText(f'設定エラー: {str(e)}')
            self.run_button.setEnabled(False)
            return

        # GPTProcessorの初期化
        try:
            self.gpt_processor = GPTProcessor()
            # 保存されているプロンプトを読み込む
            self.prompt_edit.setText(self.gpt_processor.prompt)
        except Exception as e:
            self.status_label.setText(f'GPT設定エラー: {str(e)}')
        
    def setStyle(self):
        # ダークモードパレット
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        self.setPalette(palette)
        
    def browse_input_file(self):
        extensions = " ".join(f"*{ext}" for ext in MIME_TYPES.keys())
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "音声/動画ファイルを選択",
            "",
            f"メディアファイル ({extensions});;すべてのファイル (*.*)"
        )
        if file_name:
            self.input_path_label.setText(file_name)
            self.status_label.setText("ファイルが選択されました")
            
    def run_transcription(self):
        input_path = self.input_path_label.text()
        
        if input_path == "ファイルが選択されていません":
            self.status_label.setText("入力ファイルを選択してください")
            return
            
        if not os.path.exists(input_path):
            self.status_label.setText("入力ファイルが見つかりません")
            return
            
        self.run_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.debug_text.clear()
        self.result_text.clear()
        self.tab_widget.setCurrentIndex(0)  # ログタブに切り替え
        
        options = {
            'speaker_diarization': self.speaker_checkbox.isChecked(),
            'timestamp': self.timestamp_checkbox.isChecked(),
            'punctuation': self.punctuation_checkbox.isChecked()
        }
        
        self.worker = TranscriptionWorker(self.client, input_path, options)
        self.worker.status.connect(self.status_label.setText)
        self.worker.debug.connect(self.log_debug)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_transcription_complete)
        self.worker.error.connect(self.on_transcription_error)
        self.worker.start()

    def cancel_transcription(self):
        if self.worker:
            self.worker.cancel()
            self.cancel_button.setEnabled(False)
        
    def log_debug(self, message):
        self.debug_text.append(message)
        # 自動スクロール
        scrollbar = self.debug_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def on_transcription_complete(self, text):
        self.result_text.setText(text)
        self.tab_widget.setCurrentIndex(1)  # 結果タブに切り替え
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
    def on_transcription_error(self, error_message):
        error_guidance = """
エラーが発生しました:
{error_message}

考えられる原因:
1. サーバーが一時的に混雑している
2. サーバーがメンテナンス中
3. ネットワーク接続に問題がある

対処方法:
1. しばらく時間をおいて再試行してください
2. ネットワーク接続を確認してください
3. 問題が続く場合は、サポートにお問い合わせください
"""
        self.log_debug(error_guidance.format(error_message=error_message))
        self.status_label.setText("エラーが発生しました。詳細はログを確認してください。")
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def save_prompt(self):
        """プロンプトを保存"""
        if self.gpt_processor:
            prompt_text = self.prompt_edit.toPlainText()
            try:
                self.gpt_processor.save_prompt(prompt_text)
                self.status_label.setText("プロンプトを保存しました")
                # 保存成功を視覚的にフィードバック
                save_button = self.sender()
                original_text = save_button.text()
                save_button.setText("✓")
                save_button.setEnabled(False)
                
                # 1秒後に元に戻す
                QTimer.singleShot(1000, lambda: (
                    save_button.setText(original_text),
                    save_button.setEnabled(True)
                ))
            except Exception as e:
                self.status_label.setText(f"プロンプト保存エラー: {str(e)}")

    def process_with_gpt(self):
        """GPTで処理を実行"""
        if not self.gpt_processor:
            self.status_label.setText("GPTProcessorが初期化されていません")
            return

        result_text = self.result_text.toPlainText()
        if not result_text:
            self.status_label.setText("処理するテキストがありません")
            return

        try:
            # GPT処理を実行
            processed_text = self.gpt_processor.process_text(result_text)
            
            # 結果を保存
            input_path = self.input_path_label.text()
            output_path = self.gpt_processor.save_result(input_path, processed_text)
            
            # 結果を表示
            self.result_text.setText(processed_text)
            self.status_label.setText(f"GPT処理完了: {output_path}")
            
        except Exception as e:
            self.status_label.setText(f"GPT処理エラー: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = TranscriptionGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
