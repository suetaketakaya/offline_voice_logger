# faster-whisperモデルのダウンロードガイド

## 📥 自動ダウンロード (推奨)

### 方法1: ダウンロードスクリプトを使用

最も簡単な方法です:

```bash
# 仮想環境をアクティベート
venv\Scripts\activate

# faster-whisperがインストールされていることを確認
pip install faster-whisper

# ダウンロードスクリプトを実行
python download_model.py
```

**実行すると**:
1. 既存のモデルがあるかチェック
2. なければHugging Faceから自動ダウンロード
3. `models/large-v3/` に保存

**所要時間**: 10-30分 (インターネット速度による)
**必要な容量**: 約3GB

---

## 📋 手動ダウンロード

自動ダウンロードが失敗する場合の代替方法:

### ステップ1: Pythonで直接ダウンロード

```python
from faster_whisper import WhisperModel

# モデルのダウンロードとロード
model = WhisperModel(
    "large-v3",
    device="cpu",
    compute_type="int8",
    download_root="./models"
)

print("ダウンロード完了!")
```

このコードを `test_download.py` として保存して実行:

```bash
python test_download.py
```

### ステップ2: Hugging Faceから手動ダウンロード

1. **Hugging Faceにアクセス**
   - URL: https://huggingface.co/Systran/faster-whisper-large-v3

2. **Files and versions タブをクリック**

3. **以下のファイルをダウンロード**:
   - `config.json`
   - `model.bin`
   - `tokenizer.json`
   - `vocabulary.*` (すべて)
   - その他すべてのファイル

4. **ファイルを配置**:
   ```
   OFFLINEVOICELOGGER/
   └── models/
       └── large-v3/
           ├── config.json
           ├── model.bin
           ├── tokenizer.json
           └── ... (その他のファイル)
   ```

---

## ✅ ダウンロード確認

### 方法1: ファイル確認

```bash
# Windowsの場合
dir models\large-v3

# 期待される出力: 複数のファイルが表示される
# - config.json
# - model.bin
# - tokenizer.json
# - など
```

### 方法2: Pythonで確認

```python
from pathlib import Path

model_dir = Path("models/large-v3")
if model_dir.exists():
    files = list(model_dir.glob("*"))
    print(f"ファイル数: {len(files)}")

    # サイズ確認
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    print(f"合計サイズ: {total_size / (1024**3):.2f} GB")

    if len(files) > 0:
        print("✓ モデルが正しく配置されています")
    else:
        print("✗ ファイルがありません")
else:
    print("✗ models/large-v3/ ディレクトリが存在しません")
```

---

## 🔧 トラブルシューティング

### 問題1: "インターネット接続エラー"

**原因**: プロキシ設定やファイアウォール

**解決方法**:
```bash
# プロキシ設定がある場合
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=http://proxy.example.com:8080

# ダウンロード再試行
python download_model.py
```

### 問題2: "ディスク容量不足"

**必要な容量**: 最低5GB (モデル3GB + 作業領域2GB)

**確認方法**:
```bash
# ドライブの空き容量を確認
wmic logicaldisk get caption,freespace,size
```

### 問題3: "ダウンロードが途中で止まる"

**解決方法**:
1. インターネット接続を確認
2. 一度削除して再ダウンロード:
   ```bash
   # models/large-v3/ を削除
   rmdir /s models\large-v3

   # 再ダウンロード
   python download_model.py
   ```

### 問題4: "Permission denied エラー"

**解決方法**:
1. 管理者権限でコマンドプロンプトを開く
2. または、別の場所にダウンロード:
   ```python
   # 例: Documentsフォルダにダウンロード
   model = WhisperModel(
       "large-v3",
       device="cpu",
       download_root="C:/Users/YourName/Documents/whisper_models"
   )
   ```

---

## 🎯 小さいモデルから試す

large-v3が大きすぎる場合、まず小さいモデルで試すことをお勧めします:

| モデル | サイズ | 精度 | 推奨用途 |
|-------|--------|------|---------|
| tiny | 75MB | ★★☆☆☆ | テスト用 |
| base | 145MB | ★★★☆☆ | 軽量環境 |
| small | 466MB | ★★★☆☆ | バランス |
| medium | 1.5GB | ★★★★☆ | 高精度 |
| large-v3 | 3GB | ★★★★★ | 最高精度 |

### mediumモデルをダウンロード:

```python
from faster_whisper import WhisperModel

model = WhisperModel(
    "medium",  # ← large-v3 の代わりに medium
    device="cpu",
    compute_type="int8",
    download_root="./models"
)
```

または `download_model.py` を編集:
```python
# 以下の行を変更
model = WhisperModel(
    "medium",  # ← ここを変更
    device="cpu",
    compute_type="int8",
    download_root=str(models_dir)
)
```

---

## 📝 ダウンロード完了後

モデルのダウンロードが完了したら:

```bash
# アプリケーションを起動
cd src
python main.py
```

初回起動時にモデルがロードされます（10-30秒）。

---

## 💡 ヒント

### オフライン環境でのセットアップ

1. **インターネット接続がある環境でダウンロード**
   ```bash
   python download_model.py
   ```

2. **models/ディレクトリをコピー**
   ```bash
   # USBメモリなどにコピー
   xcopy /E /I models E:\OfflineVoiceLogger\models
   ```

3. **オフライン環境に配置**
   ```
   オフラインPC/
   └── OFFLINEVOICELOGGER/
       └── models/
           └── large-v3/
               └── ... (ダウンロードしたファイル)
   ```

### ダウンロード先の変更

デフォルトでは `models/large-v3/` にダウンロードされますが、変更可能です:

**config.ini を編集**:
```ini
[Transcription]
model = C:\path\to\your\models\large-v3
```

または **環境変数を設定**:
```bash
set WHISPER_MODEL_PATH=C:\path\to\your\models
```

---

## 🆘 サポート

問題が解決しない場合は:

1. **ログを確認**: `download_model.py` の実行ログ
2. **faster-whisperのバージョン確認**: `pip show faster-whisper`
3. **再インストール**:
   ```bash
   pip uninstall faster-whisper
   pip install faster-whisper
   ```

---

**推奨**: まずは `python download_model.py` で自動ダウンロードを試してください!
