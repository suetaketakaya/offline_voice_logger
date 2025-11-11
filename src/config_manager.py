"""
OfflineVoiceLogger - 設定管理モジュール

config.iniファイルの読み書きと設定の永続化
- デフォルト設定の管理
- 設定の検証
- %APPDATA%への保存
"""

import configparser
import os
from pathlib import Path
from typing import Any, Dict, Tuple, List
from logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """設定ファイル(config.ini)の管理クラス"""

    # デフォルト設定
    DEFAULT_CONFIG = {
        'General': {
            'version': '1.0.0',
            'first_run': 'True',
            'language': 'ja'
        },
        'Audio': {
            'device_name': '',
            'sample_rate': '16000',
            'buffer_size_seconds': '10',
            'vad_threshold': '0.5'
        },
        'Transcription': {
            'model': 'medium',  # large-v3 または medium を選択
            'language': 'ja',
            'beam_size': '5',
            'vad_filter': 'True',
            'hallucination_threshold': '0.2'
        },
        'UI': {
            'window_width': '800',
            'window_height': '600',
            'window_x': '100',
            'window_y': '100',
            'font_size': '10',
            'theme': 'light',
            'auto_scroll': 'True'
        },
        'Files': {
            'save_directory': '',  # 初期化時に設定
            'file_name_template': 'transcript_{YYYYMMDD}_{HHMMSS}.txt',
            'auto_save_enabled': 'True',
            'auto_save_interval_minutes': '5',
            'encoding': 'utf-8'
        },
        'Storage': {
            'max_memory_usage_mb': '1024',
            'max_buffer_size_seconds': '30',
            'disk_warning_threshold_mb': '500',
            'disk_critical_threshold_mb': '100',
            'auto_cleanup_enabled': 'True',
            'max_backup_files': '10',
            'max_log_files': '5',
            'debug_audio_save_enabled': 'False'
        },
        'Advanced': {
            'log_level': 'INFO',
            'show_performance_monitor': 'False'
        }
    }

    def __init__(self, config_path: str = None):
        """
        Args:
            config_path (str): 設定ファイルパス (オプション)
                              デフォルト: %APPDATA%\OfflineVoiceLogger\config.ini
        """
        self.config = configparser.ConfigParser()

        # 設定ファイルパスの決定
        if config_path:
            self.config_path = Path(config_path)
        else:
            appdata_dir = os.getenv('APPDATA')
            if appdata_dir:
                config_dir = Path(appdata_dir) / 'OfflineVoiceLogger'
            else:
                config_dir = Path.cwd()

            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / 'config.ini'

        logger.info(f"設定ファイルパス: {self.config_path}")

        # 保存先ディレクトリのデフォルト値を設定
        self._set_default_save_directory()

    def _set_default_save_directory(self):
        """保存先ディレクトリのデフォルト値を設定"""
        documents_dir = Path.home() / 'Documents' / 'OfflineVoiceLogger'
        self.DEFAULT_CONFIG['Files']['save_directory'] = str(documents_dir)

    def load_config(self) -> Dict:
        """設定を読み込み

        Returns:
            Dict: 設定辞書
        """
        try:
            if self.config_path.exists():
                self.config.read(self.config_path, encoding='utf-8')
                logger.info(f"設定ファイルを読み込みました: {self.config_path}")

                # デフォルト値で不足している設定を補完
                self._merge_with_defaults()
            else:
                logger.info("設定ファイルが存在しないため、デフォルト設定を使用します")
                self._load_defaults()
                # 初回は設定ファイルを作成
                self.save_config()

            return self._config_to_dict()

        except Exception as e:
            logger.error(f"設定ファイルの読み込みに失敗: {e}")
            logger.info("デフォルト設定を使用します")
            self._load_defaults()
            return self._config_to_dict()

    def _load_defaults(self):
        """デフォルト設定をロード"""
        for section, options in self.DEFAULT_CONFIG.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)

    def _merge_with_defaults(self):
        """現在の設定とデフォルト設定をマージ"""
        for section, options in self.DEFAULT_CONFIG.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                if not self.config.has_option(section, key):
                    self.config.set(section, key, value)
                    logger.debug(f"デフォルト値を追加: [{section}] {key} = {value}")

    def save_config(self) -> bool:
        """設定を保存

        Returns:
            bool: 成功時True
        """
        try:
            # ディレクトリが存在しない場合は作成
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)

            logger.info(f"設定ファイルを保存しました: {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"設定ファイルの保存に失敗: {e}")
            return False

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """設定値を取得

        Args:
            section (str): セクション名
            key (str): キー名
            default (Any): デフォルト値

        Returns:
            Any: 設定値
        """
        try:
            if self.config.has_option(section, key):
                value = self.config.get(section, key)
                return value
            else:
                logger.debug(f"設定が見つかりません: [{section}] {key}, デフォルト値を使用: {default}")
                return default
        except Exception as e:
            logger.warning(f"設定の取得に失敗: [{section}] {key} - {e}")
            return default

    def get_int(self, section: str, key: str, default: int = 0) -> int:
        """整数値の設定を取得"""
        try:
            return self.config.getint(section, key)
        except:
            return default

    def get_float(self, section: str, key: str, default: float = 0.0) -> float:
        """浮動小数点値の設定を取得"""
        try:
            return self.config.getfloat(section, key)
        except:
            return default

    def get_bool(self, section: str, key: str, default: bool = False) -> bool:
        """真偽値の設定を取得"""
        try:
            return self.config.getboolean(section, key)
        except:
            return default

    def set(self, section: str, key: str, value: Any):
        """設定値を設定

        Args:
            section (str): セクション名
            key (str): キー名
            value (Any): 値
        """
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)

            self.config.set(section, key, str(value))
            logger.debug(f"設定を更新: [{section}] {key} = {value}")

        except Exception as e:
            logger.error(f"設定の更新に失敗: [{section}] {key} - {e}")

    def reset_to_default(self):
        """設定をデフォルトに戻す"""
        logger.info("設定をデフォルトに戻します")
        self.config.clear()
        self._load_defaults()
        self.save_config()

    def validate_config(self) -> Tuple[bool, List[str]]:
        """設定を検証

        Returns:
            Tuple[bool, List[str]]: (検証結果, エラーメッセージリスト)
        """
        errors = []

        try:
            # サンプリングレート検証
            sample_rate = self.get_int('Audio', 'sample_rate')
            if sample_rate not in [8000, 16000, 22050, 44100, 48000]:
                errors.append(f"無効なサンプリングレート: {sample_rate}")

            # バッファサイズ検証
            buffer_size = self.get_int('Audio', 'buffer_size_seconds')
            if buffer_size < 1 or buffer_size > 60:
                errors.append(f"バッファサイズは1-60秒の範囲で指定してください: {buffer_size}")

            # 言語検証
            language = self.get('Transcription', 'language')
            if language not in ['ja', 'en']:
                errors.append(f"サポートされていない言語: {language}")

            # モデル検証
            model = self.get('Transcription', 'model')
            if model not in ['tiny', 'base', 'small', 'medium', 'large-v3']:
                errors.append(f"サポートされていないモデル: {model}")

            # 保存先ディレクトリ検証
            save_dir = self.get('Files', 'save_directory')
            if save_dir:
                save_path = Path(save_dir)
                if not save_path.exists():
                    try:
                        save_path.mkdir(parents=True, exist_ok=True)
                        logger.info(f"保存先ディレクトリを作成しました: {save_dir}")
                    except Exception as e:
                        errors.append(f"保存先ディレクトリの作成に失敗: {save_dir} - {e}")

            # ウィンドウサイズ検証
            window_width = self.get_int('UI', 'window_width')
            window_height = self.get_int('UI', 'window_height')
            if window_width < 600 or window_height < 400:
                errors.append(f"ウィンドウサイズが小さすぎます: {window_width}x{window_height}")

        except Exception as e:
            logger.error(f"設定検証エラー: {e}")
            errors.append(f"設定検証中にエラーが発生しました: {e}")

        is_valid = len(errors) == 0
        if is_valid:
            logger.info("設定検証: 成功")
        else:
            logger.warning(f"設定検証: 失敗 ({len(errors)}個のエラー)")
            for error in errors:
                logger.warning(f"  - {error}")

        return is_valid, errors

    def _config_to_dict(self) -> Dict:
        """ConfigParserオブジェクトを辞書に変換

        Returns:
            Dict: 設定辞書
        """
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = dict(self.config.items(section))
        return config_dict

    def get_all_config(self) -> Dict:
        """全設定を辞書で取得

        Returns:
            Dict: 全設定
        """
        return self._config_to_dict()


# 使用例
if __name__ == "__main__":
    from logger import setup_global_logger
    setup_global_logger("DEBUG")

    # ConfigManagerのテスト
    config_mgr = ConfigManager()

    # 設定読み込み
    config = config_mgr.load_config()
    print("\n設定を読み込みました:")
    for section, options in config.items():
        print(f"[{section}]")
        for key, value in options.items():
            print(f"  {key} = {value}")

    # 設定の取得
    print(f"\n言語: {config_mgr.get('General', 'language')}")
    print(f"サンプリングレート: {config_mgr.get_int('Audio', 'sample_rate')}")
    print(f"自動保存有効: {config_mgr.get_bool('Files', 'auto_save_enabled')}")

    # 設定の変更
    config_mgr.set('General', 'language', 'en')
    config_mgr.set('Audio', 'buffer_size_seconds', '15')

    # 設定の検証
    is_valid, errors = config_mgr.validate_config()
    print(f"\n設定検証: {'成功' if is_valid else '失敗'}")
    if errors:
        print("エラー:")
        for error in errors:
            print(f"  - {error}")

    # 設定の保存
    if config_mgr.save_config():
        print(f"\n設定を保存しました: {config_mgr.config_path}")
