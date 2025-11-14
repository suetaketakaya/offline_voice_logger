"""
OfflineVoiceLogger - 文字起こしモジュール

faster-whisperを使用した音声→テキスト変換
- 完全オフライン動作 (ローカルモデルのみ使用)
- 日本語/英語対応
- VADフィルター適用
- ハルシネーション抑制
"""

import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from logger import get_logger

logger = get_logger(__name__)


class ModelNotFoundError(Exception):
    """モデルファイルが見つからない"""
    pass


class ModelLoadError(Exception):
    """モデルロードエラー"""
    pass


class TranscriptionError(Exception):
    """文字起こしエラー"""
    pass


class Transcriber:
    """文字起こしクラス (faster-whisper使用)"""

    # サポートされている言語
    SUPPORTED_LANGUAGES = ['ja', 'en']

    # サポートされているモデル
    SUPPORTED_MODELS = ['tiny', 'base', 'small', 'medium', 'large-v3']

    def __init__(self, model_path: str, device: str = "cpu",
                 compute_type: str = "int8", language: str = "ja",
                 cpu_threads: int = None, num_workers: int = 1):
        """
        Args:
            model_path (str): ローカルモデルパス
            device (str): "cpu" or "cuda"
            compute_type (str): "int8", "float16", "float32"
            language (str): "ja" or "en"
        """
        self.model_path = Path(model_path)
        self.device = device
        self.compute_type = compute_type
        self.language = language if language in self.SUPPORTED_LANGUAGES else "ja"
        # リソース制御
        self.cpu_threads = cpu_threads
        self.num_workers = num_workers

        self.model = None
        self.model_loaded = False

        # VAD設定
        self.vad_parameters = {
            'threshold': 0.5,
            'min_speech_duration_ms': 250,
            'min_silence_duration_ms': 2000
        }

        logger.info(f"Transcriber初期化: モデル={model_path}, デバイス={device}, 言語={self.language}")

    def load_model(self) -> bool:
        """モデルをロード

        Returns:
            bool: 成功時True

        Raises:
            ModelNotFoundError: モデルが見つからない場合
            ModelLoadError: モデルロードに失敗した場合
        """
        try:
            # モデルパスの検証
            if not self.model_path.exists():
                raise ModelNotFoundError(
                    f"モデルファイルが見つかりません: {self.model_path}\n"
                    f"models/ディレクトリにfaster-whisperモデルを配置してください。"
                )

            logger.info(f"モデルロード開始: {self.model_path}")

            # faster-whisperのインポート (遅延インポート)
            try:
                from faster_whisper import WhisperModel
            except ImportError as e:
                raise ModelLoadError(
                    f"faster-whisperのインポートに失敗しました: {e}\n"
                    f"pip install faster-whisper を実行してください。"
                )

            # 環境変数でネットワーク無効化 (完全オフライン動作)
            print("[Transcriber] 環境変数設定...")
            os.environ['no_proxy'] = '*'
            os.environ['NO_PROXY'] = '*'
            os.environ['http_proxy'] = ''
            os.environ['https_proxy'] = ''
            os.environ['HTTP_PROXY'] = ''
            os.environ['HTTPS_PROXY'] = ''

            # モデルロード (完全オフライン)
            print(f"[Transcriber] WhisperModel初期化開始...")
            print(f"  - モデルパス: {self.model_path}")
            print(f"  - デバイス: {self.device}")
            print(f"  - compute_type: {self.compute_type}")
            print(f"  これには数分かかる場合があります...")

            whisper_kwargs = {
                "model_size_or_path": str(self.model_path),
                "device": self.device,
                "compute_type": self.compute_type,
                "download_root": None,   # ダウンロード無効化
                "local_files_only": True # ローカルのみ
            }
            # スレッド数は指定しない（デフォルトに任せる）
            # cpu_threadsやnum_workersを設定すると初期化が遅くなる場合がある

            self.model = WhisperModel(**whisper_kwargs)

            print("[Transcriber] WhisperModel初期化完了!")
            self.model_loaded = True
            logger.info("モデルロード完了")
            return True

        except ModelNotFoundError:
            raise
        except Exception as e:
            logger.error(f"モデルロードエラー: {e}")
            self.model_loaded = False
            raise ModelLoadError(f"モデルのロードに失敗しました: {e}")

    def transcribe(self, audio_data: np.ndarray, language: str = None) -> Dict:
        """音声データを文字起こし

        Args:
            audio_data (np.ndarray): 音声データ (16kHz, モノラル)
            language (str): "ja" or "en" (Noneの場合はデフォルト言語を使用)

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
        if not self.model_loaded or self.model is None:
            raise TranscriptionError("モデルがロードされていません。先にload_model()を実行してください。")

        if language is None:
            language = self.language

        if language not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"サポートされていない言語: {language}, デフォルト({self.language})を使用します")
            language = self.language

        try:
            logger.info(f"文字起こし開始: 言語={language}, データ長={len(audio_data)}サンプル")

            # 音声データの正規化 (float32, -1.0～1.0の範囲)
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # 音声データの長さチェック
            duration = len(audio_data) / 16000  # 16kHzを仮定
            if duration < 0.1:
                logger.warning("音声データが短すぎます (< 0.1秒)")
                return {
                    "segments": [],
                    "language": language,
                    "duration": duration
                }

            # faster-whisperで文字起こし
            # VADフィルターを無効化（onnxruntimeのDLL問題を回避）
            # 精度向上のためのパラメータ設定

            # 言語に応じたinitial_promptを設定（認識精度向上）
            # 注意: プロンプトは指示文ではなく、自然な文章例を使用してハルシネーションを防ぐ
            if language == 'ja':
                initial_prompt = "今日は良い天気ですね。会議は10時から始まります。"
            else:
                initial_prompt = "Hello, how are you today? The meeting starts at ten."

            transcribe_params = {
                'language': language,
                'vad_filter': False,  # VADフィルター無効
                'beam_size': 5,  # ビームサイズ（デフォルト: 5）
                'best_of': 5,  # 5つの候補から最良のものを選択
                'temperature': 0.0,  # 確定的な認識（ハルシネーション抑制）
                'condition_on_previous_text': True,  # 前のテキストを条件として使用
                'compression_ratio_threshold': 2.4,  # ハルシネーション検出の閾値
                'log_prob_threshold': -1.0,  # 低確率セグメントの閾値
                'no_speech_threshold': 0.6,  # 無音判定の閾値
                'initial_prompt': initial_prompt,  # 言語コンテキストを提供（自然な文章例）
                'word_timestamps': False,  # 単語レベルのタイムスタンプは不要
            }

            segments, info = self.model.transcribe(audio_data, **transcribe_params)

            # セグメントを処理
            result_segments = []
            for i, segment in enumerate(segments):
                segment_dict = {
                    "id": i + 1,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "confidence": segment.avg_logprob if hasattr(segment, 'avg_logprob') else 0.0
                }
                result_segments.append(segment_dict)
                logger.debug(f"セグメント {i+1}: [{segment.start:.2f}-{segment.end:.2f}] {segment.text.strip()}")

            # セグメントをマージして自然な文の区切りにする
            result_segments = self._merge_segments(result_segments, language)

            result = {
                "segments": result_segments,
                "language": info.language if hasattr(info, 'language') else language,
                "duration": duration
            }

            logger.info(f"文字起こし完了: {len(result_segments)}セグメント, {duration:.2f}秒")
            return result

        except Exception as e:
            logger.error(f"文字起こしエラー: {e}")
            raise TranscriptionError(f"文字起こしに失敗しました: {e}")

    def set_language(self, language: str):
        """言語設定を変更

        Args:
            language (str): "ja" or "en"
        """
        if language in self.SUPPORTED_LANGUAGES:
            self.language = language
            logger.info(f"言語を変更: {language}")
        else:
            logger.warning(f"サポートされていない言語: {language}")

    def set_vad_parameters(self, threshold: float = None,
                           min_speech_duration_ms: int = None,
                           min_silence_duration_ms: int = None):
        """VADパラメータを設定

        Args:
            threshold (float): VADしきい値 (0.0-1.0)
            min_speech_duration_ms (int): 最小音声継続時間 (ミリ秒)
            min_silence_duration_ms (int): 最小無音継続時間 (ミリ秒)
        """
        if threshold is not None:
            self.vad_parameters['threshold'] = threshold
        if min_speech_duration_ms is not None:
            self.vad_parameters['min_speech_duration_ms'] = min_speech_duration_ms
        if min_silence_duration_ms is not None:
            self.vad_parameters['min_silence_duration_ms'] = min_silence_duration_ms

        logger.info(f"VADパラメータ更新: {self.vad_parameters}")

    def _merge_segments(self, segments: List[Dict], language: str) -> List[Dict]:
        """セグメントをマージして自然な文の区切りにする

        Args:
            segments (List[Dict]): セグメントのリスト
            language (str): 言語コード

        Returns:
            List[Dict]: マージされたセグメントのリスト
        """
        if not segments:
            return segments

        # 文末記号を定義
        if language == 'ja':
            sentence_endings = ('。', '！', '？', '!', '?', '.', '．')
        else:
            sentence_endings = ('.', '!', '?')

        merged = []
        current = None

        for segment in segments:
            text = segment['text'].strip()
            if not text:
                continue

            if current is None:
                # 最初のセグメント
                current = segment.copy()
            else:
                # 前のセグメントとの時間差をチェック
                time_gap = segment['start'] - current['end']
                prev_text = current['text'].rstrip()

                # 以下の条件でマージ：
                # 1. 時間差が1.0秒以内
                # 2. 前のテキストが文末記号で終わっていない
                # 3. 前のテキストが短すぎる（10文字未満）場合も積極的にマージ
                should_merge = (
                    time_gap < 1.0 and
                    (not prev_text or not prev_text[-1] in sentence_endings or len(prev_text) < 10)
                )

                if should_merge:
                    # マージ：テキストを結合し、終了時刻を更新
                    current['text'] = prev_text + ' ' + text if language == 'en' else prev_text + text
                    current['end'] = segment['end']
                    # 信頼度は平均を取る
                    current['confidence'] = (current['confidence'] + segment['confidence']) / 2
                    logger.debug(f"セグメントマージ: [{current['start']:.2f}-{current['end']:.2f}] {current['text']}")
                else:
                    # マージしない：現在のセグメントを保存して新しいセグメントを開始
                    merged.append(current)
                    current = segment.copy()

        # 最後のセグメントを追加
        if current is not None:
            merged.append(current)

        # IDを再割り当て
        for i, seg in enumerate(merged):
            seg['id'] = i + 1

        logger.info(f"セグメントマージ完了: {len(segments)} → {len(merged)}セグメント")
        return merged

    def get_supported_languages(self) -> List[str]:
        """サポートされている言語のリストを取得

        Returns:
            List[str]: 言語コードのリスト
        """
        return self.SUPPORTED_LANGUAGES.copy()

    def is_model_loaded(self) -> bool:
        """モデルがロードされているかチェック

        Returns:
            bool: ロード済みの場合True
        """
        return self.model_loaded


# 使用例
if __name__ == "__main__":
    from logger import setup_global_logger
    import time

    setup_global_logger("DEBUG")

    # モデルパスの設定
    model_path = Path.cwd().parent / 'models' / 'large-v3'

    if not model_path.exists():
        print(f"\nエラー: モデルが見つかりません: {model_path}")
        print("models/large-v3/ ディレクトリにfaster-whisperモデルを配置してください。")
    else:
        try:
            # Transcriberのテスト
            transcriber = Transcriber(
                model_path=str(model_path),
                device="cpu",
                compute_type="int8",
                language="ja"
            )

            # モデルロード
            print("\nモデルをロード中...")
            start_time = time.time()
            transcriber.load_model()
            load_time = time.time() - start_time
            print(f"モデルロード完了 ({load_time:.2f}秒)")

            # テスト用の音声データ (無音)
            print("\nテスト用の無音データで文字起こし...")
            test_audio = np.zeros(16000 * 5, dtype=np.float32)  # 5秒の無音

            result = transcriber.transcribe(test_audio)
            print(f"\n結果:")
            print(f"  言語: {result['language']}")
            print(f"  期間: {result['duration']:.2f}秒")
            print(f"  セグメント数: {len(result['segments'])}")

            for segment in result['segments']:
                print(f"  [{segment['start']:.2f}-{segment['end']:.2f}] {segment['text']}")

        except Exception as e:
            print(f"\nエラー: {e}")
