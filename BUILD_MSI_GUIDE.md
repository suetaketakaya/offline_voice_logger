# MSIインストーラ作成ガイド - OfflineVoiceLogger

このガイドでは、Windows Installer（MSI）形式で正式なインストーラを作成する手順を説明します。

## 📋 MSIインストーラの利点

### 企業/正式配布向け
- **Windows標準**: Windows Installerを使用した公式形式
- **グループポリシー対応**: Active Directory経由での一括配布が可能
- **ロールバック機能**: インストール失敗時の自動復元
- **修復機能**: プログラムと機能から修復実行可能
- **詳細なログ**: トラブルシューティングが容易

### ユーザー視点
- **信頼性**: Windows公式形式で安心
- **管理容易**: コントロールパネルから確認・削除可能
- **アップグレード対応**: 新バージョンへの更新が容易

---

## 🛠️ ステップ1: WiX Toolsetのインストール

### 1-1. ダウンロード

**WiX Toolset v3.14** (最新安定版) をダウンロード:
- URL: https://github.com/wixtoolset/wix3/releases
- ファイル: `wix314.exe` または `wix314-binaries.zip`

### 1-2. インストール

1. ダウンロードしたEXEファイルを実行
2. インストールウィザードに従う
3. デフォルトパス推奨: `C:\Program Files (x86)\WiX Toolset v3.14`
4. 環境変数PATHに自動追加される

### 1-3. インストール確認

コマンドプロンプトで確認:
```cmd
candle.exe -?
```

正常にインストールされている場合、WiXのヘルプが表示されます。

---

## 🏗️ ステップ2: MSIのビルド

### 2-1. 前提条件の確認

以下のファイルが存在することを確認:
```
C:\Users\suetake\OFFLINEVOICELOGGER\
├── dist\OfflineVoiceLogger\          # PyInstallerでビルド済みEXE
│   └── OfflineVoiceLogger.exe
├── models\large-v3\                  # Whisperモデル（2.9GB）
├── Product.wxs                       # WiX設定ファイル（作成済み）
├── License.rtf                       # ライセンス（RTF形式）
├── app_icon.ico                      # アプリアイコン
└── build_msi.bat                     # MSIビルドスクリプト
```

### 2-2. MSIのビルド実行

```cmd
cd C:\Users\suetake\OFFLINEVOICELOGGER
build_msi.bat
```

### 2-3. ビルド工程（自動実行）

1. **Heat.exe**: ファイル一覧を自動生成
   - `dist/OfflineVoiceLogger/` 配下の全ファイル
   - `models/large-v3/` 配下の全モデルファイル

2. **Candle.exe**: WiXソースをコンパイル
   - Product.wxs → Product.wixobj
   - DistFiles.wxs → DistFiles.wixobj
   - ModelFiles.wxs → ModelFiles.wixobj

3. **Light.exe**: MSIファイルを作成
   - 約10-15分かかります（モデルファイル同梱のため）
   - 圧縮処理に時間がかかります

### 2-4. 出力ファイル

```
msi_output\OfflineVoiceLogger_v1.0.0.msi  (約3.2GB)
```

---

## ✅ ステップ3: MSIのテスト

### 3-1. インストールテスト

1. **管理者権限で実行**:
   ```cmd
   msi_output\OfflineVoiceLogger_v1.0.0.msi
   ```

2. **インストールウィザード確認**:
   - 日本語表示されるか
   - ライセンス画面が表示されるか
   - インストール先を変更できるか
   - デスクトップアイコン作成オプションがあるか

3. **インストール後の確認**:
   - デスクトップショートカットが作成されているか
   - スタートメニューに登録されているか
   - アプリケーションが正常に起動するか
   - モデルがロードされるか
   - 文字起こしが動作するか

### 3-2. アンインストールテスト

1. **コントロールパネルから**:
   - 設定 → アプリ → インストールされているアプリ
   - "OfflineVoiceLogger" を選択
   - アンインストール実行

2. **確認項目**:
   - アプリケーションフォルダが削除されているか
   - デスクトップショートカットが削除されているか
   - スタートメニューから削除されているか

### 3-3. 修復テスト

1. **ファイルを手動で削除**:
   ```
   C:\Program Files\OfflineVoiceLogger\OfflineVoiceLogger.exe
   ```

2. **修復実行**:
   - 設定 → アプリ → OfflineVoiceLogger
   - 詳細オプション → 修復

3. **確認**:
   - 削除したファイルが復元されるか

---

## 📦 ステップ4: 配布準備

### 4-1. MSIファイルの署名（推奨）

コード署名証明書がある場合:

```cmd
signtool sign /f "certificate.pfx" /p "password" /t http://timestamp.digicert.com msi_output\OfflineVoiceLogger_v1.0.0.msi
```

