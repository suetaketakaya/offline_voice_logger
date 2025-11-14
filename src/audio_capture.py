"""
OfflineVoiceLogger - 音声キャプチャモジュール

Windowsループバック音声デバイスからのリアルタイム音声キャプチャ
- WASAPI経由でのシステム音声取得
- バッファリング管理
- デバイス再接続機能
"""

import sounddevice as sd
import numpy as np
import threading
import queue
import collections
from typing import List, Dict, Any, Optional
from logger import get_logger

logger = get_logger(__name__)


class DeviceNotFoundError(Exception):
    """音声デバイスが見つからない"""
    pass


class AudioCaptureError(Exception):
    """音声キャプチャエラー"""
    pass


class AudioCapture:
    """音声キャプチャクラス"""

    def __init__(self, sample_rate: int = 16000, channels: int = 1,
                 buffer_size_seconds: int = 10):
        """
        Args:
            sample_rate (int): サンプリングレート (16kHz推奨)
            channels (int): チャンネル数 (1=モノラル, 2=ステレオ)
            buffer_size_seconds (int): バッファサイズ (秒)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_size_seconds = buffer_size_seconds
        self.max_buffer_samples = sample_rate * buffer_size_seconds
        # 最小バッファサイズ（5秒）- これ以上貯まったら文字起こし開始
        self.min_buffer_samples = sample_rate * 5

        # 音声バッファ (dequeで効率的なFIFO)
        self.audio_buffer = collections.deque(maxlen=self.max_buffer_samples)
        self.buffer_lock = threading.Lock()

        # キャプチャ状態
        self.is_capturing = False
        self.capture_thread = None
        self.device_id = None
        self.stream = None

        # 音声レベル
        self.current_audio_level = 0.0
        self.audio_level_lock = threading.Lock()

        logger.info(f"AudioCapture初期化: {sample_rate}Hz, {channels}ch, バッファ{buffer_size_seconds}秒")

    def list_devices(self) -> List[Dict[str, Any]]:
        """利用可能な音声デバイスのリストを取得

        Returns:
            List[Dict]: デバイス情報のリスト
                - id: デバイスID
                - name: デバイス名
                - host_api: ホストAPI
                - max_input_channels: 最大入力チャンネル数
                - is_loopback: ループバックデバイスか (Windowsの場合)
        """
        try:
            devices = sd.query_devices()
            device_list = []

            for i, device in enumerate(devices):
                # 入力デバイスのみ
                if device['max_input_channels'] > 0:
                    device_info = {
                        'id': i,
                        'name': device['name'],
                        'host_api': sd.query_hostapis(device['hostapi'])['name'],
                        'max_input_channels': device['max_input_channels'],
                        'default_samplerate': device['default_samplerate']
                    }

                    # Windowsのループバックデバイス判定
                    # WASAPIの場合、"Stereo Mix"や"ステレオミキサー"などが該当
                    is_loopback = ('stereo mix' in device['name'].lower() or
                                   'ステレオミキサー' in device['name'].lower() or
                                   'loopback' in device['name'].lower() or
                                   'what u hear' in device['name'].lower())
                    device_info['is_loopback'] = is_loopback

                    # デバイスタイプを判定
                    if is_loopback:
                        device_info['device_type'] = 'system_audio'
                        device_info['type_display'] = 'スクリーンキャプチャー/システムオーディオ'
                    else:
                        device_info['device_type'] = 'microphone'
                        device_info['type_display'] = 'マイク'

                    device_list.append(device_info)
                    logger.debug(f"デバイス検出: {device_info}")

            logger.info(f"利用可能な入力デバイス: {len(device_list)}個")
            return device_list

        except Exception as e:
            logger.error(f"デバイスリスト取得エラー: {e}")
            raise AudioCaptureError(f"デバイスリスト取得に失敗しました: {e}")

    def find_loopback_device(self) -> Optional[int]:
        """ループバックデバイスを自動検出

        Returns:
            Optional[int]: デバイスID (見つからない場合はNone)
        """
        try:
            devices = self.list_devices()
            loopback_devices = [d for d in devices if d.get('is_loopback', False)]

            if loopback_devices:
                # 最初に見つかったループバックデバイスを返す
                device_id = loopback_devices[0]['id']
                device_name = loopback_devices[0]['name']
                logger.info(f"ループバックデバイスを検出: {device_name} (ID: {device_id})")
                return device_id
            else:
                logger.warning("ループバックデバイスが見つかりませんでした")
                return None

        except Exception as e:
            logger.error(f"ループバックデバイス検出エラー: {e}")
            return None

    def start_capture(self, device_id: int = None) -> bool:
        """音声キャプチャを開始

        Args:
            device_id (int): 使用するデバイスID (Noneの場合は自動検出)

        Returns:
            bool: 成功時True

        Raises:
            DeviceNotFoundError: デバイスが見つからない場合
            AudioCaptureError: キャプチャ開始に失敗した場合
        """
        try:
            # デバイスID自動検出
            if device_id is None:
                device_id = self.find_loopback_device()
                if device_id is None:
                    raise DeviceNotFoundError(
                        "ループバックデバイスが見つかりません。\n"
                        "Windowsの設定でステレオミキサーを有効にしてください。"
                    )

            self.device_id = device_id

            # デバイス情報を取得
            device_info = sd.query_devices(device_id)
            logger.info(f"音声キャプチャ開始: {device_info['name']}")

            # バッファをクリア
            with self.buffer_lock:
                self.audio_buffer.clear()

            # ストリーム開始
            self.is_capturing = True
            self.stream = sd.InputStream(
                device=device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._audio_callback,
                dtype='float32'
            )
            self.stream.start()

            logger.info("音声キャプチャを開始しました")
            return True

        except DeviceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"音声キャプチャ開始エラー: {e}")
            self.is_capturing = False
            raise AudioCaptureError(f"音声キャプチャの開始に失敗しました: {e}")

    def _audio_callback(self, indata, frames, time_info, status):
        """音声データのコールバック (別スレッドで実行)

        Args:
            indata: 入力音声データ
            frames: フレーム数
            time_info: タイム情報
            status: ステータス
        """
        if status:
            logger.warning(f"音声キャプチャステータス: {status}")

        try:
            # ステレオの場合はモノラルに変換
            if self.channels == 1 and indata.shape[1] > 1:
                audio_data = np.mean(indata, axis=1)
            else:
                audio_data = indata[:, 0]

            # バッファに追加
            with self.buffer_lock:
                self.audio_buffer.extend(audio_data)

            # 音声レベルを計算 (RMS)
            rms = np.sqrt(np.mean(audio_data**2))
            with self.audio_level_lock:
                self.current_audio_level = min(rms * 10, 1.0)  # 0.0-1.0に正規化

        except Exception as e:
            logger.error(f"音声コールバックエラー: {e}")

    def stop_capture(self):
        """音声キャプチャを停止"""
        try:
            self.is_capturing = False

            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            logger.info("音声キャプチャを停止しました")

        except Exception as e:
            logger.error(f"音声キャプチャ停止エラー: {e}")

    def get_audio_buffer(self) -> Optional[np.ndarray]:
        """文字起こし用の音声バッファを取得

        Returns:
            np.ndarray or None: 音声データ (最小5秒以上)
                                バッファが最小サイズ未満の場合はNone
        """
        with self.buffer_lock:
            # 最小バッファサイズ（5秒）以上貯まったら取得
            if len(self.audio_buffer) >= self.min_buffer_samples:
                # バッファから取得
                audio_data = np.array(list(self.audio_buffer))

                # バッファをクリア
                self.audio_buffer.clear()

                logger.debug(f"音声バッファ取得: {len(audio_data)}サンプル ({len(audio_data)/self.sample_rate:.2f}秒)")
                return audio_data
            else:
                return None

    def get_audio_level(self) -> float:
        """現在の音声レベルを取得 (0.0～1.0)

        Returns:
            float: 音声レベル
        """
        with self.audio_level_lock:
            return self.current_audio_level

    def get_buffer_fill_percentage(self) -> float:
        """バッファの充填率を取得

        Returns:
            float: 充填率 (0.0～1.0)
        """
        with self.buffer_lock:
            return len(self.audio_buffer) / self.max_buffer_samples

    def clear_buffer(self):
        """バッファをクリア"""
        with self.buffer_lock:
            self.audio_buffer.clear()
            logger.debug("音声バッファをクリアしました")

    def is_device_connected(self) -> bool:
        """デバイスが接続されているかチェック

        Returns:
            bool: 接続されている場合True
        """
        if self.device_id is None:
            return False

        try:
            device_info = sd.query_devices(self.device_id)
            return device_info is not None
        except:
            return False


# 使用例
if __name__ == "__main__":
    from logger import setup_global_logger
    import time

    setup_global_logger("DEBUG")

    # AudioCaptureのテスト
    audio = AudioCapture(sample_rate=16000, channels=1, buffer_size_seconds=5)

    # デバイスリスト表示
    print("\n利用可能なデバイス:")
    devices = audio.list_devices()
    for i, device in enumerate(devices):
        loopback = " [ループバック]" if device['is_loopback'] else ""
        print(f"{i+1}. {device['name']}{loopback}")

    # キャプチャ開始 (自動検出)
    try:
        audio.start_capture()
        print("\n音声キャプチャ開始... (10秒間)")

        for i in range(10):
            time.sleep(1)
            level = audio.get_audio_level()
            fill = audio.get_buffer_fill_percentage()
            print(f"[{i+1}秒] 音声レベル: {level:.2f}, バッファ充填率: {fill:.1%}")

            # バッファが満杯になったら取得
            buffer = audio.get_audio_buffer()
            if buffer is not None:
                print(f"  -> バッファ取得: {len(buffer)}サンプル ({len(buffer)/16000:.2f}秒)")

        audio.stop_capture()
        print("\n音声キャプチャ停止")

    except Exception as e:
        print(f"\nエラー: {e}")
        audio.stop_capture()
