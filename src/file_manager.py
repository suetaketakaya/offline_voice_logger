"""
OfflineVoiceLogger - ファイル管理モジュール

文字起こし結果のファイル保存・管理
- TXT/SRT/JSON形式でのエクスポート
- 自動保存
- バックアップ管理
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """ファイル管理クラス"""

    def __init__(self, base_directory: str = None):
        """
        Args:
            base_directory (str): ベースディレクトリ
                                 デフォルト: %USERPROFILE%/Documents/OfflineVoiceLogger
        """
        if base_directory:
            self.base_directory = Path(base_directory)
        else:
            self.base_directory = Path.home() / 'Documents' / 'OfflineVoiceLogger'

        # ディレクトリ作成
        self.base_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"FileManager初期化: {self.base_directory}")

        # バックアップディレクトリ
        self.backup_directory = self._get_backup_directory()
        self.backup_directory.mkdir(parents=True, exist_ok=True)

    def _get_backup_directory(self) -> Path:
        """バックアップディレクトリを取得"""
        appdata_dir = os.getenv('APPDATA')
        if appdata_dir:
            backup_dir = Path(appdata_dir) / 'OfflineVoiceLogger' / 'backup'
        else:
            backup_dir = self.base_directory / 'backup'
        return backup_dir

    def _format_timestamp(self, seconds: float) -> str:
        """秒数をタイムスタンプ文字列に変換

        Args:
            seconds (float): 秒数

        Returns:
            str: タイムスタンプ (HH:MM:SS)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _format_srt_timestamp(self, seconds: float) -> str:
        """秒数をSRT形式のタイムスタンプに変換

        Args:
            seconds (float): 秒数

        Returns:
            str: SRTタイムスタンプ (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    def save_as_text(self, segments: List[Dict], filepath: str = None,
                     encoding: str = "utf-8") -> bool:
        """TXT形式で保存

        Args:
            segments (List[Dict]): 文字起こしセグメント
            filepath (str): 保存先パス (Noneの場合は自動生成)
            encoding (str): エンコーディング

        Returns:
            bool: 成功時True
        """
        try:
            # ファイルパス自動生成
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"transcript_{timestamp}.txt"
                filepath = self.base_directory / filename

            filepath = Path(filepath)

            # 親ディレクトリ作成
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # TXT形式で保存
            with open(filepath, 'w', encoding=encoding) as f:
                for segment in segments:
                    timestamp = self._format_timestamp(segment['start'])
                    text = segment['text']
                    f.write(f"[{timestamp}] {text}\n")

            logger.info(f"TXTファイル保存完了: {filepath}")
            return True

        except Exception as e:
            logger.error(f"TXTファイル保存エラー: {e}")
            return False

    def save_as_srt(self, segments: List[Dict], filepath: str = None) -> bool:
        """SRT字幕形式で保存

        Args:
            segments (List[Dict]): 文字起こしセグメント
            filepath (str): 保存先パス (Noneの場合は自動生成)

        Returns:
            bool: 成功時True
        """
        try:
            # ファイルパス自動生成
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"transcript_{timestamp}.srt"
                filepath = self.base_directory / filename

            filepath = Path(filepath)

            # 親ディレクトリ作成
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # SRT形式で保存
            with open(filepath, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments, 1):
                    start = self._format_srt_timestamp(segment['start'])
                    end = self._format_srt_timestamp(segment['end'])
                    text = segment['text']

                    f.write(f"{i}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{text}\n\n")

            logger.info(f"SRTファイル保存完了: {filepath}")
            return True

        except Exception as e:
            logger.error(f"SRTファイル保存エラー: {e}")
            return False

    def save_as_json(self, data: Dict, filepath: str = None) -> bool:
        """JSON形式で保存

        Args:
            data (Dict): 保存するデータ
            filepath (str): 保存先パス (Noneの場合は自動生成)

        Returns:
            bool: 成功時True
        """
        try:
            # ファイルパス自動生成
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"transcript_{timestamp}.json"
                filepath = self.base_directory / filename

            filepath = Path(filepath)

            # 親ディレクトリ作成
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # JSON形式で保存
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"JSONファイル保存完了: {filepath}")
            return True

        except Exception as e:
            logger.error(f"JSONファイル保存エラー: {e}")
            return False

    def auto_save(self, segments: List[Dict], format: str = "txt") -> Optional[str]:
        """自動保存

        Args:
            segments (List[Dict]): 文字起こしセグメント
            format (str): ファイル形式 ("txt", "srt", "json")

        Returns:
            Optional[str]: 保存したファイルパス (失敗時はNone)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{timestamp}.{format}"
            filepath = self.base_directory / filename

            if format == "txt":
                success = self.save_as_text(segments, str(filepath))
            elif format == "srt":
                success = self.save_as_srt(segments, str(filepath))
            elif format == "json":
                data = {
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "version": "1.0.0"
                    },
                    "segments": segments
                }
                success = self.save_as_json(data, str(filepath))
            else:
                logger.error(f"サポートされていない形式: {format}")
                return None

            if success:
                logger.info(f"自動保存完了: {filepath}")
                return str(filepath)
            else:
                return None

        except Exception as e:
            logger.error(f"自動保存エラー: {e}")
            return None

    def create_backup(self, filepath: str) -> Optional[str]:
        """バックアップファイルを作成

        Args:
            filepath (str): バックアップ元ファイルパス

        Returns:
            Optional[str]: バックアップファイルパス (失敗時はNone)
        """
        try:
            filepath = Path(filepath)

            if not filepath.exists():
                logger.warning(f"バックアップ元ファイルが存在しません: {filepath}")
                return None

            # バックアップファイル名生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{filepath.stem}_backup_{timestamp}{filepath.suffix}"
            backup_filepath = self.backup_directory / backup_filename

            # ファイルコピー
            shutil.copy2(filepath, backup_filepath)

            logger.info(f"バックアップ作成完了: {backup_filepath}")
            return str(backup_filepath)

        except Exception as e:
            logger.error(f"バックアップ作成エラー: {e}")
            return None

    def cleanup_old_backups(self, max_backups: int = 10):
        """古いバックアップを削除

        Args:
            max_backups (int): 保持する最大バックアップ数
        """
        try:
            # バックアップファイル一覧取得 (更新日時でソート)
            backup_files = sorted(
                self.backup_directory.glob('*_backup_*'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # 最大数を超えたものを削除
            for backup_file in backup_files[max_backups:]:
                try:
                    backup_file.unlink()
                    logger.info(f"古いバックアップを削除: {backup_file.name}")
                except Exception as e:
                    logger.warning(f"バックアップ削除失敗: {backup_file.name} - {e}")

            logger.info(f"バックアップクリーンアップ完了 (保持数: {max_backups})")

        except Exception as e:
            logger.error(f"バックアップクリーンアップエラー: {e}")

    def get_recent_files(self, count: int = 10, extension: str = None) -> List[str]:
        """最近のファイルリストを取得

        Args:
            count (int): 取得する最大ファイル数
            extension (str): 拡張子フィルタ (例: ".txt")

        Returns:
            List[str]: ファイルパスのリスト
        """
        try:
            # ファイル一覧取得
            if extension:
                files = list(self.base_directory.glob(f'*{extension}'))
            else:
                files = list(self.base_directory.glob('*'))

            # 更新日時でソート
            files = sorted(
                [f for f in files if f.is_file()],
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # 指定数まで取得
            recent_files = [str(f) for f in files[:count]]

            logger.debug(f"最近のファイル: {len(recent_files)}件")
            return recent_files

        except Exception as e:
            logger.error(f"最近のファイル取得エラー: {e}")
            return []


# 使用例
if __name__ == "__main__":
    from logger import setup_global_logger

    setup_global_logger("DEBUG")

    # FileManagerのテスト
    file_mgr = FileManager()

    # テストデータ
    test_segments = [
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
    ]

    # TXT保存
    print("\nTXT形式で保存...")
    file_mgr.save_as_text(test_segments)

    # SRT保存
    print("SRT形式で保存...")
    file_mgr.save_as_srt(test_segments)

    # JSON保存
    print("JSON形式で保存...")
    test_data = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        },
        "segments": test_segments
    }
    file_mgr.save_as_json(test_data)

    # 最近のファイル
    print("\n最近のファイル:")
    recent_files = file_mgr.get_recent_files(5)
    for i, filepath in enumerate(recent_files, 1):
        print(f"{i}. {Path(filepath).name}")

    # バックアップクリーンアップ
    print("\nバックアップクリーンアップ...")
    file_mgr.cleanup_old_backups(10)

    print(f"\n保存先: {file_mgr.base_directory}")
