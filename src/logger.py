"""
OfflineVoiceLogger - ロギングモジュール

完全ローカル環境でのログ管理
- ファイルへのログ出力 (外部送信なし)
- ログローテーション (10MB x 5ファイル)
- レベル別ロギング (DEBUG, INFO, WARNING, ERROR, CRITICAL)
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


class LocalLogger:
    """ローカルファイルのみにログを記録するロガー"""

    def __init__(self, name: str = "OfflineVoiceLogger", log_level: str = "INFO"):
        """
        Args:
            name (str): ロガー名
            log_level (str): ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = None
        self.log_dir = None
        self.log_file = None

    def setup(self):
        """ロガーのセットアップ"""
        # ログディレクトリの作成
        appdata_dir = os.getenv('APPDATA')
        if appdata_dir:
            self.log_dir = Path(appdata_dir) / 'OfflineVoiceLogger' / 'logs'
        else:
            # APPDATAが取得できない場合はカレントディレクトリに
            self.log_dir = Path.cwd() / 'logs'

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / 'app.log'

        # ロガーの作成
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)

        # 既存のハンドラをクリア
        if self.logger.handlers:
            self.logger.handlers.clear()

        # ログフォーマット
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # ファイルハンドラ (ローテーション付き)
        # maxBytes: 10MB, backupCount: 5 (最大5ファイル保持)
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # コンソールハンドラ (デバッグ用)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # 警告以上のみコンソール出力
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 初期ログ
        self.logger.info("=" * 60)
        self.logger.info(f"OfflineVoiceLogger ロギング開始: {datetime.now()}")
        self.logger.info(f"ログファイル: {self.log_file}")
        self.logger.info(f"ログレベル: {logging.getLevelName(self.log_level)}")
        self.logger.info("=" * 60)

        return self.logger

    def get_logger(self):
        """ロガーインスタンスを取得"""
        if self.logger is None:
            self.setup()
        return self.logger

    def cleanup_old_logs(self, max_log_files: int = 5):
        """古いログファイルを削除

        Args:
            max_log_files (int): 保持する最大ログファイル数
        """
        if not self.log_dir:
            return

        try:
            log_files = sorted(
                self.log_dir.glob('app.log*'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # 最大ファイル数を超えたものを削除
            for log_file in log_files[max_log_files:]:
                try:
                    log_file.unlink()
                    if self.logger:
                        self.logger.info(f"古いログファイルを削除: {log_file.name}")
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"ログファイル削除失敗: {log_file.name} - {e}")

        except Exception as e:
            if self.logger:
                self.logger.error(f"ログファイルクリーンアップエラー: {e}")

    def get_log_file_path(self) -> str:
        """ログファイルパスを取得"""
        return str(self.log_file) if self.log_file else ""

    def get_log_directory(self) -> str:
        """ログディレクトリパスを取得"""
        return str(self.log_dir) if self.log_dir else ""


# グローバルロガーインスタンス
_global_logger_instance = None


def setup_global_logger(log_level: str = "INFO"):
    """グローバルロガーのセットアップ

    Args:
        log_level (str): ログレベル

    Returns:
        logging.Logger: ロガーインスタンス
    """
    global _global_logger_instance

    if _global_logger_instance is None:
        _global_logger_instance = LocalLogger(log_level=log_level)
        _global_logger_instance.setup()
        _global_logger_instance.cleanup_old_logs()

    return _global_logger_instance.get_logger()


def get_logger(name: str = None):
    """ロガーを取得

    Args:
        name (str): ロガー名 (オプション)

    Returns:
        logging.Logger: ロガーインスタンス
    """
    global _global_logger_instance

    if _global_logger_instance is None:
        setup_global_logger()

    if name:
        return logging.getLogger(name)
    else:
        return _global_logger_instance.get_logger()


# 使用例
if __name__ == "__main__":
    # ロガーのテスト
    logger = setup_global_logger("DEBUG")

    logger.debug("これはDEBUGメッセージです")
    logger.info("これはINFOメッセージです")
    logger.warning("これはWARNINGメッセージです")
    logger.error("これはERRORメッセージです")
    logger.critical("これはCRITICALメッセージです")

    # ログファイルパスの表示
    local_logger = _global_logger_instance
    print(f"\nログファイル: {local_logger.get_log_file_path()}")
    print(f"ログディレクトリ: {local_logger.get_log_directory()}")
