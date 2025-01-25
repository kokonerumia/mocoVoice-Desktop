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
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # 秒

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
                response = requests.request(method, url, **kwargs)
                if response.status_code == 500:
                    raise MocoVoiceError("サーバーエラーが発生しました")
                response.raise_for_status()
                return response
            except (requests.exceptions.RequestException, MocoVoiceError) as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                continue
        
        if isinstance(last_error, requests.exceptions.HTTPError):
            if last_error.response.status_code == 400:
                raise MocoVoiceError("リクエストが不正です")
            elif last_error.response.status_code == 401:
                raise MocoVoiceError("APIキーが無効です")
            elif last_error.response.status_code == 403:
                raise MocoVoiceError("アクセス権限がありません")
            elif last_error.response.status_code == 404:
                raise MocoVoiceError("リソースが見つかりません")
            elif last_error.response.status_code == 500:
                raise MocoVoiceError("サーバーエラーが発生しました")
            else:
                raise MocoVoiceError(f"APIエラー: {last_error}")
        else:
            raise MocoVoiceError(f"ネットワークエラー: {last_error}")

    def create_transcription_job(self, filename: str, options: Optional[Dict] = None) -> Dict:
        """文字起こしジョブを作成"""
        url = f'{self.base_url}/transcriptions/upload'
        
        data = {
            'filename': filename,
            'language': options.get('language', 'ja'),
            'transcription_model': 'timestamp' if options.get('timestamp') else 'default',
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
        response = self._make_request('POST', url, headers=self.headers)
        return response.json()

    def get_transcription_status(self, transcription_id: str) -> Dict:
        """文字起こしの状態を取得"""
        url = f'{self.base_url}/transcriptions/{transcription_id}'
        response = self._make_request('GET', url, headers=self.headers)
        return response.json()

    def get_transcription_result(self, transcription_path: str) -> str:
        """文字起こし結果を取得"""
        response = self._make_request('GET', transcription_path)
        return response.text
