"""
OfflineVoiceLogger - メインアプリケーション

すべてのモジュールを統合してアプリケーションとして動作させる
- マルチスレッド処理
- イベント駆動アーキテクチャ
- GUI連携
"""

import sys
import os
import threading
import queue
import time
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# モジュールのインポート
try:
    # 相対インポート (パッケージとして実行された場合)
    from .logger import setup_global_logger, get_logger
    from .config_manager import ConfigManager
    from .audio_capture import AudioCapture, DeviceNotFoundError, AudioCaptureError
    from .transcriber import Transcriber, ModelNotFoundError, TranscriptionError
    from .file_manager import FileManager
    from .gui import MainWindow
except ImportError:
    # 絶対インポート (スクリプトとして直接実行された場合)
    from logger import setup_global_logger, get_logger
    from config_manager import ConfigManager
    from audio_capture import AudioCapture, DeviceNotFoundError, AudioCaptureError
    from transcriber import Transcriber, ModelNotFoundError, TranscriptionError
    from file_manager import FileManager
    from gui import MainWindow

logger = get_logger(__name__)


class OfflineVoiceLoggerApp:
    """OfflineVoiceLoggerアプリケーションクラス"""

    def __init__(self):
        """初期化"""
        print("   3-1. ロガー初期化...")
        logger.info("=" * 60)
        logger.info("OfflineVoiceLogger 起動")
        logger.info("=" * 60)

        # 設定管理
        print("   3-2. 設定管理初期化...")
        self.config_mgr = ConfigManager()
        self.config = self.config_mgr.load_config()
        print("        -> 設定管理OK")

        # 音声キャプチャ
        print("   3-3. 音声キャプチャ初期化...")
        self.audio_capture = AudioCapture(
            sample_rate=self.config_mgr.get_int('Audio', 'sample_rate', 16000),
            channels=1,
            buffer_size_seconds=self.config_mgr.get_int('Audio', 'buffer_size_seconds', 10)
        )
        print("        -> 音声キャプチャOK")

        # 文字起こし
        print("   3-4. 文字起こしモジュール設定...")
        self.transcriber = None
        self.transcription_segments = []
        self.model_loading = False  # モデルロード中フラグ
        self.preload_verified = False  # 起動時プリロード検証結果
        self._load_result = None  # モデルロード結果 (success, error, callback)のタプル
        self._load_result_ready = False  # 結果が利用可能かどうか
        self.pending_full_load = False  # 検証完了後に本ロードを要求するフラグ
        self._load_seq = 0  # ロードリクエストの世代管理
        self.model_name = self.config_mgr.get('Transcription', 'model', 'medium')  # 現在のモデル名
        print("        -> 文字起こしモジュールOK")

        # 録音開始時刻（実時刻表示用）
        self.recording_start_time = None

        # 累積音声オフセット（秒）- 文字起こし済み音声の累積時間
        self.audio_offset = 0.0

        # ファイル管理
        print("   3-5. ファイル管理初期化...")
        save_dir = self.config_mgr.get('Files', 'save_directory')
        self.file_manager = FileManager(save_dir)
        print("        -> ファイル管理OK")

        # GUI
        print("   3-6. GUI変数初期化...")
        self.window = None

        # スレッド管理
        print("   3-7. スレッド管理初期化...")
        self.audio_thread = None
        self.transcription_thread = None
        self.is_running = False
        self.audio_queue = queue.Queue(maxsize=20)  # 10→20に増やしてオーバーフロー対策
        self.result_queue = queue.Queue()

        # タイマー
        self.audio_level_timer = None
        self.transcription_check_timer = None
        self.ui_sync_timer = None
        print("        -> 全初期化完了")

    def _get_model_path(self):
        """モデルパスを取得 (スクリプトの場所を基準)"""
        model_name = self.config_mgr.get('Transcription', 'model', 'medium')

        # スクリプトファイルの場所を基準にする
        script_dir = Path(__file__).parent.parent  # srcディレクトリの親

        # まず通常のパスをチェック（こちらを優先）
        model_path = script_dir / 'models' / model_name
        if model_path.exists() and (model_path / 'config.json').exists():
            logger.info(f"シンプルなモデルパスを使用: {model_path}")
            print(f"[モデルパス] シンプルパス: {model_path}")
            return model_path

        # Hugging Faceキャッシュ形式のパスをチェック
        hf_cache_path = script_dir / 'models' / f'models--Systran--faster-whisper-{model_name}' / 'snapshots'
        if hf_cache_path.exists():
            # snapshotsディレクトリ内の最初のディレクトリを取得
            snapshot_dirs = list(hf_cache_path.glob('*'))
            if snapshot_dirs:
                model_path = snapshot_dirs[0]
                logger.info(f"Hugging Faceキャッシュ形式のモデルパスを使用: {model_path}")
                print(f"[モデルパス] Hugging Faceキャッシュ形式: {model_path}")
                return model_path

        # どちらも見つからない場合は通常のパスを返す
        logger.info(f"モデルパス（未確認）: {model_path}")
        return model_path

    def _verify_model_files_sync(self):
        """モデルファイルの存在検証のみを行う（軽量）"""
        print("[モデル検証] 開始 (ファイル存在チェック)")
        model_path = self._get_model_path()
        print(f"[モデル検証] モデルパス: {model_path}")

        # 必須ファイル群（代表）
        candidate_files = [
            "config.json",
            "tokenizer.json",
            "vocabulary.json",  # 任意扱い（見つからなくても致命ではない）
            "model.bin"
        ]
        missing = []
        for name in candidate_files:
            p = model_path / name
            if not p.exists():
                found = any(fp.name == name for fp in model_path.rglob(name))
                if not found and name != "vocabulary.json":
                    missing.append(name)

        if missing:
            raise ModelNotFoundError(f"モデル内の必須ファイルが見つかりません: {missing}\nパス: {model_path}")

        logger.info("モデルファイル検証成功")
        print("[モデル検証] 完了")
        # 成功フラグ
        self.preload_verified = True
        # GUI更新（ベストエフォート）
        QTimer.singleShot(0, lambda: (
            self.window.update_model_status("検証済み", "green"),
            self.window.start_button.setEnabled(True),
            self.window.stop_button.setEnabled(False)
        ))
        return True, None

    def _load_transcriber_sync(self):
        """実体のTranscriberを作成し、WhisperModelをロードする（重い処理）"""
        try:
            print("[モデルロード] 本ロード開始")
            model_path = self._get_model_path()
            language = self.config_mgr.get('Transcription', 'language', 'ja')
            print(f"[モデルロード] モデルパス: {model_path}")
            print(f"[モデルロード] 言語: {language}")

            # デバイス選択方針:
            # 1) 設定 Transcription.use_cuda が "true" かつ CUDA 利用可なら CUDA/float16
            # 2) それ以外は CPU/int8
            use_cuda = False
            try:
                import torch  # オプション
                cfg_use_cuda = str(self.config_mgr.get('Transcription', 'use_cuda', 'false')).lower() == 'true'
                use_cuda = bool(cfg_use_cuda and getattr(torch, "cuda", None) and torch.cuda.is_available())
            except Exception:
                use_cuda = False
            device = "cuda" if use_cuda else "cpu"
            compute_type = "float16" if use_cuda else "int8"
            print(f"[モデルロード] デバイス: {device}, compute_type: {compute_type}")

            # Transcriber初期化（cpu_threadsとnum_workersはデフォルトに任せる）
            self.transcriber = Transcriber(
                model_path=str(model_path),
                device=device,
                compute_type=compute_type,
                language=language
            )
            # モデルロード
            logger.info("faster-whisperモデルをロード中...")
            print("[モデルロード] faster-whisperモデルをロード中...")
            try:
                self.transcriber.load_model()
            except Exception as e:
                # CUDA 失敗時は CPU/int8 にフォールバックして再試行
                logger.error(f"モデルロードに失敗: {e}. CPU/int8 にフォールバックします。")
                print("[モデルロード] フォールバック: CPU/int8 で再試行")
                self.transcriber = Transcriber(
                    model_path=str(model_path),
                    device="cpu",
                    compute_type="int8",
                    language=language
                )
                self.transcriber.load_model()
            logger.info("モデルロード完了")
            print("[モデルロード] 本ロード完了")
            return True, None

        except ModelNotFoundError as e:
            error_msg = str(e)
            print(f"[モデルロード] エラー - モデルが見つかりません: {error_msg}")
            logger.error(f"モデルが見つかりません: {error_msg}")
            return False, ("モデルエラー", error_msg)

        except Exception as e:
            print(f"[モデルロード] エラー: {e}")
            logger.error(f"モデルロードエラー: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            return False, ("初期化エラー", f"モデルのロードに失敗しました:\n{e}")

    def initialize_transcriber_async(self, callback, verify_only: bool = False):
        """文字起こしモジュールの初期化 (非同期 - 別スレッドで実行)

        Args:
            callback: 完了時に呼ばれるコールバック関数 callback(success: bool, error: tuple)
            verify_only (bool): Trueの場合はファイル検証のみ。Falseは本ロードまで実施。
        """
        # 新しいロード世代を開始
        self._load_seq += 1
        current_seq = self._load_seq

        def worker():
            success = False
            error = None
            try:
                # 古い世代なら何もしない
                if current_seq != self._load_seq:
                    return
                self.model_loading = True
                if verify_only:
                    QTimer.singleShot(0, lambda: self.window.update_status("モデル検証中...", "blue"))
                    QTimer.singleShot(0, lambda: self.window.update_model_status("検証中...", "blue"))
                    success, error = self._verify_model_files_sync()
                else:
                    QTimer.singleShot(0, lambda: self.window.update_status("モデルロード中...", "blue"))
                    QTimer.singleShot(0, lambda: self.window.update_model_status("ロード中...", "blue"))
                    success, error = self._load_transcriber_sync()

            except Exception as e:
                logger.error(f"モデルロード中の予期しないエラー: {e}", exc_info=True)
                success = False
                error = ("エラー", f"モデルロード中にエラーが発生しました:\n{e}")

            finally:
                # 必ずフラグをクリアして結果を保存
                self.model_loading = False
                if current_seq == self._load_seq:
                    # 結果を保存（メインスレッドのタイマーで処理）
                    self._load_result = (success, error, callback)
                    self._load_result_ready = True
                    print(f"[モデルロード] 結果を保存: success={success}")

        # 別スレッドで実行
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        # タイムアウト監視（120秒経過しても完了しない場合は復旧）
        def _timeout_guard():
            try:
                # モデルが既にロードされている場合はタイムアウトエラーを出さない
                if current_seq == self._load_seq and self.model_loading:
                    if not verify_only and self.transcriber is not None and self.transcriber.is_model_loaded():
                        # モデルは実際にはロード済み - 単にコールバックを呼ぶ
                        logger.info("モデルはロード済み - タイムアウトガードをスキップ")
                        self._on_model_load_complete(True, None, callback)
                    else:
                        logger.error("モデルロードがタイムアウトしました (120秒)")
                        self._on_model_load_complete(False, ("初期化エラー", "モデルロードがタイムアウトしました（120秒）。"), callback)
            except Exception:
                pass
        QTimer.singleShot(120000, _timeout_guard)

    def _on_model_load_complete(self, success, error, callback):
        """モデルロード完了時の処理 (GUIスレッドで実行)"""
        # model_loadingフラグはworkerスレッドのfinallyブロックでクリアされる
        # 経過表示タイマーは廃止（GUIスレッド制約回避）

        if success:
            # 検証のみ成功か、本ロード成功かで振る舞い分岐
            if self.transcriber is None:
                # 検証のみ完了 → 待機に戻す
                self.window.update_model_status(f"{self.model_name} (検証済み)", "green")
                self.window.update_status("待機中", "")
                try:
                    self.preload_verified = True
                    self.window.start_button.setEnabled(True)
                    self.window.stop_button.setEnabled(False)
                    self.window.is_recording = False
                except Exception:
                    pass
                print("\n[モデル検証] GUI更新: 検証済み -> 待機中")
                # もし録音開始時に本ロードを予約していたら、直ちに本ロードを開始
                if self.pending_full_load:
                    self.pending_full_load = False
                    print("[モデル検証] 本ロード予約あり → 本ロードを開始")
                    self.initialize_transcriber_async(self._on_transcriber_ready, verify_only=False)
            else:
                # 本ロード完了 → 録音開始準備完了（この後キャプチャ開始）
                self.window.update_status("録音開始準備完了", "green")
                self.window.update_model_status(f"{self.model_name} (ロード完了)", "green")
                print("\n[モデルロード] GUI更新: ロード完了")
            callback(True, None)
        else:
            self.window.update_status("モデルロード失敗", "red")
            self.window.update_model_status("エラー", "red")
            print("\n[モデルロード] GUI更新: エラー")
            try:
                # 失敗時は待機に戻し、開始ボタンを再度有効化
                self.window.update_status("待機中", "")
                self.window.start_button.setEnabled(True)
                self.window.stop_button.setEnabled(False)
                self.window.is_recording = False
            except Exception:
                pass
            if error:
                self.window.show_error(error[0], error[1])
            callback(False, error)

    def setup_gui(self):
        """GUIのセットアップ"""
        print("   4-1. MainWindow作成...")
        self.window = MainWindow()
        print("        -> MainWindow作成OK")

        # シグナル接続
        print("   4-2. シグナル接続...")
        self.window.start_recording_signal.connect(self.start_recording)
        self.window.stop_recording_signal.connect(self.stop_recording)
        self.window.save_file_signal.connect(self.save_file)
        self.window.reset_text_signal.connect(self.reset_text)
        print("        -> シグナル接続OK")

        # デバイスリスト更新
        print("   4-3. デバイスリスト取得...")
        try:
            devices = self.audio_capture.list_devices()
            self.window.update_device_list(devices)
            print(f"        -> デバイスリストOK ({len(devices)}個)")
        except Exception as e:
            logger.error(f"デバイスリスト取得エラー: {e}")
            print(f"        -> デバイスリストエラー: {e}")
            self.window.show_error("デバイスエラー", f"音声デバイスの取得に失敗しました:\n{e}")

        # 保存先設定
        print("   4-4. 保存先設定...")
        save_dir = self.config_mgr.get('Files', 'save_directory')
        if save_dir:
            self.window.set_save_directory(save_dir)
        print("        -> 保存先設定OK")

        # タイマー設定
        print("   4-5. タイマー設定...")
        self.audio_level_timer = QTimer()
        self.audio_level_timer.timeout.connect(self.update_audio_level)

        self.transcription_check_timer = QTimer()
        self.transcription_check_timer.timeout.connect(self.check_transcription_results)
        # UI同期タイマー（起動中常に軽量に状態を整える）
        self.ui_sync_timer = QTimer()
        self.ui_sync_timer.timeout.connect(self._sync_ui_state)
        self.ui_sync_timer.start(1000)
        print("        -> タイマー設定OK")

        # モデル状態の初期表示
        if self.transcriber is not None:
            self.window.update_model_status(f"{self.model_name} (ロード完了)", "green")
        else:
            self.window.update_model_status(f"{self.model_name} (未ロード)", "orange")
            # 起動直後にモデルを非同期プリロードし、完了まで開始ボタンを無効化
            try:
                self.window.start_button.setEnabled(False)
            except Exception:
                pass
            # イベントループ開始後に軽量検証のみ実施
            QTimer.singleShot(0, lambda: self.initialize_transcriber_async(lambda success, error: None, verify_only=True))
            # 念のためのフォールバック: 3秒後に検証済みかつ未録音なら開始ボタンを確認・有効化
            def _fallback_enable():
                try:
                    if getattr(self, "preload_verified", False) and not self.window.is_recording:
                        self.window.start_button.setEnabled(True)
                        self.window.stop_button.setEnabled(False)
                except Exception:
                    pass
            QTimer.singleShot(3000, _fallback_enable)

        logger.info("GUI設定完了")

    def start_recording(self):
        """録音開始"""
        try:
            print("\n[録音開始] 処理開始")
            logger.info("録音開始処理")

            # ローディング表示を開始
            self.window.show_loading("準備中...")

            # 既に何らかのロードが走っている場合の扱い
            if self.model_loading:
                # 検証中なら中断して即「本ロード」を開始する
                if self.transcriber is None:
                    print("[録音開始] 検証中を中断して本ロードへ切替")
                    logger.info("検証ジョブを無効化し、本ロードを即開始します")
                    try:
                        # 進行中の検証ジョブを世代無効化
                        self._load_seq += 1
                        self.model_loading = False
                        self.pending_full_load = False
                        # GUI表示を更新
                        self.window.show_loading("モデルをロード中...")
                        self.window.update_status("モデルロード中...", "blue")
                        self.window.update_model_status("ロード中...", "blue")
                    except Exception:
                        pass
                    # イベントループに乗せて本ロード開始
                    QTimer.singleShot(0, lambda: self.initialize_transcriber_async(self._on_transcriber_ready, verify_only=False))
                else:
                    print("[録音開始] モデルロード中のため待機")
                    logger.warning("モデルロード中です")
                return

            # Transcriber初期化 (初回のみ - 非同期)
            if self.transcriber is None:
                print("[録音開始] 初回録音 - モデルを非同期ロード開始（本ロード）")
                logger.info("初回録音: モデルを非同期ロード（本ロード）")
                self.window.show_loading("モデルをロード中...")
                self.initialize_transcriber_async(self._on_transcriber_ready, verify_only=False)
                return

            # モデル準備済み: 録音開始
            print("[録音開始] モデル準備済み - キャプチャ開始")
            self.window.show_loading("キャプチャ開始中...")
            self._start_capture()

        except Exception as e:
            print(f"[録音開始] エラー発生: {e}")
            logger.error(f"録音開始エラー: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            self.window.hide_loading()
            self.window.show_error("録音エラー", f"録音の開始に失敗しました:\n{e}")
            self.window.start_button.setEnabled(True)
            self.window.stop_button.setEnabled(False)

    def _on_transcriber_ready(self, success, error):
        """モデルロード完了後のコールバック"""
        if success:
            logger.info("モデルロード完了 - 録音を開始します")
            try:
                # 準備完了、UIを反映（録音開始直前）
                self.window.show_loading("キャプチャ開始中...")
                self.window.update_status("録音開始準備完了", "green")
            except Exception:
                pass
            self._start_capture()
        else:
            logger.error("モデルロード失敗")
            try:
                self.window.hide_loading()
                self.window.start_button.setEnabled(True)
                self.window.stop_button.setEnabled(False)
                self.window.is_recording = False
                self.window.update_status("待機中", "")
            except Exception:
                pass

    def _start_capture(self):
        """録音キャプチャを開始 (内部メソッド)"""
        try:
            # デバイスID取得
            device_id = self.window.get_selected_device_id()

            # スレッド開始準備
            self.is_running = True
            self.transcription_segments.clear()
            self.window.clear_transcription_text()

            # 録音開始時刻を記録（実時刻表示用）
            from datetime import datetime
            self.recording_start_time = datetime.now()

            # 累積音声オフセットをリセット
            self.audio_offset = 0.0

            # ワーカースレッドを先に起動
            self.transcription_thread = threading.Thread(
                target=self.transcription_worker,
                daemon=True
            )
            self.transcription_thread.start()
            logger.info("文字起こしスレッド開始")

            self.audio_thread = threading.Thread(
                target=self.audio_worker,
                daemon=True
            )
            self.audio_thread.start()
            logger.info("音声処理スレッド開始")

            # スレッドの起動を待つ
            time.sleep(0.1)

            # 音声キャプチャ開始 (これ以降コールバックが呼ばれる)
            self.audio_capture.start_capture(device_id)
            logger.info("音声キャプチャ開始")

            # タイマー開始
            self.audio_level_timer.start(100)  # 100ms
            self.transcription_check_timer.start(500)  # 500ms

            # ローディングを非表示
            self.window.hide_loading()
            self.window.update_status("録音中", "green")
            try:
                # 実際に録音が走り始めたのでUIを録音状態へ
                self.window.stop_button.setEnabled(True)
                self.window.start_button.setEnabled(False)
                self.window.is_recording = True
            except Exception:
                pass
            logger.info("録音開始完了")

        except DeviceNotFoundError as e:
            logger.error(f"デバイスエラー: {e}")
            self.is_running = False
            self.window.hide_loading()
            self.window.show_error("デバイスエラー", str(e))
            try:
                self.window.start_button.setEnabled(True)
                self.window.stop_button.setEnabled(False)
                self.window.is_recording = False
                self.window.update_status("待機中", "")
            except Exception:
                pass

        except Exception as e:
            logger.error(f"キャプチャ開始エラー: {e}", exc_info=True)
            self.is_running = False
            self.window.hide_loading()
            self.window.show_error("録音エラー", f"録音の開始に失敗しました:\n{e}")
            try:
                self.window.start_button.setEnabled(True)
                self.window.stop_button.setEnabled(False)
                self.window.is_recording = False
                self.window.update_status("待機中", "")
            except Exception:
                pass

    def stop_recording(self):
        """録音停止"""
        try:
            logger.info("録音停止処理")

            # タイマー停止
            if self.audio_level_timer:
                self.audio_level_timer.stop()
            if self.transcription_check_timer:
                self.transcription_check_timer.stop()

            # スレッド停止
            self.is_running = False

            # 音声キャプチャ停止
            self.audio_capture.stop_capture()

            # スレッド終了待機
            if self.audio_thread and self.audio_thread.is_alive():
                self.audio_thread.join(timeout=2)
            if self.transcription_thread and self.transcription_thread.is_alive():
                self.transcription_thread.join(timeout=2)

            self.window.update_status("停止", "orange")
            logger.info("録音停止完了")

        except Exception as e:
            logger.error(f"録音停止エラー: {e}")
            self.window.show_error("停止エラー", f"録音の停止に失敗しました:\n{e}")

    def audio_worker(self):
        """音声処理ワーカー (別スレッド)"""
        logger.info("音声処理スレッド開始")

        while self.is_running:
            try:
                # バッファが満杯になったら取得
                audio_buffer = self.audio_capture.get_audio_buffer()

                if audio_buffer is not None:
                    # 現在のオフセットを保存
                    current_offset = self.audio_offset

                    # オフセットを更新（このバッファの長さ分進める）
                    buffer_duration = len(audio_buffer) / self.audio_capture.sample_rate
                    self.audio_offset += buffer_duration

                    # キューに追加（音声データとオフセットのタプル）
                    try:
                        self.audio_queue.put((audio_buffer, current_offset), timeout=1)
                        logger.debug(f"音声バッファをキューに追加: {len(audio_buffer)}サンプル, オフセット={current_offset:.2f}秒")
                    except queue.Full:
                        logger.warning("音声キューが満杯です")

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"音声処理エラー: {e}")

        logger.info("音声処理スレッド終了")

    def transcription_worker(self):
        """文字起こしワーカー (別スレッド)"""
        print("[文字起こしスレッド] 開始")
        logger.info("文字起こしスレッド開始")

        while self.is_running:
            try:
                # キューから音声データとオフセットを取得
                try:
                    audio_data, offset = self.audio_queue.get(timeout=1)
                except queue.Empty:
                    continue

                print(f"[文字起こしスレッド] 音声データ受信 (オフセット={offset:.2f}秒) - 処理開始")
                logger.info(f"文字起こし処理開始 (オフセット={offset:.2f}秒)...")

                # transcriberがNoneでないことを確認
                if self.transcriber is None:
                    print("[文字起こしスレッド] エラー: transcriberが初期化されていません")
                    logger.error("transcriber is None")
                    continue

                # 言語取得
                language = self.window.get_selected_language()
                print(f"[文字起こしスレッド] 言語: {language}")

                # 文字起こし実行
                result = self.transcriber.transcribe(audio_data, language)
                print(f"[文字起こしスレッド] 文字起こし完了")

                # セグメントのタイムスタンプにオフセットを追加
                for segment in result['segments']:
                    segment['start'] += offset
                    segment['end'] += offset

                # 結果をキューに追加
                self.result_queue.put(result)

                logger.info(f"文字起こし完了: {len(result['segments'])}セグメント")

            except Exception as e:
                print(f"[文字起こしスレッド] エラー: {e}")
                logger.error(f"文字起こしエラー: {e}", exc_info=True)
                import traceback
                traceback.print_exc()

        print("[文字起こしスレッド] 終了")
        logger.info("文字起こしスレッド終了")

    def update_audio_level(self):
        """音声レベル更新 (UIスレッド)"""
        if self.is_running:
            level = self.audio_capture.get_audio_level()
            self.window.update_audio_level(level)

    def _sync_ui_state(self):
        """UIの状態を定期的に同期（安全弁）"""
        try:
            # モデルロード結果が準備できていれば処理
            if self._load_result_ready:
                self._load_result_ready = False
                if self._load_result:
                    success, error, callback = self._load_result
                    self._load_result = None
                    print(f"[UIタイマー] モデルロード結果を処理: success={success}")
                    self._on_model_load_complete(success, error, callback)

            # モデル検証済みなのに開始ボタンが有効でない場合は有効化
            if getattr(self, "preload_verified", False) and not self.is_running:
                if not self.window.start_button.isEnabled():
                    self.window.start_button.setEnabled(True)
                # モデル状態表示が「ロード中」のままなら「検証済み」に更新
                # テキスト比較は厳密でなくてもよいが、ここでは簡易に
                current = self.window.model_status_label.text()
                if "ロード中" in current or "未ロード" in current:
                    self.window.update_model_status("検証済み", "green")
        except Exception:
            pass


    def check_transcription_results(self):
        """文字起こし結果チェック (UIスレッド)"""
        try:
            while not self.result_queue.empty():
                result = self.result_queue.get_nowait()

                # セグメントを追加（重複を防ぐ）
                new_segments = []
                for segment in result['segments']:
                    # 重複チェック: 同じテキストと時刻のセグメントを除外
                    is_duplicate = False
                    for existing in self.transcription_segments:
                        # テキストが同じで、時刻が1.0秒以内の差の場合は重複とみなす
                        if (existing['text'].strip() == segment['text'].strip() and
                            abs(existing['start'] - segment['start']) < 1.0):
                            is_duplicate = True
                            logger.debug(f"重複セグメントをスキップ: {segment['text'][:30]}...")
                            break

                    # さらに、今回追加する新規セグメント内でも重複チェック
                    for new_seg in new_segments:
                        if (new_seg['text'].strip() == segment['text'].strip() and
                            abs(new_seg['start'] - segment['start']) < 1.0):
                            is_duplicate = True
                            logger.debug(f"新規セグメント内で重複をスキップ: {segment['text'][:30]}...")
                            break

                    if not is_duplicate:
                        new_segments.append(segment)
                        self.transcription_segments.append(segment)

                # 新規セグメントをタイムスタンプ順にソートしてGUI表示
                new_segments.sort(key=lambda x: x['start'])
                for segment in new_segments:
                    # GUI更新
                    timestamp = self._format_timestamp(segment['start'])
                    self.window.add_transcription_text(segment['text'], timestamp)

        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"結果チェックエラー: {e}")

    def _format_timestamp(self, seconds: float) -> str:
        """タイムスタンプフォーマット - 実時刻を表示"""
        from datetime import datetime, timedelta

        if self.recording_start_time is None:
            # 録音開始時刻が未設定の場合は経過時間で表示
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"

        # 録音開始時刻 + 経過秒数 = 実時刻
        actual_time = self.recording_start_time + timedelta(seconds=seconds)
        return actual_time.strftime("%H:%M:%S")

    def save_file(self):
        """ファイル保存"""
        try:
            if not self.transcription_segments:
                self.window.show_warning("警告", "保存する内容がありません。")
                return

            # 保存先
            save_dir = self.window.get_save_directory()
            if save_dir:
                self.file_manager.base_directory = Path(save_dir)

            # 保存
            filepath = self.file_manager.auto_save(self.transcription_segments, "txt")

            if filepath:
                self.window.show_info("保存完了", f"ファイルを保存しました:\n{filepath}")
                logger.info(f"ファイル保存完了: {filepath}")
            else:
                self.window.show_error("保存エラー", "ファイルの保存に失敗しました。")

        except Exception as e:
            logger.error(f"ファイル保存エラー: {e}")
            self.window.show_error("保存エラー", f"ファイルの保存中にエラーが発生しました:\n{e}")

    def reset_text(self):
        """文字起こし結果をリセット"""
        try:
            # GUIのテキストエリアをクリア
            self.window.clear_transcription_text()

            # 内部の文字起こしデータをクリア
            self.transcription_segments = []

            # 成功メッセージ
            self.window.show_info("リセット完了", "文字起こし結果の履歴をクリアしました。")
            logger.info("文字起こし結果をリセット")

        except Exception as e:
            logger.error(f"リセットエラー: {e}")
            self.window.show_error("リセットエラー", f"リセット中にエラーが発生しました:\n{e}")

    def run(self):
        """アプリケーション実行"""
        print("   4. GUIセットアップ開始...")
        # GUIセットアップ
        self.setup_gui()

        # ウィンドウ表示
        print("   4-6. ウィンドウ表示...")
        self.window.show()
        print("        -> ウィンドウ表示OK")

        logger.info("アプリケーション起動完了")

        # ウィンドウ表示直後のフォールバック: ボタン状態強制同期
        def _post_show_sync():
            try:
                if getattr(self, "preload_verified", False) and not self.window.is_recording:
                    self.window.start_button.setEnabled(True)
                    self.window.stop_button.setEnabled(False)
            except Exception:
                pass
        QTimer.singleShot(0, _post_show_sync)
        QTimer.singleShot(1000, _post_show_sync)


