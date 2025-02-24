# mocoVoice-Desktop

音声ファイルの文字起こしと分析を行うデスクトップアプリケーション

## 機能

- 音声ファイルの文字起こし
  - 複数の音声フォーマットに対応（wav, mp3, m4a, mp4）
  - 動画ファイルからの音声抽出（mp4, mov, avi, mkv, flv, wmv）
  - 長時間音声の自動分割処理
  - タイムスタンプ付き文字起こし
  - 話者の自動識別

- 会話の分析
  - 発話量の時間変化グラフ
  - 話者ごとの総発話量
  - 発話の遷移パターン分析
  - 会話の統計情報

- 話者の管理
  - 話者名の一括変更
  - 複数話者の統合
  - カラーコードによる視覚的な識別
  - 直感的な編集インターフェース

- テキスト編集機能
  - ダークモード対応のモダンなUI
  - リアルタイムプレビュー
  - JSONフォーマットの自動整形
  - 編集履歴の保持

- AI処理による会話の分析
  - 会話内容の要約
  - キーワード抽出
  - 感情分析
  - カスタマイズ可能なプロンプト

## 必要条件

- Python 3.8以上
- ffmpeg（動画ファイルからの音声抽出に必要）

### ffmpegのインストール

#### macOS
```bash
brew install ffmpeg
```

#### Windows
1. [ffmpeg公式サイト](https://www.ffmpeg.org/download.html)からダウンロード
2. ダウンロードしたファイルを解凍してC:\ffmpegに配置
3. システム環境変数のPATHにC:\ffmpeg\binを追加

## インストール

1. リポジトリをクローン
```bash
git clone https://github.com/kokonerumia/mocoVoice-Desktop.git
cd mocoVoice-Desktop
```

2. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

3. 設定ファイルを作成
```bash
cp config.json.example config.json
```

4. config.jsonを編集
- mocoVoiceApiKey: 文字起こしAPIのキー
- openaiApiKey: AI処理用のOpenAI APIキー

## 使用方法

1. アプリケーションの起動
   - 方法1: mocoVoice.appをApplicationsフォルダにドラッグ＆ドロップしてDockから起動
   - 方法2: ターミナルから起動
     ```bash
     python main.py
     ```

2. 音声/動画ファイルの文字起こし
   - 「ファイルを選択」をクリック
   - 音声ファイル（mp3, wav, m4a）または動画ファイル（mp4, mov, avi等）を選択
   - 必要に応じてオプションを設定（話者分離、句読点の自動挿入など）
   - 「文字起こし開始」をクリックして処理を開始
   - または「録音」をクリックして直接録音を開始

3. 結果の編集・分析
   - 「話者名の編集」で話者の管理
   - 「会話分析」タブで統計情報を確認
   - 「AI処理結果」タブでAIによる分析を実行

4. 結果の保存
   - 「名前を付けて保存」で新規保存
   - 「上書き保存」で既存ファイルを更新

## 注意事項

- 長時間の音声ファイルは自動的に分割して処理されます
- AI処理にはOpenAI APIの利用料金が発生します
- 音声ファイルは一時的にサーバーにアップロードされます
- 動画ファイルから音声を抽出する場合は、ffmpegが必要です

## 最近の更新

- 動画ファイルからの音声抽出機能を追加
- 音声変換処理の進捗表示を改善
- エラー処理とエラーメッセージを改善
- ファイル選択ボタンのラベルを「ファイルを選択」に変更
