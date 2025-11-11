"""
faster-whisperモデルのダウンロードスクリプト

このスクリプトを実行すると、faster-whisperのlarge-v3モデルを
ローカルにダウンロードします。

注意: インターネット接続が必要です（初回ダウンロード時のみ）
"""

import os
import sys
from pathlib import Path

def download_model():
    """faster-whisper large-v3 モデルをダウンロード"""

    print("=" * 60)
    print("faster-whisper large-v3 モデルダウンロード")
    print("=" * 60)
    print()

    # faster-whisperのインポート確認
    try:
        from faster_whisper import WhisperModel
        print("✓ faster-whisper がインストールされています")
    except ImportError:
        print("✗ faster-whisper がインストールされていません")
        print()
        print("以下のコマンドでインストールしてください:")
        print("  pip install faster-whisper")
        return False

    # モデル保存先
    models_dir = Path(__file__).parent / 'models'
    model_dir = models_dir / 'large-v3'

    print(f"\nモデル保存先: {model_dir}")
    print()

    # ディレクトリ作成
    models_dir.mkdir(exist_ok=True)

    # ダウンロード確認
    print("このスクリプトは以下を実行します:")
    print("1. Hugging Faceからfaster-whisper large-v3モデルをダウンロード")
    print("2. models/large-v3/ ディレクトリに保存")
    print()
    print("注意:")
    print("- ダウンロードサイズ: 約3GB")
    print("- インターネット接続が必要です")
    print("- ダウンロードには10-30分かかる場合があります")
    print()

    response = input("ダウンロードを開始しますか? (y/n): ")
    if response.lower() != 'y':
        print("キャンセルされました。")
        return False

    print()
    print("=" * 60)
    print("ダウンロード開始...")
    print("=" * 60)
    print()

    try:
        # モデルのダウンロードとロード
        # download_root を指定することでローカルに保存
        print("モデルをダウンロード中...")
        print("(初回は時間がかかります。完了までお待ちください...)")
        print()

        model = WhisperModel(
            "large-v3",
            device="cpu",
            compute_type="int8",
            download_root=str(models_dir)
        )

        print()
        print("=" * 60)
        print("✓ ダウンロード完了!")
        print("=" * 60)
        print()
        print(f"モデルファイルの場所: {model_dir}")
        print()

        # ファイルの確認
        if model_dir.exists():
            files = list(model_dir.glob("*"))
            print(f"ダウンロードされたファイル数: {len(files)}")
            print()
            print("ファイル一覧:")
            for file in files[:10]:  # 最初の10ファイルのみ表示
                file_size = file.stat().st_size / (1024 * 1024)  # MB
                print(f"  - {file.name} ({file_size:.2f} MB)")
            if len(files) > 10:
                print(f"  ... 他 {len(files) - 10} ファイル")

        print()
        print("次のステップ:")
        print("1. python src/main.py でアプリケーションを起動")
        print("2. モデルが自動的にロードされます")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 60)
        print("✗ エラーが発生しました")
        print("=" * 60)
        print()
        print(f"エラー内容: {e}")
        print()
        print("トラブルシューティング:")
        print("1. インターネット接続を確認してください")
        print("2. ディスク空き容量を確認してください (最低5GB必要)")
        print("3. faster-whisperを再インストールしてみてください:")
        print("   pip uninstall faster-whisper")
        print("   pip install faster-whisper")
        print()
        return False


def check_existing_model():
    """既存モデルの確認"""
    model_dir = Path(__file__).parent / 'models' / 'large-v3'

    if model_dir.exists():
        files = list(model_dir.glob("*"))
        if len(files) > 0:
            print("=" * 60)
            print("既存のモデルが見つかりました")
            print("=" * 60)
            print()
            print(f"場所: {model_dir}")
            print(f"ファイル数: {len(files)}")
            print()

            # 合計サイズ
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            total_size_mb = total_size / (1024 * 1024)
            total_size_gb = total_size_mb / 1024
            print(f"合計サイズ: {total_size_gb:.2f} GB ({total_size_mb:.0f} MB)")
            print()

            response = input("既存のモデルを使用しますか? (y/n): ")
            if response.lower() == 'y':
                print()
                print("既存のモデルを使用します。")
                print("python src/main.py でアプリケーションを起動できます。")
                return True
            else:
                response = input("既存のモデルを削除して再ダウンロードしますか? (y/n): ")
                if response.lower() == 'y':
                    import shutil
                    shutil.rmtree(model_dir)
                    print(f"削除しました: {model_dir}")
                    print()
                    return False
                else:
                    print("キャンセルされました。")
                    return True

    return False


if __name__ == "__main__":
    print()
    print("faster-whisper モデルダウンローダー")
    print()

    # 既存モデルの確認
    if check_existing_model():
        sys.exit(0)

    # モデルのダウンロード
    success = download_model()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
