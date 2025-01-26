# mocoVoice-Desktop

音声ファイルの文字起こしと分析を行うデスクトップアプリケーション

## 機能

- 音声ファイルの文字起こし
- 話者の識別
- 会話の分析
  - 発話量の時間変化
  - 話者ごとの総発話量
  - 発話の遷移パターン
- 話者の管理
  - 話者IDの変更
  - 話者の統合
  - 一括変換機能
- AI処理による会話の分析

## インストール

1. リポジトリをクローン
```bash
git clone https://github.com/kokonerumia/mocoVoice-Desktop.git
```

2. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

3. 設定ファイルを作成
```bash
cp config.json.example config.json
```

4. config.jsonを編集して必要な設定を行う

## 使用方法

1. アプリケーションを起動
```bash
python main.py
```

2. 音声ファイルを選択して文字起こしを実行

3. 必要に応じて話者の管理や会話の分析を行う

## ライセンス

MIT License
