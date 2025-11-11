# OfflineVoiceLogger 配布ガイド

このガイドでは、OfflineVoiceLoggerをWindowsアプリケーションとして配布する手順を説明します。

## 準備したファイル

### 1. アプリケーションアイコン
- `app_icon.ico` - 複数サイズを含むアイコンファイル
- `app_icon.png` - プレビュー用PNG

### 2. PyInstallerの設定
- `OfflineVoiceLogger.spec` - EXE作成設定
- `version_info.txt` - バージョン情報
- `build.bat` - ビルド実行スクリプト

### 3. Inno Setupの設定
- `installer_script.iss` - インストーラ作成スクリプト

### 4. ドキュメント
- `README.md` - ユーザーガイド
- `LICENSE.txt` - ライセンス
- `AUDIO_SETUP.md` - オーディオ設定ガイド

## ビルド手順

### ステップ1: EXE作成

```batch
build.bat
```

または手動で：

```batch
pyinstaller OfflineVoiceLogger.spec
```

出力: `dist\OfflineVoiceLogger\OfflineVoiceLogger.exe`

### ステップ2: インストーラ作成

1. **Inno Setupをインストール**
   - https://jrsoftware.org/isdl.php からダウンロード
   - インストールウィザードに従ってインストール

2. **インストーラのカスタマイズ**
   - `installer_script.iss` を開く
   - `AppId={{YOUR-GUID-HERE}}` を固有のGUIDに変更
     (GUIDは https://www.guidgen.com/ で生成可能)

3. **コンパイル**
   - Inno Setupで `installer_script.iss` を開く
   - Build → Compile を実行
   - または右クリック → Compile

出力: `installer_output\OfflineVoiceLogger_Setup_v1.0.0.exe`

## 配布前のチェックリスト

- [ ] EXEが正常に起動するか確認
- [ ] モデルダウンロードが機能するか確認
- [ ] インストーラが正常に動作するか確認
- [ ] アンインストールが正常に動作するか確認
- [ ] デスクトップアイコンが正しく表示されるか確認
- [ ] README.mdとLICENSE.txtが含まれているか確認

## 配布サイズの最適化

### モデルファイルを含めない場合（推奨）

インストーラにモデルファイルを含めず、初回起動時に自動ダウンロードする方式：

**利点**:
- インストーラサイズが小さい（約300MB）
- ユーザーが必要なモデルのみダウンロード可能

**欠点**:
- 初回起動時にダウンロード時間が必要

### モデルファイルを含める場合

base モデルを含める場合のインストーラサイズ: 約600MB
large-v3 モデルを含める場合のインストーラサイズ: 約3.2GB

## トラブルシューティング

### ビルドエラー: モジュールが見つからない

```batch
pip install pyinstaller pillow
```

### Inno Setupでコンパイルエラー

- `LICENSE.txt` と `README.md` がルートディレクトリに存在することを確認
- パスが正しいか確認

### EXEが起動しない

- Windowsファイアウォールやウイルス対策ソフトでブロックされていないか確認
- `build\OfflineVoiceLogger\warn-OfflineVoiceLogger.txt` でエラーを確認

## 配布方法

### GitHub Releases

1. GitHubリポジトリを作成
2. Releasesページから新しいリリースを作成
3. インストーラ (`OfflineVoiceLogger_Setup_v1.0.0.exe`) をアップロード
4. リリースノートに以下を記載:
   - 新機能
   - バグ修正
   - システム要件
   - ダウンロードリンク

### その他の配布方法

- 自社Webサイトでホスティング
- Microsoft Storeでの公開（要審査）
- クラウドストレージ（Google Drive, Dropbox等）での共有

## セキュリティ

### コード署名（推奨）

配布前にEXEファイルにデジタル署名を追加することを推奨します：

1. コード署名証明書を取得
2. SignToolでEXEに署名
3. ユーザーがダウンロード時に警告が表示されにくくなります

### チェックサムの提供

SHA256チェックサムをREADMEに記載：

```batch
certutil -hashfile OfflineVoiceLogger_Setup_v1.0.0.exe SHA256
```

## サポート

配布後のサポート:
- GitHub Issues でバグレポートを受付
- ドキュメントを定期的に更新
- FAQを作成

---

Copyright (C) 2025 OfflineVoiceLogger Project
