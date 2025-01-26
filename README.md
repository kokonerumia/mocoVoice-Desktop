# MocoVoice Desktop

## 機能

- 音声/動画ファイルの文字起こし
  - 話者分離（話者ごとに自動で色分け表示）
  - タイムスタンプ（時:分:秒.ミリ秒形式）
  - 句読点の自動挿入
  - その場で音声録音可能
  - 動画ファイル(.mp4, .mov, .avi等)から自動で音声抽出
  - ネットワーク負荷軽減のためローカルで音声変換処理
- テキストファイルの読み込み/編集
  - 文字起こし結果はJSON形式で保存/読み込み
  - 話者情報とタイムスタンプを含む構造化データ
  - 表示モード/編集モードの切り替え
  - リアルタイムJSONバリデーション
  - 上書き保存機能
- AI処理機能
  - カスタマイズ可能なプロンプト
  - プロンプトの保存/読み込み
  - 処理結果の保存
- ログ表示
  - ポップアップ形式のログウィンドウ
  - エラー発生時の自動表示
  - 処理状況のリアルタイム表示
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
   - 処理状況は「ログを表示」ボタンで確認可能
   - 完了すると文字起こし結果が表示
     - 話者ごとに自動で色分けされて表示
     - タイムスタンプは時:分:秒.ミリ秒形式で表示

3. 文字起こし結果の表示/編集
   - 「編集モード」ボタンをクリックして編集モードに切り替え
   - JSON形式で直接編集可能
   - リアルタイムでJSONの検証を実行
   - 「表示モード」ボタンをクリックして色分け表示に戻る
   - 「名前を付けて保存」または「上書き保存」ボタンで保存

4. 文字起こし結果の読み込み
   - 「テキストを読み込む」ボタンをクリックしてJSONファイルを選択
   - 自動的に色分け表示で表示
   - 「編集モード」ボタンで編集可能

5. AI処理
   - プロンプトを入力（または読み込み）
   - 「AI処理実行」ボタンをクリック
   - 処理結果はAI処理結果タブに表示
   - 「結果を保存」ボタンで結果を保存可能

6. ログの確認
   - 「ログを表示」ボタンをクリックしてログウィンドウを表示
   - エラー発生時は自動的に表示
   - 処理状況をリアルタイムで確認可能

7. テーマの切り替え
   - 🌓ボタンをクリックしてダークモード/ライトモードを切り替え

## プロジェクト構成

```
mocoVoice-Desktop/
├── gui/                      # GUIモジュール
│   ├── widgets/             # ウィジェットコンポーネント
│   │   ├── file_panel.py    # ファイル選択パネル
│   │   ├── options_panel.py # オプションパネル
│   │   ├── control_panel.py # コントロールパネル
│   │   ├── ai_panel.py      # AI処理パネル
│   │   ├── log_dialog.py    # ログ表示ダイアログ
│   │   └── result/          # 結果表示関連
│   │       ├── __init__.py
│   │       ├── constants.py  # 定数定義
│   │       ├── utils.py     # ユーティリティ関数
│   │       ├── transcript_formatter.py  # 文字起こし結果整形
│   │       ├── file_handler.py  # ファイル操作
│   │       └── result_panel.py  # 結果表示パネル
│   ├── transcription_worker.py  # 文字起こし処理ワーカー
│   └── main_window.py       # メインウィンドウ
├── audio_splitter.py        # 音声分割モジュール
├── gpt_processor.py         # AI処理モジュール
├── moco_client.py           # MocoVoice APIクライアント
├── result_merger.py         # 結果統合モジュール
├── main.py                  # メインエントリーポイント
├── config.json              # 設定ファイル
└── requirements.txt         # 依存パッケージ
```

## 文字起こし結果のJSON形式

```json
[
  {
    "start": 0.4865625,      // 開始時間（秒）
    "end": 1.7665625,        // 終了時間（秒）
    "text": "こんにちは",     // 発話内容
    "speaker": "SPEAKER_01",  // 話者ID
    "lang": "ja"             // 言語
  },
  ...
]
```

## 開発環境

- Python 3.8以上
- PyQt6
- OpenAI API
- MocoVoice API
