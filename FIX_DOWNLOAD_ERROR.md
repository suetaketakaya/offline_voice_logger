# ダウンロードエラーの解決方法

## 発生したエラー

```
error: unable to write file model.fp32-00001-of-00002.safetensors
fatal: unable to checkout working tree
```

## 原因

1. **間違ったモデル**: `openai/whisper-large-v3` は通常のWhisperモデル
   - このプロジェクトでは `faster-whisper` を使用します
   - 形式が異なるため動作しません

2. **ファイル書き込みエラー**: ディスク容量不足またはパス/権限の問題

---

## 解決方法

### ステップ1: 不完全なダウンロードを削除

```bash
# Windowsコマンドプロンプト
cd C:\Users\suetake\OFFLINEVOICELOGGER
rmdir /s /q whisper-large-v3
```

### ステップ2: ディスク容量を確認

```bash
# 空き容量確認
wmic logicaldisk get caption,freespace,size
```

**必要な容量**: 最低 5GB

空き容量が不足している場合:
1. 不要なファイルを削除
2. 別のドライブにプロジェクトを移動
3. より小さいモデル（medium）を使用

### ステップ3: 正しい方法でダウンロード

#### 方法A: 自動ダウンロードスクリプト（最も簡単）

```bash
# 1. faster-whisperをインストール
pip install faster-whisper

# 2. 自動ダウンロード
python download_model.py
```

**実行すると**:
- Hugging Faceから正しいfaster-whisperモデルをダウンロード
- `models/large-v3/` に自動配置
- 完了通知

#### 方法B: Pythonで直接ダウンロード

```python
# quick_download.py として保存
from faster_whisper import WhisperModel

print("faster-whisper large-v3 をダウンロード中...")
model = WhisperModel(
    "large-v3",
    device="cpu",
    compute_type="int8",
    download_root="./models"
)
print("ダウンロード完了!")
```

実行:
```bash
python quick_download.py
```

---

## より小さいモデルで試す（推奨）

large-v3（3GB）が大きすぎる場合、まずmedium（1.5GB）で試すことをお勧めします:

```bash
# download_model.py を編集
# または以下を実行
python -c "from faster_whisper import WhisperModel; WhisperModel('medium', device='cpu', compute_type='int8', download_root='./models')"
```

その後、`src/config_manager.py` でデフォルトモデルを変更:

```python
DEFAULT_CONFIG = {
    ...
    'Transcription': {
        'model': 'medium',  # ← large-v3 から medium に変更
        ...
    }
}
```

---

## モデルサイズ比較

| モデル | サイズ | メモリ | 精度 | 推奨用途 |
|--------|--------|--------|------|----------|
| tiny | 75MB | 1GB | ★★☆☆☆ | テスト用 |
| base | 145MB | 1GB | ★★★☆☆ | 軽量環境 |
| small | 466MB | 2GB | ★★★☆☆ | 省メモリ |
| **medium** | 1.5GB | 4GB | ★★★★☆ | **推奨** |
| large-v3 | 3GB | 8GB | ★★★★★ | 高精度 |

**推奨**: まず **medium** で試して、動作確認後に large-v3 にアップグレード

---

## 完了確認

ダウンロードが完了したら:

```bash
# ファイルの確認
dir models\large-v3

# または medium の場合
dir models\medium

# アプリケーションを起動
cd src
python main.py
```

---

## トラブルシューティング

### エラー: "faster-whisper がインストールされていません"

```bash
pip install faster-whisper
```

### エラー: "ディスク容量不足"

1. **別のドライブを使用**:
   ```python
   model = WhisperModel(
       "medium",
       download_root="D:/whisper_models"  # 別ドライブに指定
   )
   ```

2. **小さいモデルを使用**: medium または small

### エラー: "ネットワークエラー"

1. プロキシ設定:
   ```bash
   set HTTP_PROXY=http://proxy.example.com:8080
   set HTTPS_PROXY=http://proxy.example.com:8080
   ```

2. VPN接続を確認

3. 別の時間帯に再試行

---

## 推奨手順（まとめ）

1. **不完全なダウンロードを削除**:
   ```bash
   rmdir /s /q whisper-large-v3
   ```

2. **ディスク容量を確認** (5GB以上必要)

3. **自動ダウンロード実行**:
   ```bash
   pip install faster-whisper
   python download_model.py
   ```

4. **アプリ起動**:
   ```bash
   cd src
   python main.py
   ```

これで正しいfaster-whisperモデルがダウンロードされ、アプリケーションが動作するはずです！
