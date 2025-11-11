# OfflineVoiceLogger - ソフトウェア詳細設計書

**バージョン**: 1.0.0
**作成日**: 2025-11-09
**対象**: Windows 10/11 64bit

---

## 目次

1. [システム概要](#1-システム概要)
2. [アーキテクチャ設計](#2-アーキテクチャ設計)
3. [モジュール設計](#3-モジュール設計)
4. [データ設計](#4-データ設計)
5. [ユーザーインターフェース設計](#5-ユーザーインターフェース設計)
6. [セキュリティ設計](#6-セキュリティ設計)
7. [パフォーマンス設計](#7-パフォーマンス設計)
8. [エラーハンドリング設計](#8-エラーハンドリング設計)
9. [デプロイメント設計](#9-デプロイメント設計)

---

## 1. システム概要

### 1.1 目的
Windowsデスクトップ上の音声データをリアルタイムでキャプチャし、faster-whisperを使用して日本語/英語の文字起こしを行う完全オフライン動作のツール。社外秘情報を扱うため、インターネット接続を一切行わない。

### 1.2 主要機能
- リアルタイム音声キャプチャ（WASAPI経由）
- faster-whisper (large-v3/medium) による文字起こし
- 日本語/英語の言語選択
- 複数形式でのエクスポート（TXT/SRT/JSON）
- 完全ローカル動作（オフライン）
- MSIインストーラーでの配布

### 1.3 システム要件

#### 最小要件
- CPU: Intel Core i5 第8世代以上 / AMD Ryzen 5 3000シリーズ以上
- メモリ: 8GB RAM
- ストレージ: 5GB 空き容量
- OS: Windows 10 64bit以降

#### 推奨要件
- CPU: Intel Core i7 第10世代以上 / AMD Ryzen 7 3000シリーズ以上
- メモリ: 16GB RAM以上
- ストレージ: SSD 10GB以上
- OS: Windows 10/11 64bit

---

## 2. アーキテクチャ設計

### 2.1 システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                    ユーザーインターフェース層              │
│  (GUI: tkinter/PyQt5)                                   │
│  - メインウィンドウ                                       │
│  - 設定ダイアログ                                         │
│  - ステータス表示                                         │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│                    アプリケーション層                      │
│  - イベントハンドラ                                       │
│  - ビジネスロジック                                       │
│  - 設定管理                                               │
└────┬──────────┬──────────┬──────────┬──────────────────┘
     │          │          │          │
┌────┴───┐ ┌───┴────┐ ┌──┴─────┐ ┌──┴──────────┐
│ 音声   │ │ 文字   │ │ ファイル│ │ リソース    │
│キャプチャ│ │起こし  │ │ 管理   │ │ 監視       │
│モジュール│ │モジュール│ │モジュール│ │モジュール  │
└────┬───┘ └───┬────┘ └──┬─────┘ └──┬──────────┘
     │          │          │          │
┌────┴──────────┴──────────┴──────────┴──────────────────┐
│                    インフラストラクチャ層                  │
│  - ロギング                                               │
│  - エラーハンドリング                                     │
│  - データ永続化                                           │
└─────────────────────────────────────────────────────────┘
```

### 2.2 マルチスレッド構成

```
メインスレッド (GUIスレッド)
├── GUI更新
├── イベント処理
└── ユーザー操作の受付

音声キャプチャスレッド
├── WASAPI経由で音声データ取得
├── バッファリング
├── Queueへのデータ追加
└── ★処理済みバッファの即座削除（メモリ管理）

文字起こしスレッド
├── Queueからデータ取得
├── faster-whisper処理
├── 結果のコールバック
└── ★処理済み音声データの即座削除

インクリメンタル保存スレッド（★新規）
├── ★セグメント生成時に即座に一時ファイルへ追記
├── ★5分ごとに正式ファイルに反映
├── ★メモリバッファクリア
└── ★バックアップ作成

ストレージ監視スレッド（★新規）
├── ★録音開始前のディスク容量チェック
├── ★録音中の30秒ごとのディスク容量監視
├── ★警告しきい値（500MB）で警告表示
├── ★緊急しきい値（100MB）で録音自動停止
└── ★一時ファイルの定期クリーンアップ

リソース監視スレッド
├── メモリ使用量チェック
├── CPU使用率監視
└── 警告通知
```

**改善ポイント**:
1. **インクリメンタル保存スレッド**: 文字起こし結果をメモリに蓄積せず、即座にディスクに書き込む
2. **ストレージ監視スレッド**: ディスク容量を常時監視し、不足時に自動停止
3. **メモリ管理**: 処理済みデータを即座に削除してメモリ使用量を一定に保つ

---

## 3. モジュール設計

### 3.1 モジュール一覧

| モジュール名 | ファイル名 | 責務 |
|-------------|-----------|------|
| メインアプリケーション | `main.py` | アプリケーションエントリポイント |
| 音声キャプチャ | `audio_capture.py` | WASAPI経由の音声取得 |
| 文字起こし | `transcriber.py` | faster-whisper処理 |
| GUI | `gui.py` | ユーザーインターフェース |
| ファイル管理 | `file_manager.py` | ファイル保存・エクスポート |
| 設定管理 | `config_manager.py` | 設定の読み書き |
| リソース監視 | `resource_monitor.py` | ディスク/メモリ監視 |
| **インクリメンタル保存** | `incremental_saver.py` | **リアルタイム自動保存** |
| **ストレージ管理** | `storage_manager.py` | **ディスク容量・一時ファイル管理** |
| ロギング | `logger.py` | ログ管理 |
| エラーハンドラ | `error_handler.py` | エラー処理 |

### 3.2 主要モジュールの詳細設計

#### 3.2.1 音声キャプチャモジュール (`audio_capture.py`)

**クラス**: `AudioCapture`

**責務**:
- Windowsループバック音声デバイスの検出
- リアルタイム音声キャプチャ
- バッファ管理
- デバイス再接続

**主要メソッド**:

```python
class AudioCapture:
    def __init__(self, sample_rate=16000, channels=1, buffer_seconds=10):
        """
        Args:
            sample_rate (int): サンプリングレート (16kHz推奨)
            channels (int): チャンネル数 (1=モノラル)
            buffer_seconds (int): バッファサイズ (秒)
        """

    def list_devices(self) -> List[Dict[str, Any]]:
        """
        利用可能な音声デバイスのリストを取得

        Returns:
            List[Dict]: デバイス情報のリスト
                - id: デバイスID
                - name: デバイス名
                - is_loopback: ループバックデバイスか
        """

    def start_capture(self, device_id: int) -> bool:
        """
        音声キャプチャを開始

        Args:
            device_id (int): 使用するデバイスID

        Returns:
            bool: 成功時True

        Raises:
            DeviceNotFoundError: デバイスが見つからない場合
            AudioCaptureError: キャプチャ開始に失敗した場合
        """

    def stop_capture(self):
        """音声キャプチャを停止"""

    def get_audio_buffer(self) -> Optional[np.ndarray]:
        """
        文字起こし用の音声バッファを取得

        Returns:
            np.ndarray or None: 音声データ（バッファサイズ分）
        """

    def get_audio_level(self) -> float:
        """
        現在の音声レベルを取得（0.0～1.0）

        Returns:
            float: 音声レベル
        """
```

**内部処理フロー**:

```
1. デバイス初期化
   ↓
2. WASAPIループバックデバイス取得
   ↓
3. オーディオストリーム開始
   ↓
4. [ループ] 音声データ読み込み
   ↓
5. バッファに追加（deque使用）
   ↓
6. バッファがいっぱいになったら通知
   ↓
7. 停止命令まで繰り返し
```

#### 3.2.2 文字起こしモジュール (`transcriber.py`)

**クラス**: `Transcriber`

**責務**:
- faster-whisperモデルのロード
- 音声→テキスト変換
- 言語切り替え
- VADフィルター適用

**主要メソッド**:

```python
class Transcriber:
    def __init__(self, model_path: str, device: str = "cpu",
                 compute_type: str = "int8"):
        """
        Args:
            model_path (str): ローカルモデルパス
            device (str): "cpu" or "cuda"
            compute_type (str): "int8", "float16", "float32"
        """

    def load_model(self) -> bool:
        """
        モデルをロード

        Returns:
            bool: 成功時True

        Raises:
            ModelNotFoundError: モデルが見つからない場合
            ModelLoadError: モデルロードに失敗した場合
        """

    def transcribe(self, audio_data: np.ndarray, language: str = "ja") -> Dict:
        """
        音声データを文字起こし

        Args:
            audio_data (np.ndarray): 音声データ (16kHz, モノラル)
            language (str): "ja" or "en"

        Returns:
            Dict: {
                "segments": [
                    {
                        "id": int,
                        "start": float,
                        "end": float,
                        "text": str,
                        "confidence": float
                    },
                    ...
                ],
                "language": str,
                "duration": float
            }

        Raises:
            TranscriptionError: 文字起こしに失敗した場合
        """

    def set_language(self, language: str):
        """言語設定を変更"""

    def get_supported_languages(self) -> List[str]:
        """サポートされている言語のリストを取得"""
```

**faster-whisper設定**:

```python
# 完全オフライン動作の設定
model = WhisperModel(
    model_size_or_path="./models/large-v3",  # ローカルパス
    device="cpu",
    compute_type="int8",
    download_root=None,  # ダウンロード無効
    local_files_only=True  # ローカルファイルのみ
)

# 文字起こしオプション
segments, info = model.transcribe(
    audio_data,
    language=language,
    vad_filter=True,  # VADフィルター有効
    vad_parameters=dict(
        threshold=0.5,
        min_speech_duration_ms=250,
        min_silence_duration_ms=2000
    ),
    beam_size=5,
    hallucination_silence_threshold=0.2  # ハルシネーション抑制
)
```

#### 3.2.3 GUIモジュール (`gui.py`)

**クラス**: `MainWindow`

**責務**:
- ユーザーインターフェースの構築
- イベントハンドリング
- リアルタイム表示更新
- ユーザー操作の受付

**主要メソッド**:

```python
class MainWindow:
    def __init__(self):
        """メインウィンドウの初期化"""

    def setup_ui(self):
        """UI要素の配置"""

    def on_start_recording(self):
        """録音開始ボタンのハンドラ"""

    def on_stop_recording(self):
        """録音停止ボタンのハンドラ"""

    def on_save_file(self):
        """ファイル保存ボタンのハンドラ"""

    def update_transcription_display(self, text: str, timestamp: str):
        """文字起こし結果の表示更新"""

    def update_audio_level(self, level: float):
        """音声レベルメーターの更新"""

    def show_error(self, message: str, details: str = None):
        """エラーダイアログの表示"""

    def show_settings_dialog(self):
        """設定ダイアログの表示"""
```

**UI構成**:

```
┌─────────────────────────────────────────────────────┐
│ OfflineVoiceLogger v1.0.0                     [_][□][X]│
├─────────────────────────────────────────────────────┤
│ [ファイル] [編集] [表示] [ツール] [ヘルプ]              │
├─────────────────────────────────────────────────────┤
│ デバイス: [Stereo Mix ▼]  言語: [日本語 ▼]          │
│ 保存先: [C:\Users\...\Documents   ] [参照]           │
│                                                     │
│ [■ 録音開始] [□ 停止] [|| 一時停止]                 │
│ ┌──────────────────────────────────────────────┐  │
│ │ 音声レベル: ████████░░░░░░░░ 65%              │  │
│ └──────────────────────────────────────────────┘  │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ 文字起こし結果                                  │   │
│ │                                                │   │
│ │ [10:30:15] こんにちは、テストです。              │   │
│ │ [10:30:20] 音声認識のテストを行っています。      │   │
│ │                                                │   │
│ │                                                │   │
│ │                                                │   │
│ └─────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│ ⚫ 録音中 | 経過: 00:15:32 | 文字数: 1,234 | CPU: 45% │
└─────────────────────────────────────────────────────┘
```

#### 3.2.4 ファイル管理モジュール (`file_manager.py`)

**クラス**: `FileManager`

**責務**:
- ファイル保存
- 複数形式のエクスポート
- 自動保存
- バックアップ管理

**主要メソッド**:

```python
class FileManager:
    def __init__(self, base_directory: str):
        """
        Args:
            base_directory (str): ベースディレクトリ
        """

    def save_as_text(self, segments: List[Dict], filepath: str,
                     encoding: str = "utf-8") -> bool:
        """
        TXT形式で保存

        Args:
            segments (List[Dict]): 文字起こしセグメント
            filepath (str): 保存先パス
            encoding (str): エンコーディング

        Returns:
            bool: 成功時True
        """

    def save_as_srt(self, segments: List[Dict], filepath: str) -> bool:
        """SRT字幕形式で保存"""

    def save_as_json(self, data: Dict, filepath: str) -> bool:
        """JSON形式で保存"""

    def auto_save(self, segments: List[Dict]) -> str:
        """
        自動保存

        Returns:
            str: 保存したファイルパス
        """

    def create_backup(self, filepath: str) -> str:
        """バックアップファイルを作成"""

    def cleanup_old_backups(self, max_backups: int = 10):
        """古いバックアップを削除"""
```

**ファイル形式**:

**TXT形式**:
```
[10:30:15] こんにちは、テストです。
[10:30:20] 音声認識のテストを行っています。
```

**SRT形式**:
```
1
00:00:00,000 --> 00:00:05,200
こんにちは、テストです。

2
00:00:05,200 --> 00:00:12,300
音声認識のテストを行っています。
```

**JSON形式**: データ構造設計（4章）参照

#### 3.2.5 インクリメンタル保存モジュール (`incremental_saver.py`)

**クラス**: `IncrementalSaver`

**責務**:
- 文字起こし結果のリアルタイム保存
- メモリ使用量の最小化
- クラッシュ時のデータ損失防止
- 自動バックアップ管理

**設計方針**:
文字起こし結果をメモリ上に蓄積せず、セグメントごとにファイルに追記することで、長時間録音でもメモリ使用量を一定に保ち、クラッシュ時のデータ損失を最小化する。

**主要メソッド**:

```python
class IncrementalSaver:
    def __init__(self, base_filepath: str, auto_save_interval: int = 300):
        """
        Args:
            base_filepath (str): 保存先ファイルパス
            auto_save_interval (int): 自動保存間隔（秒）
        """
        self.base_filepath = base_filepath
        self.temp_filepath = base_filepath + ".tmp"
        self.backup_filepath = base_filepath + ".backup"
        self.auto_save_interval = auto_save_interval
        self.last_save_time = time.time()
        self.unsaved_segments = []
        self.lock = threading.Lock()

    def append_segment(self, segment: Dict) -> bool:
        """
        セグメントをメモリとファイルに追加

        Args:
            segment (Dict): 文字起こしセグメント
                {
                    "id": int,
                    "start": float,
                    "end": float,
                    "text": str,
                    "confidence": float
                }

        Returns:
            bool: 成功時True

        処理フロー:
            1. セグメントを一時リストに追加（メモリ）
            2. 一時ファイルに即座に追記（ディスク）
            3. 自動保存間隔に達したら正式ファイルに反映
        """
        with self.lock:
            # メモリに追加（UIリアルタイム表示用）
            self.unsaved_segments.append(segment)

            # 一時ファイルに即座に追記（クラッシュ対策）
            self._append_to_temp_file(segment)

            # 自動保存タイミングチェック
            if time.time() - self.last_save_time >= self.auto_save_interval:
                self.flush_to_disk()

        return True

    def _append_to_temp_file(self, segment: Dict):
        """一時ファイルに追記（排他制御あり）"""
        try:
            with open(self.temp_filepath, 'a', encoding='utf-8') as f:
                timestamp = self._format_timestamp(segment['start'])
                f.write(f"[{timestamp}] {segment['text']}\n")
                f.flush()  # バッファを即座にディスクに書き込み
                os.fsync(f.fileno())  # OSレベルでディスクに書き込み
        except IOError as e:
            logger.error(f"Failed to append to temp file: {e}")
            raise

    def flush_to_disk(self) -> bool:
        """
        一時ファイルを正式ファイルに反映

        処理フロー:
            1. 現在の正式ファイルをバックアップ
            2. 一時ファイルを正式ファイルにリネーム
            3. 新しい一時ファイルを作成
            4. メモリ上のバッファをクリア

        Returns:
            bool: 成功時True
        """
        with self.lock:
            try:
                # 既存ファイルをバックアップ
                if os.path.exists(self.base_filepath):
                    shutil.copy2(self.base_filepath, self.backup_filepath)

                # 一時ファイルを正式ファイルに反映
                if os.path.exists(self.temp_filepath):
                    shutil.move(self.temp_filepath, self.base_filepath)

                # メモリバッファをクリア
                self.unsaved_segments.clear()
                self.last_save_time = time.time()

                logger.info(f"Flushed to disk: {self.base_filepath}")
                return True

            except Exception as e:
                logger.error(f"Failed to flush to disk: {e}")
                return False

    def recover_from_crash(self) -> List[Dict]:
        """
        クラッシュから復旧（一時ファイルから読み込み）

        Returns:
            List[Dict]: 復旧したセグメント
        """
        segments = []

        # 一時ファイルが存在する場合は復旧
        if os.path.exists(self.temp_filepath):
            try:
                with open(self.temp_filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        segment = self._parse_line(line)
                        if segment:
                            segments.append(segment)
                logger.info(f"Recovered {len(segments)} segments from crash")
            except Exception as e:
                logger.error(f"Failed to recover from crash: {e}")

        return segments

    def get_memory_usage(self) -> int:
        """
        現在のメモリ使用量を取得（バイト）

        Returns:
            int: メモリ使用量（バイト）
        """
        import sys
        return sys.getsizeof(self.unsaved_segments)

    def cleanup(self):
        """クリーンアップ（終了時）"""
        self.flush_to_disk()
        if os.path.exists(self.temp_filepath):
            os.remove(self.temp_filepath)
```

**保存タイミングの詳細**:

```
┌─────────────────────────────────────────────────────┐
│ 保存タイミング戦略                                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 1. リアルタイム保存（即座）                           │
│    文字起こしセグメント生成                           │
│    ↓                                                │
│    一時ファイルに即座に追記                           │
│    ↓                                                │
│    メモリに保持（GUIリアルタイム表示用）              │
│                                                     │
│ 2. 自動保存（5分ごと、デフォルト）                    │
│    タイマーチェック                                   │
│    ↓                                                │
│    現在のファイルをバックアップ                       │
│    ↓                                                │
│    一時ファイル → 正式ファイルに反映                  │
│    ↓                                                │
│    メモリバッファクリア                               │
│                                                     │
│ 3. 手動保存（ユーザー操作）                           │
│    「保存」ボタンクリック                             │
│    ↓                                                │
│    即座にflush_to_disk()実行                         │
│                                                     │
│ 4. 終了時保存                                        │
│    アプリ終了                                        │
│    ↓                                                │
│    cleanup()で強制保存                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**メモリ使用量の管理**:

```python
# メモリ効率的な設計
# - 文字起こし結果をメモリに蓄積しない
# - unsaved_segmentsは最大5分間のセグメントのみ保持
# - 自動保存後に即座にクリア

# 例: 5分間の文字起こし結果
# - 平均セグメント数: 60個（5秒に1セグメント）
# - 1セグメントのサイズ: 約200バイト
# - 合計メモリ使用量: 約12KB（非常に小さい）

# 従来の設計（全データをメモリに保持）の場合:
# - 8時間録音: 約5,760セグメント
# - メモリ使用量: 約1.2MB
#
# 新設計（5分間のみ保持）の場合:
# - 常に60セグメント
# - メモリ使用量: 約12KB（100分の1）
```

#### 3.2.6 ストレージ管理モジュール (`storage_manager.py`)

**クラス**: `StorageManager`

**責務**:
- ディスク容量の監視と管理
- 一時ファイルのクリーンアップ
- 音声バッファの管理
- ストレージ容量不足時の対応

**主要メソッド**:

```python
class StorageManager:
    def __init__(self, save_directory: str,
                 warning_threshold_mb: int = 500,
                 critical_threshold_mb: int = 100):
        """
        Args:
            save_directory (str): 保存先ディレクトリ
            warning_threshold_mb (int): 警告しきい値（MB）
            critical_threshold_mb (int): 緊急しきい値（MB）
        """
        self.save_directory = save_directory
        self.warning_threshold = warning_threshold_mb * 1024 * 1024
        self.critical_threshold = critical_threshold_mb * 1024 * 1024
        self.temp_dir = os.path.join(os.getenv('TEMP'), 'OfflineVoiceLogger')
        os.makedirs(self.temp_dir, exist_ok=True)

    def check_disk_space_before_recording(self) -> Tuple[bool, str]:
        """
        録音開始前のディスク容量チェック

        Returns:
            Tuple[bool, str]: (開始可能か, メッセージ)
        """
        stat = psutil.disk_usage(self.save_directory)
        free_bytes = stat.free

        # 最低1GB必要
        if free_bytes < 1024 * 1024 * 1024:
            return False, f"ディスク容量不足: {free_bytes / (1024**3):.2f}GB\n最低1GB必要です。"

        # 500MB未満で警告
        if free_bytes < self.warning_threshold:
            return True, f"警告: ディスク容量が少なくなっています（残り{free_bytes / (1024**2):.0f}MB）"

        return True, "OK"

    def monitor_disk_space_during_recording(self,
                                            callback_warning,
                                            callback_critical) -> threading.Thread:
        """
        録音中のディスク容量監視（30秒ごと）

        Args:
            callback_warning: 警告時のコールバック
            callback_critical: 緊急時のコールバック（録音停止）

        Returns:
            threading.Thread: 監視スレッド
        """
        def monitor():
            while self.is_monitoring:
                stat = psutil.disk_usage(self.save_directory)
                free_bytes = stat.free

                if free_bytes < self.critical_threshold:
                    callback_critical(f"ディスク容量が{free_bytes / (1024**2):.0f}MB未満です。録音を停止します。")
                    break
                elif free_bytes < self.warning_threshold:
                    callback_warning(f"ディスク容量が少なくなっています（残り{free_bytes / (1024**2):.0f}MB）")

                time.sleep(30)  # 30秒ごと

        self.is_monitoring = True
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread

    def cleanup_temp_audio_buffer(self):
        """
        一時音声バッファのクリーンアップ

        処理:
            1. TEMPディレクトリ内の古い音声バッファを削除
            2. 処理済みバッファを即座に削除
        """
        try:
            if os.path.exists(self.temp_dir):
                for filename in os.listdir(self.temp_dir):
                    filepath = os.path.join(self.temp_dir, filename)

                    # 24時間以上古いファイルを削除
                    if os.path.isfile(filepath):
                        file_age = time.time() - os.path.getmtime(filepath)
                        if file_age > 24 * 3600:
                            os.remove(filepath)
                            logger.info(f"Cleaned up old temp file: {filename}")

        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")

    def get_storage_statistics(self) -> Dict:
        """
        ストレージ統計情報を取得

        Returns:
            Dict: {
                "total_gb": float,
                "used_gb": float,
                "free_gb": float,
                "percent_used": float,
                "temp_files_mb": float,
                "transcript_files_count": int,
                "transcript_files_mb": float
            }
        """
        stat = psutil.disk_usage(self.save_directory)

        # 一時ファイルのサイズ
        temp_size = self._get_directory_size(self.temp_dir)

        # 文字起こしファイルの統計
        transcript_files = []
        if os.path.exists(self.save_directory):
            for filename in os.listdir(self.save_directory):
                if filename.startswith('transcript_'):
                    filepath = os.path.join(self.save_directory, filename)
                    if os.path.isfile(filepath):
                        transcript_files.append(filepath)

        transcript_size = sum(os.path.getsize(f) for f in transcript_files)

        return {
            "total_gb": stat.total / (1024**3),
            "used_gb": stat.used / (1024**3),
            "free_gb": stat.free / (1024**3),
            "percent_used": stat.percent,
            "temp_files_mb": temp_size / (1024**2),
            "transcript_files_count": len(transcript_files),
            "transcript_files_mb": transcript_size / (1024**2)
        }

    def _get_directory_size(self, directory: str) -> int:
        """ディレクトリの合計サイズを取得（バイト）"""
        total_size = 0
        if os.path.exists(directory):
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        return total_size

    def suggest_cleanup_actions(self) -> List[str]:
        """
        クリーンアップアクションを提案

        Returns:
            List[str]: 提案リスト
        """
        suggestions = []

        stat = psutil.disk_usage(self.save_directory)
        free_gb = stat.free / (1024**3)

        if free_gb < 1:
            suggestions.append("古い文字起こしファイルを削除してください")
            suggestions.append("一時ファイルをクリーンアップしてください")
            suggestions.append("他のドライブに保存先を変更してください")

        # 一時ファイルが大きい場合
        temp_size_mb = self._get_directory_size(self.temp_dir) / (1024**2)
        if temp_size_mb > 100:
            suggestions.append(f"一時ファイルが{temp_size_mb:.0f}MBあります。クリーンアップを推奨します。")

        return suggestions
```

**音声バッファの管理戦略**:

```python
# 音声バッファの一時保存と削除
class AudioBufferStorage:
    """音声バッファの一時ストレージ管理"""

    def __init__(self, temp_dir: str, max_memory_mb: int = 1024):
        self.temp_dir = temp_dir
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_buffer = collections.deque()

    def add_audio_chunk(self, audio_data: np.ndarray):
        """音声チャンクを追加"""
        # メモリ使用量チェック
        current_memory = self._get_buffer_memory_size()

        if current_memory > self.max_memory_bytes:
            # メモリ超過: 古いデータをディスクに退避
            self._flush_to_temp_disk()

        self.current_buffer.append(audio_data)

    def get_buffer_for_transcription(self) -> np.ndarray:
        """文字起こし用バッファを取得"""
        buffer_data = np.concatenate(list(self.current_buffer))

        # バッファクリア（メモリ解放）
        self.current_buffer.clear()

        return buffer_data

    def _flush_to_temp_disk(self):
        """古いデータを一時ディスクに退避（必要に応じて）"""
        # 通常はバッファクリアで対応
        # 長時間録音の場合のみディスクに退避
        pass

    def cleanup_after_transcription(self):
        """文字起こし後のクリーンアップ"""
        # 処理済み音声データを即座に削除
        self.current_buffer.clear()

        # 一時ファイルも削除
        if os.path.exists(self.temp_dir):
            for filename in os.listdir(self.temp_dir):
                if filename.startswith('audio_buffer_'):
                    filepath = os.path.join(self.temp_dir, filename)
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        logger.warning(f"Failed to remove temp audio file: {e}")
```

#### 3.2.5 設定管理モジュール (`config_manager.py`)

**クラス**: `ConfigManager`

**責務**:
- 設定ファイルの読み書き
- デフォルト値の管理
- 設定の検証

**主要メソッド**:

```python
class ConfigManager:
    def __init__(self, config_path: str = None):
        """
        Args:
            config_path (str): 設定ファイルパス
                デフォルト: %APPDATA%\OfflineVoiceLogger\config.ini
        """

    def load_config(self) -> Dict:
        """設定を読み込み"""

    def save_config(self, config: Dict) -> bool:
        """設定を保存"""

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """設定値を取得"""

    def set(self, section: str, key: str, value: Any):
        """設定値を設定"""

    def reset_to_default(self):
        """設定をデフォルトに戻す"""

    def validate_config(self, config: Dict) -> Tuple[bool, List[str]]:
        """
        設定を検証

        Returns:
            Tuple[bool, List[str]]: (検証結果, エラーメッセージリスト)
        """
```

#### 3.2.6 リソース監視モジュール (`resource_monitor.py`)

**クラス**: `ResourceMonitor`

**責務**:
- ディスク容量監視
- メモリ使用量監視
- CPU使用率監視
- 警告通知

**主要メソッド**:

```python
class ResourceMonitor:
    def __init__(self, warning_threshold_mb: int = 500,
                 critical_threshold_mb: int = 100):
        """
        Args:
            warning_threshold_mb (int): 警告しきい値（MB）
            critical_threshold_mb (int): 緊急しきい値（MB）
        """

    def check_disk_space(self, path: str) -> Tuple[str, int]:
        """
        ディスク容量チェック

        Returns:
            Tuple[str, int]: (状態, 空き容量)
                状態: "ok", "warning", "critical"
        """

    def check_memory_usage(self) -> Tuple[str, float]:
        """
        メモリ使用率チェック

        Returns:
            Tuple[str, float]: (状態, 使用率)
        """

    def get_cpu_usage(self) -> float:
        """CPU使用率を取得 (%)"""

    def start_monitoring(self, interval_seconds: int = 30):
        """定期監視を開始"""

    def stop_monitoring(self):
        """監視を停止"""
```

---

## 4. データ設計

### 4.1 データ構造

#### 4.1.1 文字起こし結果データ

```json
{
  "metadata": {
    "version": "1.0.0",
    "created_at": "2025-11-09T10:30:00",
    "device_name": "Stereo Mix",
    "language": "ja",
    "model": "large-v3",
    "duration_seconds": 3600
  },
  "segments": [
    {
      "id": 1,
      "start": 0.0,
      "end": 5.2,
      "text": "こんにちは、テストです。",
      "confidence": 0.95
    },
    {
      "id": 2,
      "start": 5.2,
      "end": 12.3,
      "text": "音声認識のテストを行っています。",
      "confidence": 0.92
    }
  ],
  "statistics": {
    "total_segments": 150,
    "total_characters": 4500,
    "average_confidence": 0.93
  }
}
```

#### 4.1.2 設定ファイル (`config.ini`)

```ini
[General]
version = 1.0.0
first_run = False
language = ja

[Audio]
device_name = Stereo Mix
sample_rate = 16000
buffer_size_seconds = 10
vad_threshold = 0.5

[Transcription]
model = large-v3
language = ja
beam_size = 5
vad_filter = True
hallucination_threshold = 0.2

[UI]
window_width = 800
window_height = 600
window_x = 100
window_y = 100
font_size = 10
theme = light
auto_scroll = True

[Files]
save_directory = C:\Users\{username}\Documents\OfflineVoiceLogger
file_name_template = transcript_{YYYYMMDD}_{HHMMSS}.txt
auto_save_enabled = True
auto_save_interval_minutes = 5
encoding = utf-8

[Storage]
max_memory_usage_mb = 1024
max_buffer_size_seconds = 30
disk_warning_threshold_mb = 500
disk_critical_threshold_mb = 100
auto_cleanup_enabled = True
max_backup_files = 10
max_log_files = 5
debug_audio_save_enabled = False

[Advanced]
log_level = INFO
show_performance_monitor = False
```

### 4.2 データフロー

```
音声デバイス
    ↓ (音声データ)
音声キャプチャモジュール
    ↓ (バッファリング)
Queue (スレッド間通信)
    ↓ (音声データ)
文字起こしモジュール
    ↓ (faster-whisper処理)
文字起こし結果
    ↓ (コールバック)
GUI (リアルタイム表示)
    ↓ (保存命令)
ファイル管理モジュール
    ↓ (TXT/SRT/JSON)
ローカルストレージ
```

### 4.3 ディレクトリ構造

```
C:\Program Files\OfflineVoiceLogger\
├── OfflineVoiceLogger.exe
├── models\
│   └── large-v3\
│       ├── model.bin
│       ├── config.json
│       └── ...
├── assets\
│   ├── icon.ico
│   └── images\
└── LICENSE.txt

%APPDATA%\OfflineVoiceLogger\
├── config.ini
├── logs\
│   ├── app.log
│   ├── app.log.1
│   └── ...
├── backup\
│   ├── transcript_20251109_103000_backup.txt
│   └── ...
└── crash_reports\
    └── crash_20251109_105030.log

%TEMP%\OfflineVoiceLogger\
└── audio_buffer\
    └── (一時音声ファイル - 処理後自動削除)

%USERPROFILE%\Documents\OfflineVoiceLogger\
├── transcript_20251109_103000.txt
├── transcript_20251109_103000.srt
└── transcript_20251109_103000.json
```

---

## 5. ユーザーインターフェース設計

### 5.1 デザイン指針

**コンセプト**: プロフェッショナル、信頼性、シンプル、視認性重視

### 5.2 カラースキーム

**ライトモード**:
- ベース背景: #F5F5F5 (ライトグレー)
- ウィンドウ背景: #FFFFFF (ホワイト)
- テキスト: #212121 (ダークグレー)
- 開始ボタン: #4CAF50 (グリーン)
- 停止ボタン: #F44336 (レッド)
- アクセント: #2196F3 (ブルー)

**ダークモード**:
- ベース背景: #1E1E1E
- ウィンドウ背景: #2D2D2D
- テキスト: #E0E0E0
- アクセント: #64B5F6

### 5.3 タイポグラフィ

- フォント: Yu Gothic UI (游ゴシック UI)
- フォールバック: Meiryo UI, MS Gothic
- タイトル: 12pt Bold
- 本文: 9pt Regular
- 文字起こし結果: 10pt Regular
- ステータスバー: 8pt Regular

### 5.4 レイアウト

**ウィンドウサイズ**:
- 初期サイズ: 800px × 600px
- 最小サイズ: 600px × 400px
- リサイズ可能

**マージン・パディング**:
- ウィンドウ内側: 15px
- セクション間: 10px
- ボタン間隔: 8px

### 5.5 主要画面

#### 5.5.1 メイン画面

```
┌─────────────────────────────────────────────────────┐
│ OfflineVoiceLogger v1.0.0                     [_][□][X]│
├─────────────────────────────────────────────────────┤
│ [ファイル] [編集] [表示] [ツール] [ヘルプ]              │
├─────────────────────────────────────────────────────┤
│ デバイス: [Stereo Mix ▼]  言語: [日本語 ▼]          │
│ 保存先: [C:\Users\...\Documents   ] [参照]           │
│                                                     │
│ [■ 録音開始] [□ 停止] [|| 一時停止] [💾 保存]        │
│ ┌──────────────────────────────────────────────┐  │
│ │ 音声レベル: ████████░░░░░░░░ 65%              │  │
│ └──────────────────────────────────────────────┘  │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ 文字起こし結果                                  │   │
│ │                                                │   │
│ │ [10:30:15] こんにちは、テストです。              │   │
│ │ [10:30:20] 音声認識のテストを行っています。      │   │
│ │                                                │   │
│ │                                                │   │
│ │                                                │   │
│ └─────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│ ⚫ 録音中 | 経過: 00:15:32 | 文字数: 1,234 | CPU: 45% │
└─────────────────────────────────────────────────────┘
```

#### 5.5.2 設定ダイアログ

```
┌─────────────────────────────────────┐
│ 設定                        [_][□][X] │
├─────────────────────────────────────┤
│ [一般] [音声] [文字起こし] [表示] [ストレージ] │
├─────────────────────────────────────┤
│ 一般設定                              │
│                                     │
│ 言語:                                │
│ ● 日本語  ○ English                 │
│                                     │
│ 保存先ディレクトリ:                   │
│ [C:\Users\...\Documents    ] [参照] │
│                                     │
│ 自動保存:                            │
│ ☑ 有効                              │
│ 間隔: [5] 分                         │
│                                     │
│ ファイル名テンプレート:                │
│ [transcript_{YYYYMMDD}_{HHMMSS}]   │
│                                     │
├─────────────────────────────────────┤
│            [OK] [キャンセル] [適用]    │
└─────────────────────────────────────┘
```

### 5.6 キーボードショートカット

| ショートカット | 機能 |
|--------------|------|
| Ctrl+R | 録音開始/停止 |
| Space | 一時停止/再開 |
| Ctrl+S | 手動保存 |
| Ctrl+Shift+S | 名前を付けて保存 |
| Ctrl+F | 検索 |
| Ctrl+C | コピー |
| Ctrl+A | 全選択 |
| Ctrl+ (+/-) | フォントサイズ変更 |
| Ctrl+, | 設定 |
| F1 | ヘルプ |
| Ctrl+Q | 終了 |

---

## 6. セキュリティ設計

### 6.1 ネットワーク通信の完全遮断

#### 6.1.1 環境変数設定

```python
import os

# プロキシ設定を無効化
os.environ['no_proxy'] = '*'
os.environ['NO_PROXY'] = '*'
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
```

#### 6.1.2 faster-whisperのローカル専用設定

```python
from faster_whisper import WhisperModel

# 完全オフライン動作
model = WhisperModel(
    model_size_or_path="./models/large-v3",  # ローカルパス指定
    device="cpu",
    compute_type="int8",
    download_root=None,  # ダウンロード無効化
    local_files_only=True  # ローカルファイルのみ使用
)
```

#### 6.1.3 禁止事項

以下の機能は実装しない:
- ✗ インターネット接続
- ✗ 自動更新チェック
- ✗ テレメトリー送信
- ✗ クラウドストレージ連携
- ✗ 外部API呼び出し
- ✗ オンラインヘルプ
- ✗ クラッシュレポートの外部送信

### 6.2 データ保護

#### 6.2.1 ローカル保存のみ

- すべての音声データ・文字起こし結果はローカルディスクのみに保存
- 一時ファイルもローカルに保存
- クラウドアップロード機能は実装しない

#### 6.2.2 ファイル暗号化（オプション）

```python
from cryptography.fernet import Fernet

def encrypt_file(file_path: str, key: bytes):
    """ファイルを暗号化 (AES-256)"""
    f = Fernet(key)
    with open(file_path, 'rb') as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)

    with open(file_path + '.enc', 'wb') as file:
        file.write(encrypted_data)
```

### 6.3 セキュリティ検証

#### 6.3.1 ネットワーク分離テスト

```
1. ネットワークアダプタを無効化
2. アプリケーションを起動
3. すべての機能を実行
4. 正常に動作することを確認
```

#### 6.3.2 パケットキャプチャ確認

```
1. Wiresharkを起動
2. アプリケーションを使用
3. 外部通信が0件であることを確認
```

#### 6.3.3 ファイアウォールログ確認

```
1. Windowsファイアウォールログを有効化
2. アプリケーション使用後にログを確認
3. 外部接続の試みが0件であることを確認
```

---

## 7. パフォーマンス設計

### 7.1 性能目標

#### 7.1.1 処理性能

| 項目 | 目標値 |
|-----|-------|
| 文字起こし遅延 | 15-25秒 (large-v3使用時) |
| CPU使用率 | 50-70% (推奨環境) |
| メモリ使用量 | 6-8GB (large-v3使用時) |
| GUI応答性 | 100ms以内 |

#### 7.1.2 安定性

| 項目 | 目標値 |
|-----|-------|
| 連続稼働時間 | 8時間以上 |
| メモリリーク | なし |
| クラッシュ率 | 0.01%未満 |

### 7.2 最適化戦略

#### 7.2.1 マルチスレッド処理

```python
import threading
import queue

# スレッド構成
audio_capture_thread = threading.Thread(target=capture_audio)
transcription_thread = threading.Thread(target=transcribe_audio)
file_write_thread = threading.Thread(target=write_file)

# Queueでスレッド間通信
audio_queue = queue.Queue(maxsize=10)
result_queue = queue.Queue()
```

#### 7.2.2 バッファ管理

```python
import collections

class AudioBufferManager:
    def __init__(self, max_memory_mb=1024, buffer_seconds=10):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.buffer_seconds = buffer_seconds
        self.buffer = collections.deque(maxlen=buffer_seconds * 16000)

    def add_audio_data(self, audio_chunk):
        """効率的なFIFOバッファ"""
        self.buffer.extend(audio_chunk)

    def get_buffer(self):
        """バッファ取得後クリア"""
        data = np.array(list(self.buffer))
        self.buffer.clear()
        return data
```

#### 7.2.3 メモリ管理

```python
import gc

class MemoryManager:
    def __init__(self):
        self.threshold = 0.9  # 90%

    def check_and_cleanup(self):
        """メモリ使用量チェックとクリーンアップ"""
        memory = psutil.virtual_memory()
        if memory.percent / 100.0 > self.threshold:
            # ガベージコレクション強制実行
            gc.collect()
            # バッファサイズ縮小
            self.reduce_buffer_size()
```

### 7.3 リソース監視

#### 7.3.1 ディスク容量監視

```python
def monitor_disk_space(save_directory: str, interval: int = 30):
    """30秒ごとにディスク容量をチェック"""
    while is_recording:
        stat = psutil.disk_usage(save_directory)
        free_mb = stat.free / (1024 * 1024)

        if free_mb < 100:  # 100MB未満
            # 録音を自動停止
            stop_recording()
            show_error("ディスク容量不足のため録音を停止しました")
        elif free_mb < 500:  # 500MB未満
            show_warning("ディスク容量が少なくなっています")

        time.sleep(interval)
```

#### 7.3.2 メモリ使用量監視

```python
def monitor_memory_usage():
    """メモリ使用量の監視"""
    memory = psutil.virtual_memory()
    usage_percent = memory.percent

    if usage_percent > 90:
        # 緊急対応
        reduce_buffer_size()
        suggest_lighter_model()
    elif usage_percent > 80:
        show_warning("メモリ使用量が高くなっています")
```

---

## 8. エラーハンドリング設計

### 8.1 エラー分類

| カテゴリ | 重要度 | 対応 |
|---------|-------|------|
| 致命的エラー | Critical | アプリケーション終了 |
| 重大エラー | Error | 機能停止、ユーザー通知 |
| 警告 | Warning | 通知のみ、処理継続 |
| 情報 | Info | ログのみ |

### 8.2 エラーハンドリング戦略

#### 8.2.1 カスタム例外クラス

```python
class OfflineVoiceLoggerError(Exception):
    """ベース例外クラス"""
    pass

class DeviceNotFoundError(OfflineVoiceLoggerError):
    """音声デバイスが見つからない"""
    pass

class AudioCaptureError(OfflineVoiceLoggerError):
    """音声キャプチャエラー"""
    pass

class ModelNotFoundError(OfflineVoiceLoggerError):
    """モデルファイルが見つからない"""
    pass

class ModelLoadError(OfflineVoiceLoggerError):
    """モデルロードエラー"""
    pass

class TranscriptionError(OfflineVoiceLoggerError):
    """文字起こしエラー"""
    pass

class DiskSpaceError(OfflineVoiceLoggerError):
    """ディスク容量不足"""
    pass

class MemoryError(OfflineVoiceLoggerError):
    """メモリ不足"""
    pass
```

#### 8.2.2 エラーハンドラ実装

```python
class ErrorHandler:
    def __init__(self, logger):
        self.logger = logger

    def handle_error(self, error: Exception, context: str = ""):
        """エラーを処理"""
        error_type = type(error).__name__
        error_message = str(error)

        # ログ記録
        self.logger.error(f"[{context}] {error_type}: {error_message}",
                         exc_info=True)

        # ユーザーへの通知
        if isinstance(error, DeviceNotFoundError):
            self._handle_device_not_found(error)
        elif isinstance(error, ModelNotFoundError):
            self._handle_model_not_found(error)
        elif isinstance(error, DiskSpaceError):
            self._handle_disk_space_error(error)
        elif isinstance(error, MemoryError):
            self._handle_memory_error(error)
        else:
            self._handle_generic_error(error)

    def _handle_device_not_found(self, error):
        """音声デバイスエラーの処理"""
        show_error_dialog(
            title="音声デバイスエラー",
            message="音声デバイスが見つかりません。",
            details=str(error),
            suggestions=[
                "1. デバイスマネージャーで音声デバイスを確認してください",
                "2. ステレオミキサーが有効になっているか確認してください",
                "3. デバイスドライバーを再インストールしてください"
            ]
        )
```

#### 8.2.3 エラーダイアログ

```
┌─────────────────────────────────────┐
│ ⚠ エラー                             │
├─────────────────────────────────────┤
│ 音声デバイスが見つかりません。         │
│                                     │
│ 解決方法:                            │
│ 1. デバイスマネージャーで音声デバイス │
│    を確認してください                 │
│ 2. ステレオミキサーが有効になっている │
│    か確認してください                 │
│ 3. デバイスドライバーを再インストール │
│    してください                       │
│                                     │
│ [詳細を表示 ▼]                       │
│                                     │
│          [OK] [ヘルプを開く]          │
└─────────────────────────────────────┘
```

### 8.3 ロギング設計

#### 8.3.1 ログレベル

| レベル | 用途 |
|-------|------|
| DEBUG | 開発時のデバッグ情報 |
| INFO | 通常の動作情報 |
| WARNING | 警告（処理は継続） |
| ERROR | エラー（機能停止） |
| CRITICAL | 致命的エラー（アプリ終了） |

#### 8.3.2 ログ実装

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    """ロガーのセットアップ"""
    log_dir = os.path.join(os.getenv('APPDATA'), 'OfflineVoiceLogger', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, 'app.log')

    # ログフォーマット
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # ファイルハンドラ（ローテーション）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    # ルートロガー設定
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    return logger
```

#### 8.3.3 ログ出力例

```
[2025-11-09 10:30:15] [INFO] [MainWindow] Application started
[2025-11-09 10:30:16] [INFO] [AudioCapture] Initializing audio device: Stereo Mix
[2025-11-09 10:30:17] [INFO] [Transcriber] Loading model: large-v3
[2025-11-09 10:30:25] [INFO] [Transcriber] Model loaded successfully
[2025-11-09 10:30:30] [INFO] [AudioCapture] Recording started
[2025-11-09 10:30:40] [WARNING] [AudioCapture] Buffer overflow detected
[2025-11-09 10:31:05] [ERROR] [AudioCapture] Device disconnected: Stereo Mix
[2025-11-09 10:31:05] [INFO] [AudioCapture] Attempting to reconnect...
```

### 8.4 クラッシュレポート

#### 8.4.1 クラッシュ時の処理

```python
import sys
import traceback

def handle_crash(exc_type, exc_value, exc_traceback):
    """クラッシュ時のハンドラ"""
    # クラッシュレポート作成
    crash_dir = os.path.join(os.getenv('APPDATA'),
                            'OfflineVoiceLogger',
                            'crash_reports')
    os.makedirs(crash_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    crash_file = os.path.join(crash_dir, f'crash_{timestamp}.log')

    with open(crash_file, 'w', encoding='utf-8') as f:
        f.write(f"Crash Report - {timestamp}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Exception Type: {exc_type.__name__}\n")
        f.write(f"Exception Message: {exc_value}\n\n")
        f.write("Traceback:\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

    # 現在のデータを緊急保存
    emergency_save()

    # ユーザーに通知
    show_crash_dialog(crash_file)

# グローバルハンドラ設定
sys.excepthook = handle_crash
```

---

## 9. デプロイメント設計

### 9.1 EXE化

#### 9.1.1 PyInstallerスペックファイル

```python
# OfflineVoiceLogger.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('models', 'models'),  # モデルファイルを含める
        ('assets', 'assets'),  # アイコンなど
    ],
    hiddenimports=[
        'faster_whisper',
        'sounddevice',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OfflineVoiceLogger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUIアプリ
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',  # アイコン
    version='version_info.txt'  # バージョン情報
)
```

#### 9.1.2 ビルドコマンド

```bash
pyinstaller OfflineVoiceLogger.spec
```

### 9.2 MSIインストーラー

#### 9.2.1 WiX Toolset設定 (Product.wxs)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*"
           Name="OfflineVoiceLogger"
           Language="1041"
           Version="1.0.0"
           Manufacturer="Your Name"
           UpgradeCode="YOUR-GUID-HERE">

    <Package InstallerVersion="200"
             Compressed="yes"
             InstallScope="perMachine" />

    <MajorUpgrade DowngradeErrorMessage="新しいバージョンが既にインストールされています。" />
    <MediaTemplate EmbedCab="yes" />

    <!-- 機能定義 -->
    <Feature Id="ProductFeature" Title="OfflineVoiceLogger" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
      <ComponentRef Id="ApplicationShortcut" />
      <ComponentRef Id="DesktopShortcut" />
    </Feature>

    <!-- UIシーケンス -->
    <UIRef Id="WixUI_InstallDir" />
    <Property Id="WIXUI_INSTALLDIR" Value="INSTALLFOLDER" />
  </Product>

  <!-- ディレクトリ構造 -->
  <Fragment>
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFiles64Folder">
        <Directory Id="INSTALLFOLDER" Name="OfflineVoiceLogger">
          <Directory Id="ModelsFolder" Name="models" />
          <Directory Id="AssetsFolder" Name="assets" />
        </Directory>
      </Directory>

      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="OfflineVoiceLogger"/>
      </Directory>

      <Directory Id="DesktopFolder" Name="Desktop" />
    </Directory>
  </Fragment>

  <!-- コンポーネント定義 -->
  <Fragment>
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="MainExecutable">
        <File Id="OfflineVoiceLoggerEXE"
              Source="dist\OfflineVoiceLogger.exe"
              KeyPath="yes" />
      </Component>

      <!-- モデルファイルコンポーネント -->
      <Component Id="ModelFiles" Directory="ModelsFolder">
        <File Source="models\large-v3\model.bin" />
        <File Source="models\large-v3\config.json" />
        <!-- その他のモデルファイル -->
      </Component>
    </ComponentGroup>

    <!-- スタートメニューショートカット -->
    <DirectoryRef Id="ApplicationProgramsFolder">
      <Component Id="ApplicationShortcut">
        <Shortcut Id="ApplicationStartMenuShortcut"
                  Name="OfflineVoiceLogger"
                  Target="[INSTALLFOLDER]OfflineVoiceLogger.exe"
                  WorkingDirectory="INSTALLFOLDER"
                  Icon="AppIcon" />
        <RemoveFolder Id="CleanUpShortCut" Directory="ApplicationProgramsFolder" On="uninstall"/>
        <RegistryValue Root="HKCU"
                      Key="Software\OfflineVoiceLogger"
                      Name="installed"
                      Type="integer"
                      Value="1"
                      KeyPath="yes"/>
      </Component>
    </DirectoryRef>

    <!-- デスクトップショートカット -->
    <DirectoryRef Id="DesktopFolder">
      <Component Id="DesktopShortcut">
        <Shortcut Id="DesktopShortcut"
                  Name="OfflineVoiceLogger"
                  Target="[INSTALLFOLDER]OfflineVoiceLogger.exe"
                  WorkingDirectory="INSTALLFOLDER"
                  Icon="AppIcon" />
        <RegistryValue Root="HKCU"
                      Key="Software\OfflineVoiceLogger"
                      Name="desktop_shortcut"
                      Type="integer"
                      Value="1"
                      KeyPath="yes"/>
      </Component>
    </DirectoryRef>
  </Fragment>

  <!-- アイコン定義 -->
  <Fragment>
    <Icon Id="AppIcon" SourceFile="assets\icon.ico" />
  </Fragment>
</Wix>
```

#### 9.2.2 MSIビルドスクリプト

```batch
@echo off
echo Building MSI Installer...

REM WiX Toolset のパス
set WIX_PATH=C:\Program Files (x86)\WiX Toolset v3.11\bin

REM ビルド
"%WIX_PATH%\candle.exe" Product.wxs -out obj\Product.wixobj
"%WIX_PATH%\light.exe" obj\Product.wixobj -out bin\OfflineVoiceLogger.msi -ext WixUIExtension

echo Build complete!
pause
```

### 9.3 リリースパッケージ

#### 9.3.1 ディレクトリ構造

```
OfflineVoiceLogger_v1.0.0_Release\
├── OfflineVoiceLogger_v1.0.0.msi
├── README.txt
├── LICENSE.txt
├── CHANGELOG.txt
├── docs\
│   ├── UserGuide.pdf
│   └── Troubleshooting.pdf
└── checksums.txt
```

#### 9.3.2 README.txt

```
OfflineVoiceLogger v1.0.0
=========================

完全オフライン動作のリアルタイム音声文字起こしツール

■ システム要件
- OS: Windows 10/11 (64bit)
- CPU: Intel Core i5 第8世代以上
- メモリ: 8GB以上（16GB推奨）
- ストレージ: 5GB以上の空き容量

■ インストール方法
1. OfflineVoiceLogger_v1.0.0.msi をダブルクリック
2. インストールウィザードの指示に従ってインストール
3. 管理者権限が必要です

■ 使用方法
詳細は docs\UserGuide.pdf を参照してください。

■ セキュリティについて
本ツールは完全にオフラインで動作します。
インターネット接続は一切行いません。

■ サポート
問題が発生した場合は docs\Troubleshooting.pdf を参照してください。

■ ライセンス
LICENSE.txt を参照してください。
```

### 9.4 配布チェックリスト

```
□ EXEファイルのビルド完了
□ MSIインストーラーのビルド完了
□ ウイルススキャン完了
□ クリーンPC環境でインストールテスト完了
□ ネットワーク分離状態での動作確認完了
□ ドキュメント一式作成完了
□ README.txt作成完了
□ CHANGELOG.txt作成完了
□ チェックサムファイル生成完了
□ ZIPファイル作成完了
□ バージョン番号確認完了
```

---

## 付録

### A. 開発環境セットアップ

#### A.1 必要なツール

```
- Python 3.9以上
- PyInstaller
- WiX Toolset 3.11
- Visual Studio Code (推奨)
- Git
```

#### A.2 依存ライブラリ (requirements.txt)

```
faster-whisper==0.10.0
sounddevice==0.4.6
numpy==1.24.3
psutil==5.9.5
cryptography==41.0.3
```

### B. テストケース一覧

詳細は別ドキュメント「TEST_PLAN.md」を参照。

### C. 既知の問題

- Windows 11の一部環境でステレオミキサーがデフォルトで無効
  → トラブルシューティングガイドに対処法を記載

### D. 今後の機能拡張予定

- Phase 4 (オプション機能) 参照
- ダークモード対応
- データ暗号化
- 多言語UI (英語)

---

**文書履歴**

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|---------|-------|
| 1.0.0 | 2025-11-09 | 初版作成 | - |

---

**承認**

| 役割 | 氏名 | 承認日 | 署名 |
|-----|------|-------|------|
| 設計者 | - | - | - |
| レビュー担当 | - | - | - |
| 承認者 | - | - | - |

---

**END OF DOCUMENT**
