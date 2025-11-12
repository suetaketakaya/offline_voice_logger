# MSIインストーラ作成 - クイックスタートガイド

## 📦 現在の準備状況

### ✅ 完了項目
- [x] PyInstallerでEXEビルド完了 (35MB)
- [x] large-v3モデル配置完了 (2.9GB)
- [x] WiX設定ファイル作成 (`Product.wxs`)
- [x] MSIビルドスクリプト作成 (`build_msi.bat`)
- [x] 日本語ローカライゼーション (`Product_ja-JP.wxl`)
- [x] ライセンスファイル (`License.rtf`)
- [x] 詳細ガイド (`BUILD_MSI_GUIDE.md`)

### ⏳ 次に必要な作業
1. WiX Toolsetのインストール
2. MSIのビルド実行
3. MSIのテストインストール
4. GitHub Releasesへのアップロード

---

## 🚀 MSI作成手順（3ステップ）

### ステップ1: WiX Toolsetのインストール

#### 1-1. ダウンロード
```
URL: https://github.com/wixtoolset/wix3/releases/latest
ファイル: wix314.exe
```

#### 1-2. インストール
1. ダウンロードした `wix314.exe` を実行
2. インストールウィザードに従う
3. デフォルト設定で進める
4. 完了後、コマンドプロンプトを再起動

#### 1-3. 確認
```cmd
candle.exe -?
```
ヘルプが表示されればOK

---

### ステップ2: MSIビルド実行

#### 2-1. ビルドスクリプト実行
```cmd
cd C:\Users\suetake\OFFLINEVOICELOGGER
build_msi.bat
```

#### 2-2. 処理時間
- Heat.exe: 1-2分 (ファイル一覧生成)
- Candle.exe: 1-2分 (コンパイル)
- Light.exe: **10-15分** (MSI作成、large-v3モデル圧縮)

**合計: 約15-20分**

#### 2-3. 出力ファイル
```
msi_output\OfflineVoiceLogger_v1.0.0.msi (約3.2GB)
```

---

### ステップ3: MSIテスト

#### 3-1. インストールテスト
```cmd
msi_output\OfflineVoiceLogger_v1.0.0.msi
```

**確認項目**:
- [x] インストールウィザードが日本語で表示される
- [x] ライセンス画面が表示される
- [x] インストール先を選択できる
- [x] デスクトップショートカットが作成される
- [x] アプリケーションが起動する
- [x] モデルがロードされる（large-v3）
- [x] 文字起こしが動作する

#### 3-2. アンインストールテスト
1. 設定 → アプリ → OfflineVoiceLogger
2. アンインストール実行
3. ファイルが削除されていることを確認

#### 3-3. 修復テスト（オプション）
1. EXEファイルを手動で削除
2. 設定 → アプリ → OfflineVoiceLogger → 修復
3. ファイルが復元されることを確認

---

## 📤 GitHub Releasesへのアップロード

### 4-1. チェックサム生成
```cmd
certutil -hashfile msi_output\OfflineVoiceLogger_v1.0.0.msi SHA256
```

出力されたSHA256ハッシュをコピー

### 4-2. GitHub Releaseの作成

1. **GitHubリポジトリにアクセス**:
   ```
   https://github.com/suetaketakaya/offline_voice_logger/releases
   ```

2. **"Draft a new release"をクリック**

3. **Tag選択**:
   - 既存のタグ `v1.0.0` を選択

4. **Release情報を入力**:

**Title**: `OfflineVoiceLogger v1.0.0`

**Description**:
```markdown
# OfflineVoiceLogger v1.0.0

完全オフラインで動作する音声文字起こしアプリケーション

## 📥 ダウンロード

### MSIインストーラ（推奨）
**OfflineVoiceLogger_v1.0.0.msi** (約3.2GB)

- Windows Installer形式
- large-v3モデル同梱（インターネット接続不要）
- 企業配布対応（グループポリシー対応）
- 修復・ロールバック機能付き

**SHA256**: `[ここにチェックサムを貼り付け]`

## 📦 インストール手順

1. MSIファイルをダウンロード（約3.2GB）
2. ダブルクリックして実行
3. インストールウィザードに従う
4. デスクトップアイコンから起動

## 💻 システム要件

- **OS**: Windows 10/11 (64bit)
- **メモリ**: 8GB以上推奨
- **ディスク**: 5GB以上の空き容量
- **インターネット**: 不要（完全オフライン動作）

## ✨ 主な機能

- 🎤 リアルタイム音声文字起こし
- 🌐 完全オフライン動作（faster-whisper large-v3）
- 🖥️ マイク & スクリーンキャプチャー対応
- 🔄 文字起こし履歴のリセット機能
- 📊 モデルロード中のローディング表示
- 🎯 高精度な日本語・英語認識

## 📝 更新内容

- ✅ 初回リリース
- ✅ large-v3モデル同梱版
- ✅ MSIインストーラ対応

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

5. **MSIファイルをアップロード**:
   - `msi_output\OfflineVoiceLogger_v1.0.0.msi` をドラッグ&ドロップ

6. **"Publish release"をクリック**

---

## 🔧 トラブルシューティング

### エラー1: WiXが見つからない
**解決策**: コマンドプロンプトを再起動してPATHを再読み込み

### エラー2: Heat.exeが失敗
**原因**: distフォルダまたはmodelsフォルダが存在しない
**解決策**: `build.bat` を実行してEXEを再ビルド

### エラー3: Light.exeが遅い
**説明**: large-v3モデル（2.9GB）の圧縮に時間がかかります（正常）
**対策**: 10-15分待つ

### エラー4: インストール時にSmartScreen警告
**原因**: コード署名がない
**対策**:
- 一般ユーザー向け: "詳細情報" → "実行" で続行可能
- 企業配布向け: コード署名証明書を購入して署名

---

## 📚 参考ドキュメント

- **詳細ガイド**: `BUILD_MSI_GUIDE.md`
- **WiX公式**: https://wixtoolset.org/
- **GitHub Repository**: https://github.com/suetaketakaya/offline_voice_logger

---

## 📞 サポート

問題が発生した場合:
1. `BUILD_MSI_GUIDE.md` のトラブルシューティングセクションを確認
2. GitHubでIssueを作成
3. ビルドログを確認（エラーメッセージをコピー）

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

© 2025 OfflineVoiceLogger Project
