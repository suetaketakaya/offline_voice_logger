# MSIインストーラ作成チェックリスト

## ✅ 完了済み

- [x] **PyInstaller EXE作成**
  - ファイル: `dist\OfflineVoiceLogger\OfflineVoiceLogger.exe` (35MB)
  - 確認日: 2025-11-12

- [x] **large-v3モデル配置**
  - フォルダ: `models\large-v3\`
  - サイズ: 2.9GB

- [x] **WiX設定ファイル作成**
  - `Product.wxs` - メインのWiX設定
  - `Product_ja-JP.wxl` - 日本語ローカライゼーション
  - `License.rtf` - ライセンス（RTF形式）

- [x] **MSIビルドスクリプト**
  - `build_msi.bat` - 自動ビルドスクリプト

- [x] **ドキュメント作成**
  - `BUILD_MSI_GUIDE.md` - 詳細ガイド（160行）
  - `MSI_QUICKSTART.md` - クイックスタート
  - `MSI_CHECKLIST.md` - このファイル

- [x] **Git管理**
  - コミット済み: cd79caf
  - タグ作成: v1.0.0
  - プッシュ済み: origin/main

---

## ⏳ 次に実行する作業

### 1. WiX Toolsetインストール

**所要時間**: 5分

**手順**:
```
1. https://github.com/wixtoolset/wix3/releases/latest にアクセス
2. wix314.exe をダウンロード
3. ダウンロードしたEXEを実行
4. インストールウィザードに従う（デフォルト設定でOK）
5. 完了後、コマンドプロンプトを再起動
6. candle.exe -? で確認
```

**確認方法**:
```cmd
candle.exe -?
```
→ WiXのヘルプが表示されればOK

---

### 2. MSIビルド実行

**所要時間**: 15-20分

**手順**:
```cmd
cd C:\Users\suetake\OFFLINEVOICELOGGER
build_msi.bat
```

**処理内容**:
- [1/5] WiX確認
- [2/5] ディレクトリ作成
- [3/5] Heat.exe でファイル一覧生成（1-2分）
- [4/5] Candle.exe でコンパイル（1-2分）
- [5/5] Light.exe でMSI作成（10-15分） ← ここが一番時間がかかる

**出力**:
```
msi_output\OfflineVoiceLogger_v1.0.0.msi (約3.2GB)
```

---

### 3. MSIテスト

**所要時間**: 10分

**インストールテスト**:
```cmd
msi_output\OfflineVoiceLogger_v1.0.0.msi
```

**確認項目**:
- [ ] インストールウィザードが日本語表示される
- [ ] ライセンス画面が表示される
- [ ] インストール先を選択できる
- [ ] デスクトップショートカットが作成される
- [ ] スタートメニューに登録される
- [ ] アプリが起動する
- [ ] large-v3モデルがロードされる
- [ ] 文字起こしが動作する

**アンインストールテスト**:
- [ ] 設定 → アプリ → OfflineVoiceLogger → アンインストール
- [ ] ファイルが削除される
- [ ] ショートカットが削除される

---

### 4. チェックサム生成

**所要時間**: 1分

```cmd
certutil -hashfile msi_output\OfflineVoiceLogger_v1.0.0.msi SHA256
```

**出力されたSHA256ハッシュをメモ帳にコピー**

---

### 5. GitHub Releaseにアップロード

**所要時間**: 10分（アップロード含む）

**手順**:
1. https://github.com/suetaketakaya/offline_voice_logger/releases にアクセス
2. v1.0.0 タグの "Edit release" をクリック（既にタグは作成済み）
3. Title: `OfflineVoiceLogger v1.0.0`
4. Description: `MSI_QUICKSTART.md` の GitHub Release セクションをコピー
5. SHA256ハッシュを記載
6. MSIファイルをドラッグ&ドロップでアップロード
7. "Publish release" をクリック

---

## 🎯 完了後の確認

### GitHub Releasesでの確認
- [ ] Release が公開されている
- [ ] MSIファイルがダウンロード可能
- [ ] SHA256ハッシュが正確に記載されている
- [ ] 説明文が適切に表示されている

### ダウンロードテスト
- [ ] GitHub Releasesからダウンロード
- [ ] SHA256ハッシュを確認
- [ ] ダウンロードしたMSIでインストールテスト

---

## 📊 進捗状況

```
準備フェーズ:  ████████████████████ 100% 完了
ビルドフェーズ: ░░░░░░░░░░░░░░░░░░░░   0% (WiXインストール待ち)
テストフェーズ: ░░░░░░░░░░░░░░░░░░░░   0%
配布フェーズ:   ░░░░░░░░░░░░░░░░░░░░   0%
```

**次のアクション**: WiX Toolset v3.14 をインストール

---

## 🚨 注意事項

### 重要なポイント
1. **MSIビルドは時間がかかります**（15-20分）
   - Light.exeでのMSI作成が特に時間がかかる（10-15分）
   - large-v3モデル（2.9GB）の圧縮処理が原因
   - **正常な動作です。中断しないでください**

2. **ファイルサイズが大きい**
   - MSI: 約3.2GB
   - GitHub Releasesへのアップロードに時間がかかる
   - 安定したインターネット接続が必要

3. **Windows SmartScreen警告**
   - コード署名がないため警告が出る可能性あり
   - ユーザーは「詳細情報」→「実行」で続行可能

---

## 📞 問題が発生した場合

### 参照ドキュメント
1. `BUILD_MSI_GUIDE.md` - 詳細なトラブルシューティング
2. `MSI_QUICKSTART.md` - クイックリファレンス

### エラーの種類別対応
- **WiXエラー**: BUILD_MSI_GUIDE.md のトラブルシューティングセクション参照
- **ビルドエラー**: ログを確認（build_msi.batの出力）
- **インストールエラー**: MSIログを確認（%TEMP%フォルダ）

---

## ✨ オプション作業（後日対応可）

### コード署名（推奨）
- [ ] コード署名証明書を購入（年間3-5万円）
- [ ] signtoolでMSIに署名
- [ ] SmartScreen警告を回避

### Firebase Hosting
- [ ] Firebaseでダウンロードページ作成
- [ ] プロジェクト情報:
  - Project name: offlinevoicelogger
  - Project ID: offlinevoicelogger
  - Project number: 865653494967

### 追加ドキュメント
- [ ] ユーザーマニュアル作成
- [ ] システム管理者向けガイド
- [ ] FAQ作成

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

最終更新: 2025-11-12
