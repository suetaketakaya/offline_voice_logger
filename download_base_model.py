"""
faster-whisper baseモデルのダウンロードスクリプト
最も軽量で高速（日本語でも実用的）
"""

import os
import sys
from pathlib import Path

# UTF-8出力設定
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def download_base_model():
    """faster-whisper base モデルをダウンロード"""

    print("=" * 60)
    print("faster-whisper base モデル自動ダウンロード")
    print("=" * 60)
    print()
    print("baseモデルの特徴:")
    print("  - サイズ: 約290MB (最軽量)")
    print("  - メモリ: 約1-2GB")
    print("  - ロード時間: 10-30秒")
    print("  - 精度: 基本的な文字起こしには十分")
    print()

    # faster-whisperのインポート確認
    try:
        from faster_whisper import WhisperModel
        print("[OK] faster-whisper がインストールされています")
    except ImportError:
        print("[ERROR] faster-whisper がインストールされていません")
        return False

    # モデル保存先
    models_dir = Path(__file__).parent / 'models'
    model_dir = models_dir / 'base'

    print(f"\nモデル保存先: {model_dir}")
    print()

    # ディレクトリ作成
    models_dir.mkdir(exist_ok=True)

    print("ダウンロード開始...")
    print("=" * 60)
    print()

    try:
        print("モデルをダウンロード中...")
        print()

        model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8",
            download_root=str(models_dir),
            num_workers=1
        )

        print()
        print("=" * 60)
        print("[SUCCESS] ダウンロード完了!")
        print("=" * 60)
        print()

        # Hugging Faceキャッシュからbaseディレクトリにコピー
        hf_cache_path = models_dir / 'models--Systran--faster-whisper-base' / 'snapshots'
        if hf_cache_path.exists():
            snapshot_dirs = list(hf_cache_path.glob('*'))
            if snapshot_dirs:
                import shutil
                source_dir = snapshot_dirs[0]
                if model_dir.exists():
                    shutil.rmtree(model_dir)
                shutil.copytree(source_dir, model_dir)
                print(f"モデルファイルをコピー: {model_dir}")

        if model_dir.exists():
            files = list(model_dir.glob("*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            total_size_mb = total_size / (1024 * 1024)
            print(f"合計サイズ: {total_size_mb:.0f} MB")

        print()
        print("設定を自動更新しています...")

        # 設定ファイルを自動更新
        import configparser
        config_path = Path(os.getenv('APPDATA')) / 'OfflineVoiceLogger' / 'config.ini'
        if config_path.exists():
            config = configparser.ConfigParser()
            config.read(config_path, encoding='utf-8')
            config.set('Transcription', 'model', 'base')
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
            print("[OK] 設定を base モデルに更新しました")
        else:
            print("[WARNING] 設定ファイルが見つかりません")

        print()
        print("=" * 60)
        print("セットアップ完了！")
        print("=" * 60)
        print()
        print("次のステップ:")
        print("1. cd src")
        print("2. python main.py")
        print("3. 録音開始ボタンをクリック")
        print()
        print("baseモデルは10-30秒でロードが完了します！")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 60)
        print("[ERROR] エラーが発生しました")
        print("=" * 60)
        print()
        print(f"エラー内容: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    success = download_base_model()
    sys.exit(0 if success else 1)
