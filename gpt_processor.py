import os
import json
from openai import OpenAI
from datetime import datetime

class GPTProcessor:
    def __init__(self):
        # APIキーの読み込み
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.client = OpenAI(api_key=config.get('openaiApiKey'))
                if not self.client.api_key or self.client.api_key == 'YOUR_OPENAI_API_KEY':
                    raise ValueError('OpenAI APIキーが設定されていません')
        except Exception as e:
            raise Exception(f'設定エラー: {str(e)}')

        # デフォルトプロンプトの読み込み
        self.prompt = self._load_prompt()

    def _load_prompt(self):
        """プロンプトファイルを読み込む"""
        try:
            with open('default_prompt.txt', 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            # デフォルトプロンプトファイルが存在しない場合は作成
            default_prompt = "以下の文章を英語に翻訳してください。"
            with open('default_prompt.txt', 'w', encoding='utf-8') as f:
                f.write(default_prompt)
            return default_prompt

    def save_prompt(self, prompt):
        """新しいプロンプトを保存"""
        with open('default_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(prompt)
        self.prompt = prompt

    def process_text(self, text):
        """テキストをChatGPT APIで処理"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{self.prompt}\n\n{text}"}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f'ChatGPT API エラー: {str(e)}')

    def save_result(self, original_path, text):
        """処理結果を保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            os.path.dirname(original_path),
            f'{os.path.splitext(os.path.basename(original_path))[0]}_gpt_{timestamp}.txt'
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return output_path
