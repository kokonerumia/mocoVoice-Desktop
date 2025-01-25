import os
import json
import time
import requests
from typing import Dict, Optional

MIME_TYPES = {
    '.wav': 'audio/wav',
    '.mp3': 'audio/mpeg',
    '.m4a': 'audio/mp4',
    '.mp4': 'audio/mp4',
}

class MocoVoiceError(Exception):
    """MocoVoice APIのエラー"""
    pass

class MocoVoiceClient:
    MAX_RETRIES = 5
    RETRY_DELAY = 5  # 秒

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.mocomoco.ai/api/v1'
        self.headers = {
            'accept': 'application/json',
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

    def get_mime_type(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        return MIME_TYPES.get(ext, 'application/octet-stream')

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """リトライ機能付きのリクエスト実行"""
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.request(method, url, timeout=30, **kwargs)
                
                # サーバーエラーの場合はリトライ
                if response.status_code >= 500:
                    error_msg = f"サーバーエラー (ステータスコード: {response.status_code})"
                    if attempt < self.MAX_RETRIES - 1:
                        print(f"リトライ {attempt + 1}/{self.MAX_RETRIES}: {error_msg}")
                        time.sleep(self.RETRY_DELAY * (attempt + 1))
                        continue
                    raise MocoVoiceError(error_msg)
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout:
                error_msg = "リクエストがタイムアウトしました"
                if attempt < self.MAX_RETRIES - 1:
                    print(f"リトライ {attempt + 1}/{self.MAX_RETRIES}: {error_msg}")
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                raise MocoVoiceError(error_msg)
                
            except requests.exceptions.ConnectionError as e:
                error_msg = f"接続エラー: {str(e)}"
                if attempt < self.MAX_RETRIES - 1:
                    print(f"リトライ {attempt + 1}/{self.MAX_RETRIES}: {error_msg}")
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                raise MocoVoiceError(error_msg)
                
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    print(f"リトライ {attempt + 1}/{self.MAX_RETRIES}: {str(e)}")
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                break
        
        # 最終的なエラーハンドリング
        if isinstance(last_error, requests.exceptions.HTTPError):
            status_code = last_error.response.status_code
            error_messages = {
                400: "リクエストが不正です",
                401: "APIキーが無効です",
                403: "アクセス権限がありません",
                404: "リソースが見つかりません",
                500: "サーバーエラーが発生しました",
                502: "サーバーが一時的に利用できません",
                503: "サービスが一時的に利用できません",
                504: "ゲートウェイタイムアウト"
            }
            error_msg = error_messages.get(status_code, f"APIエラー (ステータスコード: {status_code})")
            raise MocoVoiceError(error_msg)
        else:
            raise MocoVoiceError(f"ネットワークエラー: {str(last_error)}")

    def create_transcription_job(self, filename: str, options: Optional[Dict] = None) -> Dict:
        """文字起こしジョブを作成"""
        url = f'{self.base_url}/transcriptions/upload'
        
        data = {
            'filename': filename,
            'language': options.get('language', 'ja'),
            'transcription_model': 'default',  # タイムスタンプモデルに問題があるため、一時的にdefaultを使用
            'words': []
        }

        if options.get('speaker_diarization'):
            data['words'].append({'word': '[SPEAKER_DIARIZATION]', 'reading': 'ON'})
        if options.get('punctuation'):
            data['words'].append({'word': '[AUTO_PUNCTUATION]', 'reading': 'ON'})

        response = self._make_request('POST', url, headers=self.headers, json=data)
        return response.json()

    def upload_audio_file(self, upload_url: str, file_path: str) -> int:
        """音声ファイルをアップロード"""
        mime_type = self.get_mime_type(file_path)
        headers = {'Content-Type': mime_type}
        
        with open(file_path, 'rb') as f:
            response = self._make_request('PUT', upload_url, headers=headers, data=f)
        return response.status_code

    def start_transcription(self, transcription_id: str) -> Dict:
        """文字起こしを開始"""
        url = f'{self.base_url}/transcriptions/{transcription_id}/transcribe'
        try:
            response = requests.post(url, headers=self.headers, timeout=30)
            
            # レスポンスの詳細をログ出力
            print(f"Start transcription response: Status={response.status_code}")
            if response.status_code != 200:
                print(f"Response content: {response.text}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Start transcription error: {str(e)}")
            raise MocoVoiceError(f"書き起こし開始エラー: {str(e)}")

    def get_transcription_status(self, transcription_id: str) -> Dict:
        """文字起こしの状態を取得"""
        url = f'{self.base_url}/transcriptions/{transcription_id}'
        response = self._make_request('GET', url, headers=self.headers)
        return response.json()

    def get_transcription_result(self, transcription_path: str) -> str:
        """文字起こし結果を取得"""
        response = self._make_request('GET', transcription_path)
        return response.text