def main():
    """メインエントリポイント"""
    try:
        print("=" * 60)
        print("OfflineVoiceLogger 起動開始")
        print("=" * 60)

        # ロガー設定
        print("1. ロガー初期化中...")
        setup_global_logger("INFO")
        logger = get_logger(__name__)
        logger.info("ロガー初期化完了")
        print("   -> ロガー初期化完了")

        # Qtアプリケーション
        print("2. PyQt5アプリケーション初期化中...")
        app = QApplication(sys.argv)
        logger.info("PyQt5アプリケーション初期化完了")
        print("   -> PyQt5アプリケーション初期化完了")

        # アプリケーション起動
        print("3. OfflineVoiceLoggerApp初期化中...")
        voice_logger = OfflineVoiceLoggerApp()
        logger.info("OfflineVoiceLoggerApp初期化完了")
        print("   -> OfflineVoiceLoggerApp初期化完了")

        print("4. GUI起動中...")
        voice_logger.run()
        logger.info("GUI起動完了")
        print("   -> GUI起動完了")

        print()
        print("アプリケーション起動成功！")
        print("=" * 60)

        # イベントループ
        sys.exit(app.exec_())

    except Exception as e:
        print()
        print("=" * 60)
        print("エラーが発生しました:")
        print("=" * 60)
        print(f"\nエラー内容: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("=" * 60)
        input("\nEnterキーを押して終了...")


if __name__ == "__main__":
    main()
