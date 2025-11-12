# Inno Setupインストーラ作成手順

## 1. Inno Setupのインストール

1. 下記URLからダウンロード:
   https://jrsoftware.org/isdl.php

2. `innosetup-6.x.x.exe` を実行してインストール

3. デフォルト設定でインストール（推奨）

## 2. インストーラのコンパイル

1. Inno Setupを起動

2. **File → Open** で `installer_script.iss` を開く

3. **Build → Compile** をクリック
   - または `F9` キーを押す

4. コンパイル開始（約10-15分かかります）
   - large-v3モデル（2.9GB）を含めるため時間がかかります

5. 完了すると以下が生成されます:
   ```
   installer_output/OfflineVoiceLogger_Setup_v1.0.0.exe (約3.5GB)
   ```

## 3. インストーラのテスト

1. `OfflineVoiceLogger_Setup_v1.0.0.exe` を実行

2. インストール手順に従う

3. インストール完了後、アプリケーションを起動して動作確認:
   - モデルが正常にロードされるか
   - 音声デバイスが認識されるか
   - 文字起こしが動作するか

## 4. GitHub Releasesへのアップロード

### 方法1: GitHub Web UIを使用

1. https://github.com/suetaketakaya/offline_voice_logger/releases にアクセス

2. **Draft a new release** をクリック

3. **Choose a tag** で `v1.0.0` を選択

4. Release title: `OfflineVoiceLogger v1.0.0`

5. Description に以下を記載:
   ```markdown
   # OfflineVoiceLogger v1.0.0

   完全オフラインで動作する音声文字起こしアプリケーション

   ## 主な機能
   - faster-whisper (large-v3モデル) による高精度な日本語・英語認識
   - リアルタイム文字起こし
   - マイク & システムオーディオ対応
   - 完全オフライン動作

   ## ダウンロード
   - **OfflineVoiceLogger_Setup_v1.0.0.exe** (約3.5GB)
     - large-v3モデル同梱
     - インストーラ付き

   ## システム要件
   - OS: Windows 10/11 (64bit)
   - メモリ: 8GB以上推奨
   - ディスク: 5GB以上の空き容量

   ## インストール
   1. ダウンロードしたEXEファイルを実行
   2. インストールウィザードに従う
   3. デスクトップアイコンから起動
   ```

6. **Attach binaries** で `OfflineVoiceLogger_Setup_v1.0.0.exe` をアップロード

7. **Publish release** をクリック

### 方法2: GitHub CLIを使用

```bash
# GitHub CLIがインストールされている場合
gh release create v1.0.0 \
  installer_output/OfflineVoiceLogger_Setup_v1.0.0.exe \
  --title "OfflineVoiceLogger v1.0.0" \
  --notes-file RELEASE_NOTES.md
```

## トラブルシューティング

### コンパイルエラー: モデルファイルが見つからない

**原因:** `models/large-v3/` が存在しない

**解決策:**
```bash
python download_model.py
```
を実行してモデルをダウンロード

### コンパイルエラー: dist/OfflineVoiceLoggerが見つからない

**原因:** EXEファイルがビルドされていない

**解決策:**
```bash
build.bat
```
を実行してEXEをビルド

### インストーラサイズが大きすぎる

**説明:** large-v3モデルが2.9GBあるため、インストーラが3.5GBになります

**代替案:**
- `installer_script.iss` の line 57-58 をコメントアウトしてモデルを含めない
- ユーザーに初回起動時の自動ダウンロードを案内

## 次のステップ

インストーラ作成後:
1. GitHub Releasesで配布
2. Firebase Hostingでダウンロードページ作成
3. READMEにインストール手順を記載
