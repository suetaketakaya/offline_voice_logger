# OfflineVoiceLogger v1.0.0

完全オフラインで動作する音声文字起こしアプリケーション

## 🎉 主な機能

### 高精度文字起こし
- **faster-whisper (large-v3モデル)** による最高精度の日本語・英語認識
- リアルタイム文字起こし
- 自動的な文章セグメント結合で自然な区切り

### 音声入力対応
- **マイク入力**: 会議、プレゼン、講義などの録音
- **システムオーディオ**: PC画面の音声を文字起こし
  - ブラウザ動画（YouTube等）
  - オンライン会議（Teams、Zoom等）
  - 画面録画音声

### 使いやすいUI
- シンプルで直感的なGUI
- リアルタイム音声レベル表示
- モデルロード中のローディング表示
- 文字起こし履歴のリセット機能

### 完全オフライン動作
- インターネット接続不要
- プライバシー保護（音声データは外部送信されません）
- 会議室等のオフライン環境でも使用可能

## 📥 ダウンロード

### インストーラ版（推奨）
**OfflineVoiceLogger_Setup_v1.0.0.exe** (約3.5GB)
- large-v3モデル同梱
- ワンクリックインストール
- すぐに高精度文字起こしを開始可能

### ポータブル版
**OfflineVoiceLogger_v1.0.0_Portable.zip** (約4.7GB)
- インストール不要
- USBメモリ等で持ち運び可能
- 展開して実行するだけ

## 💻 システム要件

- **OS**: Windows 10/11 (64bit)
- **メモリ**: 8GB以上推奨
- **ディスク**: 5GB以上の空き容量
- **CPU**: Intel Core i5以上推奨

## 🚀 インストール手順

### インストーラ版
1. `OfflineVoiceLogger_Setup_v1.0.0.exe` をダウンロード
2. ダウンロードしたファイルを実行
3. インストールウィザードに従う
4. デスクトップアイコンから起動

### ポータブル版
1. `OfflineVoiceLogger_v1.0.0_Portable.zip` をダウンロード
2. 任意のフォルダに展開
3. `OfflineVoiceLogger.exe` を実行

## 📖 使い方

1. アプリケーションを起動
2. **音声デバイス** を選択:
   - マイク: マイクからの音声を録音
   - スクリーンキャプチャー: PC画面の音声を録音
3. **言語** を選択（日本語/English）
4. **🎙️ 録音開始** ボタンをクリック
5. 文字起こし結果がリアルタイムで表示されます
6. **⏹️ 停止** で録音を終了
7. **💾 保存** で結果をテキストファイルに保存

### スクリーンキャプチャーの設定
- Windows 11の場合: 設定 → システム → サウンド → 詳細設定
- 詳細は `AUDIO_SETUP.md` を参照

## 🆕 v1.0.0 新機能

### UI改善
- リセットボタン追加: 文字起こし履歴を一括クリア
- ローディング表示: モデルロード中・録音準備中に表示
- モデル名表示: 現在使用中のモデルをステータスに表示

### 文字起こし精度向上
- セグメント結合ロジック改善: 自然な文の区切りを実現
- beam_size: 5 → 10 に増加
- best_of: 5 候補から最良の結果を選択
- 不要なプロンプトテキストの出力を削除

### 配布・インストール
- Windows用インストーラ
- アプリケーションアイコン
- large-v3モデル同梱（高精度）

## 📄 ライセンス

MIT License - 商用利用可能

## 🔗 リンク

- **GitHub**: https://github.com/suetaketakaya/offline_voice_logger
- **ドキュメント**: [README.md](https://github.com/suetaketakaya/offline_voice_logger/blob/main/README.md)
- **オーディオ設定ガイド**: [AUDIO_SETUP.md](https://github.com/suetaketakaya/offline_voice_logger/blob/main/AUDIO_SETUP.md)
- **配布ガイド**: [DISTRIBUTION_GUIDE.md](https://github.com/suetaketakaya/offline_voice_logger/blob/main/DISTRIBUTION_GUIDE.md)

## 📞 サポート

問題が発生した場合:
- **Issue**: https://github.com/suetaketakaya/offline_voice_logger/issues
- **ドキュメント**: プロジェクトのREADMEを参照

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

© 2025 OfflineVoiceLogger Project
