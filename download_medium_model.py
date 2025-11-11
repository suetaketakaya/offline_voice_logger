"""
faster-whisper mediumモデルのダウンロードスクリプト
large-v3より軽量で高速
"""

import os
import sys
from pathlib import Path

# UTF-8出力設定
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def download_medium_model():
    """faster-whisper medium モデルをダウンロード"""

    print("=" * 60)
    print("faster-whisper medium モデル自動ダウンロード")
    print("=" * 60)
    print()
    print("mediumモデルの特徴:")
    print("  - サイズ: 約1.5GB (large-v3の半分)")
    print("  - メモリ: 約3-4GB")
    print("  - ロード時間: 1-2分")
    print("  - 精度: 日本語でも十分実用的")
    print()

    # faster-whisperのインポート確認
    try:
        from faster_whisper import WhisperModel
        print("[OK] faster-whisper がインストールされています")
    except ImportError:
        print("[ERROR] faster-whisper がインストールされていません")
        print()
        print("以下のコマンドでインストールしてください:")
        print("  pip install faster-whisper")
        return False

    # モデル保存先
    models_dir = Path(__file__).parent / 'models'
    model_dir = models_dir / 'medium'

    print(f"\nモデル保存先: {model_dir}")
    print()

    # ディレクトリ作成
    models_dir.mkdir(exist_ok=True)

    print("ダウンロード開始...")
    print("=" * 60)
    print()

    try:
        # モデルのダウンロードとロード
        print("モデルをダウンロード中...")
        print("(初回は数分かかります。完了までお待ちください...)")
        print()

        model = WhisperModel(
            "medium",
            device="cpu",
            compute_type="int8",
            download_root=str(models_dir)
        )

        print()
        print("=" * 60)
        print("[SUCCESS] ダウンロード完了!")
        print("=" * 60)
        print()

        # Hugging Faceキャッシュからmediumディレクトリにコピー
        hf_cache_path = models_dir / 'models--Systran--faster-whisper-medium' / 'snapshots'
        if hf_cache_path.exists():
            snapshot_dirs = list(hf_cache_path.glob('*'))
            if snapshot_dirs:
                import shutil
                source_dir = snapshot_dirs[0]
                if model_dir.exists():
                    shutil.rmtree(model_dir)
                shutil.copytree(source_dir, model_dir)
                print(f"モデルファイルをコピー: {model_dir}")

        # ファイルの確認
        if model_dir.exists():
            files = list(model_dir.glob("*"))
            print(f"ダウンロードされたファイル数: {len(files)}")
            print()
            print("ファイル一覧:")
            for file in sorted(files)[:15]:
                if file.is_file():
                    file_size = file.stat().st_size / (1024 * 1024)
                    print(f"  - {file.name} ({file_size:.2f} MB)")

            # 合計サイズ
            print()
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            total_size_gb = total_size / (1024 * 1024 * 1024)
            print(f"合計サイズ: {total_size_gb:.2f} GB")

        print()
        print("次のステップ:")
        print("1. 設定ファイルを編集してmediumモデルを使用")
        print("2. cd src")
        print("3. python main.py でアプリケーションを起動")
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
        print()
        return False


if __name__ == "__main__":
    print()
    success = download_medium_model()

    if success:
        print("\n" + "=" * 60)
        print("mediumモデルのダウンロードが完了しました！")
        print("=" * 60)
        print()
        print("設定を変更してmediumモデルを使用するには:")
        print("  1. 設定ファイル: %APPDATA%\\OfflineVoiceLogger\\config.ini")
        print("  2. [Transcription]セクションの model = large-v3")
        print("     を model = medium に変更")
        print()
        print("または、自動で設定を変更しますか？ (y/n): ", end="")

        try:
            response = input()
            if response.lower() == 'y':
                import configparser
                config_path = Path(os.getenv('APPDATA')) / 'OfflineVoiceLogger' / 'config.ini'
                if config_path.exists():
                    config = configparser.ConfigParser()
                    config.read(config_path, encoding='utf-8')
                    config.set('Transcription', 'model', 'medium')
                    with open(config_path, 'w', encoding='utf-8') as f:
                        config.write(f)
                    print("\n設定を更新しました！")
                    print("python src/main.py でアプリケーションを起動できます。")
                else:
                    print("\n設定ファイルが見つかりませんでした。")
                    print("アプリケーションを一度起動して設定ファイルを作成してください。")
        except EOFError:
            print("\n設定は変更されませんでした。")

        sys.exit(0)
    else:
        print("モデルダウンロード失敗")
        sys.exit(1)
