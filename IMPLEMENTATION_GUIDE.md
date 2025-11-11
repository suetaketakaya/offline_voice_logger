# OfflineVoiceLogger - 実装ガイド

## Phase 1 (MVP) 実装完了

Phase 1の主要機能の実装が完了しました!

### 実装済みモジュール

#### 1. logger.py - ロギングモジュール
- ローカルファイルへのログ出力
- ログローテーション (10MB × 5ファイル)
- レベル別ロギング (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 完全ローカル動作 (外部送信なし)

#### 2. config_manager.py - 設定管理モジュール
- config.iniファイルの読み書き
- デフォルト設定の管理
- 設定の検証
- %APPDATA%への永続化

#### 3. audio_capture.py - 音声キャプチャモジュール
- WASAPIループバックデバイスからの音声取得
- リアルタイムバッファリング
- デバイス自動検出
- 音声レベル監視

#### 4. transcriber.py - 文字起こしモジュール
- faster-whisper (large-v3) による文字起こし
- 日本語/英語対応
- VADフィルター適用
- 完全オフライン動作 (ローカルモデルのみ使用)

#### 5. file_manager.py - ファイル管理モジュール
- TXT/SRT/JSON形式でのエクスポート
- 自動保存機能
- バックアップ管理

#### 6. gui.py - GUIモジュール (PyQt5)
- メインウィンドウ
- デバイス選択
- 言語選択
- 録音開始/停止ボタン
- リアルタイム文字起こし表示
- 音声レベルメーター

#### 7. main.py - メインアプリケーション
- すべてのモジュールの統合
- マルチスレッド処理 (音声キャプチャ/文字起こし)
- イベント駆動アーキテクチャ
- GUI連携

## 次のステップ

### 1. 動作テスト

#### 準備
```bash
# 仮想環境の作成とアクティベート
python -m venv venv
venv\Scripts\activate

# 依存ライブラリのインストール
pip install -r requirements.txt
```

#### faster-whisperモデルの配置
1. faster-whisperの`large-v3`モデルをダウンロード
2. `models/large-v3/`ディレクトリに配置
   ```
   OFFLINEVOICELOGGER/
   ├── models/
   │   └── large-v3/
   │       ├── model.bin
   │       ├── config.json
   │       └── ... (その他のモデルファイル)
   ```

#### 実行
```bash
cd src
python main.py
```

### 2. 動作確認項目

- [ ] アプリケーションが起動する
- [ ] デバイスリストが表示される
- [ ] ループバックデバイスが検出される
- [ ] faster-whisperモデルがロードされる
- [ ] 録音開始/停止が動作する
- [ ] 音声レベルメーターが動作する
- [ ] 文字起こし結果がリアルタイムで表示される
- [ ] ファイル保存が動作する
- [ ] 日本語/英語の切り替えが動作する

### 3. トラブルシューティング

#### エラー: "faster-whisperのインポートに失敗"
```bash
pip install faster-whisper
```

#### エラー: "モデルファイルが見つかりません"
- `models/large-v3/`にモデルファイルを配置してください
- モデルのダウンロード:
  ```bash
  # Hugging Faceからダウンロード
  # https://huggingface.co/guillaumekln/faster-whisper-large-v3
  ```

#### エラー: "音声デバイスが見つかりません"
- Windowsの設定でステレオミキサーを有効にしてください
- サウンド設定 → 録音デバイス → ステレオミキサー → 有効化

#### エラー: "sounddevice"関連
```bash
pip install sounddevice
```

### 4. EXE化の準備

次の段階では、PyInstallerを使用してEXE化します:

#### PyInstallerスペックファイルの作成
```python
# OfflineVoiceLogger.spec
# (詳細は次回実装)
```

#### ビルドコマンド
```bash
pyinstaller OfflineVoiceLogger.spec
```

## Phase 2以降の予定

Phase 1 (MVP)の動作確認が完了したら、以下のフェーズに進みます:

### Phase 2: 機能拡張とMSI化 (予定)
- SRT/JSON形式のエクスポート (既に実装済み)
- 音声レベルメーターの改善
- プログレスバー
- メニューバー
- MSIインストーラー作成
- 初回セットアップウィザード

### Phase 3: 品質向上とセキュリティ強化 (予定)
- 包括的なエラーハンドリング
- ログ機能の強化
- 自動保存の実装
- バックアップ・復旧機能
- ヘルプ機能
- セキュリティ監査

### Phase 4: 高度な機能 (オプション)
- ダークモード
- 検索機能
- フォントサイズ変更
- パフォーマンスモニター

## ファイル構成

```
OFFLINEVOICELOGGER/
├── src/
│   ├── main.py              # メインエントリポイント
│   ├── logger.py            # ロギングモジュール
│   ├── config_manager.py    # 設定管理
│   ├── audio_capture.py     # 音声キャプチャ
│   ├── transcriber.py       # 文字起こし
│   ├── file_manager.py      # ファイル管理
│   └── gui.py               # GUI
├── models/
│   └── large-v3/            # faster-whisperモデル (要配置)
├── logs/                    # ログファイル (自動生成)
├── requirements.txt         # 依存ライブラリ
├── README.md
├── .gitignore
└── IMPLEMENTATION_GUIDE.md  # このファイル
```

## 設定ファイル

初回起動時に以下の場所に設定ファイルが作成されます:

```
%APPDATA%\OfflineVoiceLogger\
├── config.ini              # 設定ファイル
└── logs\
    └── app.log             # アプリケーションログ
```

## サポート

問題が発生した場合は、以下を確認してください:

1. ログファイル: `%APPDATA%\OfflineVoiceLogger\logs\app.log`
2. Python バージョン: 3.9以上
3. 依存ライブラリ: `requirements.txt`に記載のバージョン
4. モデルファイル: `models/large-v3/`に正しく配置されているか

---

**実装完了日**: 2025-11-09
**Phase 1 (MVP)**: 完了
**次のステップ**: 動作テストとEXE化