**利点**:
- Windows SmartScreenの警告が出にくくなる
- ユーザーの信頼度が向上
- 企業配布に必須

### 4-2. チェックサム生成

```cmd
certutil -hashfile msi_output\OfflineVoiceLogger_v1.0.0.msi SHA256
```

出力されたSHA256ハッシュをREADMEに記載します。

### 4-3. インストールサイズ計算

```cmd
dir msi_output\OfflineVoiceLogger_v1.0.0.msi
```

---

## 🚀 ステップ5: GitHub Releasesへの公開

### 5-1. Releaseの作成

1. GitHubリポジトリにアクセス:
   https://github.com/suetaketakaya/offline_voice_logger/releases

2. **Draft a new release** をクリック

3. **Release情報を入力**:
   - **Tag**: `v1.0.0`
   - **Title**: `OfflineVoiceLogger v1.0.0`
   - **Description**:
     ```markdown
     # OfflineVoiceLogger v1.0.0

     完全オフラインで動作する音声文字起こしアプリケーション

     ## ダウンロード

     ### MSIインストーラ（推奨）
     **OfflineVoiceLogger_v1.0.0.msi** (約3.2GB)
     - Windows Installer形式
     - large-v3モデル同梱
     - 企業配布対応
     - 修復・ロールバック機能付き

     **SHA256**: `[チェックサムをここに記載]`

     ### インストール手順
     1. MSIファイルをダウンロード
     2. ダブルクリックして実行
     3. インストールウィザードに従う
     4. デスクトップアイコンから起動

     ## システム要件
     - OS: Windows 10/11 (64bit)
     - メモリ: 8GB以上推奨
     - ディスク: 5GB以上の空き容量
     ```

4. **MSIファイルをアップロード**:
   - `msi_output\OfflineVoiceLogger_v1.0.0.msi` をドラッグ&ドロップ

5. **Publish release** をクリック

### 5-2. ダウンロードページのカスタマイズ

READMEにインストール手順を追加:

```markdown
## インストール

### MSIインストーラ（推奨）

1. [最新リリース](https://github.com/suetaketakaya/offline_voice_logger/releases/latest)から`OfflineVoiceLogger_v1.0.0.msi`をダウンロード

2. ダウンロードしたMSIファイルをダブルクリック

3. インストールウィザードに従う

4. デスクトップアイコンから起動
```

---

## 🔧 トラブルシューティング

### エラー1: Heat.exeが失敗する

**原因**: distフォルダが存在しない

**解決策**:
```cmd
build.bat
```
を実行してEXEを先にビルド

### エラー2: Light.exeでエラー

**症状**: "LGHT0204: ICE03: Invalid template string"

**解決策**: Product.wxsのPackage要素でPlatform="x64"を確認

### エラー3: MSIが大きすぎる

**説明**: large-v3モデル（2.9GB）を含めるため3.2GBになります

**代替案**:
- Product.wxsからModelFilesコンポーネントグループを削除
- 初回起動時の自動ダウンロードに変更

### エラー4: インストールに時間がかかる

**説明**: 3.2GBのMSIを展開するため、5-10分かかります

**対策**: ユーザーに事前に案内

---

## 📊 MSI vs EXE比較

| 項目 | MSI (WiX) | EXE (Inno Setup) |
|------|-----------|------------------|
| **形式** | Windows Installer | 独自形式 |
| **企業配布** | ◎ GP対応 | △ 限定的 |
| **修復機能** | ◎ 標準対応 | × なし |
| **ロールバック** | ◎ 自動 | △ 限定的 |
| **カスタマイズ** | △ 難しい | ◎ 容易 |
| **作成難易度** | ★★★★☆ | ★★☆☆☆ |
| **ファイルサイズ** | 3.2GB | 3.5GB |

## 🎯 推奨配布戦略

### 一般ユーザー向け
- **MSIインストーラ** を推奨
- GitHubで配布
- Firebaseでダウンロードページ作成

### 企業向け
- **MSI + コード署名**
- グループポリシーでの配布手順を提供
- システム管理者向けドキュメント作成

### 開発者向け
- **ソースコード** + ビルド手順
- GitHubリポジトリで公開
- コントリビューションガイド作成

---

## 📚 参考リンク

- **WiX Toolset公式**: https://wixtoolset.org/
- **WiX Tutorial**: https://www.firegiant.com/wix/tutorial/
- **Windows Installer**: https://docs.microsoft.com/en-us/windows/win32/msi/windows-installer-portal

---

## 次のステップ

MSIインストーラ作成後:

1. ✅ ローカルでテストインストール
2. ✅ アンインストール・修復機能のテスト
3. ✅ GitHub Releasesで公開
4. ⬜ Firebaseでダウンロードページ作成
5. ⬜ READMEにインストール手順追加
6. ⬜ ユーザーフィードバック収集

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

© 2025 OfflineVoiceLogger Project
