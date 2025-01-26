# MocoVoice Desktop

## 機能

- 音声/動画ファイルの文字起こし
  - 話者分離
  - タイムスタンプ
  - 句読点の自動挿入
  - その場で音声録音可能
  - 動画ファイル(.mp4, .mov, .avi等)から自動で音声抽出
  - ネットワーク負荷軽減のためローカルで音声変換処理
- テキストファイルの読み込み
- AI処理機能
  - カスタマイズ可能なプロンプト
  - プロンプトの保存/読み込み
  - 処理結果の保存
- ダークモード/ライトモード切り替え

## インストール

1. リポジトリをクローン
```bash
git clone https://github.com/kokonerumia/mocoVoice-Desktop.git
cd mocoVoice-Desktop
```

2. 必要なパッケージとツールをインストール

macOSの場合:
```bash
brew install ffmpeg portaudio  # 必要なツールをインストール
pip install -r requirements.txt  # Pythonパッケージをインストール
```

Linuxの場合:
```bash
sudo apt-get install ffmpeg portaudio19-dev  # Ubuntuの場合
pip install -r requirements.txt
```

Windowsの場合:
```bash
# ffmpegをダウンロードしてPATHに追加してから:
pip install -r requirements.txt
```

3. 設定ファイルの作成
`config.json.example`を`config.json`にコピーし、APIキーを設定:
```bash
cp config.json.example config.json
```

そして`config.json`内のAPIキーを実際の値に置き換えてください:
- `YOUR_MOCO_VOICE_API_KEY`: MocoVoice APIキー
- `YOUR_OPENAI_API_KEY`: OpenAI APIキー

## 使用方法

1. アプリケーションの起動
```bash
python main.py
```

2. 音声/動画ファイルの文字起こし
   - 「音声ファイルを選択」ボタンをクリックして音声ファイル(.wav, .mp3等)や動画ファイル(.mp4, .mov等)を選択
     - 動画ファイルの場合は自動的に音声が抽出されます
   - または「録音」ボタンをクリックしてその場で音声を録音（録音中は赤色表示）
   - 必要に応じてオプション（話者分離、タイムスタンプ、句読点）を設定
   - 「文字起こし開始」ボタンをクリック
   - 処理状況はログタブで確認可能
   - 完了すると結果タブに文字起こし結果が表示

5. テーマの切り替え
   - 右上の🌓ボタンをクリックしてダークモード/ライトモードを切り替え

3. テキストファイルの読み込み
   - 「テキストを読み込む」ボタンをクリックしてテキストファイルを選択
   - 結果タブに内容が表示

4. AI処理
   - プロンプトを入力（または読み込み）
   - 「AI処理実行」ボタンをクリック
   - 処理結果はAI処理結果タブに表示
   - 「結果を保存」ボタンで結果を保存可能

## プロジェクト構成

```
mocoVoice-Desktop/
├── gui/                      # GUIモジュール
│   ├── widgets/             # ウィジェットコンポーネント
│   │   ├── file_panel.py    # ファイル選択パネル
│   │   ├── options_panel.py # オプションパネル
│   │   ├── control_panel.py # コントロールパネル
│   │   ├── ai_panel.py      # AI処理パネル
│   │   └── result_panel.py  # 結果表示パネル
│   ├── transcription_worker.py  # 文字起こし処理ワーカー
│   └── main_window.py       # メインウィンドウ
├── audio_splitter.py        # 音声分割モジュール
├── gpt_processor.py         # AI処理モジュール
├── moco_client.py           # MocoVoice APIクライアント
├── result_merger.py         # 結果統合モジュール
├── main.py                # メインエントリーポイント
├── config.json             # 設定ファイル
└── requirements.txt        # 依存パッケージ
```

## 開発環境

- Python 3.8以上
- PyQt6
- OpenAI API
- MocoVoice API
