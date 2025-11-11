"""
faster-whisperモデルの自動ダウンロードスクリプト（非対話型）
"""

import os
import sys
from pathlib import Path

# UTF-8出力設定
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def download_model():
    """faster-whisper large-v3 モデルを自動ダウンロード"""

    print("=" * 60)
    print("faster-whisper large-v3 モデル自動ダウンロード")
    print("=" * 60)
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
    model_dir = models_dir / 'large-v3'

    print(f"\nモデル保存先: {model_dir}")
    print()

    # ディレクトリ作成
    models_dir.mkdir(exist_ok=True)

    print("ダウンロード情報:")
    print("- モデル: large-v3")
    print("- サイズ: 約3GB")
    print("- 所要時間: 10-30分（回線速度による）")
    print()
    print("=" * 60)
    print("ダウンロード開始...")
    print("=" * 60)
    print()

    try:
        # モデルのダウンロードとロード
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
        print("[SUCCESS] ダウンロード完了!")
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
            for file in sorted(files)[:15]:  # 最初の15ファイルのみ表示
                if file.is_file():
                    file_size = file.stat().st_size / (1024 * 1024)  # MB
                    print(f"  - {file.name} ({file_size:.2f} MB)")
            if len(files) > 15:
                print(f"  ... 他 {len(files) - 15} ファイル")

            # 合計サイズ
            print()
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            total_size_gb = total_size / (1024 * 1024 * 1024)
            print(f"合計サイズ: {total_size_gb:.2f} GB")

        print()
        print("次のステップ:")
        print("1. cd src")
        print("2. python main.py でアプリケーションを起動")
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
        print("トラブルシューティング:")
        print("1. インターネット接続を確認してください")
        print("2. ディスク空き容量を確認してください (最低5GB必要)")
        print("3. faster-whisperを再インストールしてみてください:")
        print("   pip uninstall faster-whisper")
        print("   pip install faster-whisper")
        print()
        return False


if __name__ == "__main__":
    print()
    success = download_model()

    if success:
        print("モデルダウンロード成功!")
        sys.exit(0)
    else:
        print("モデルダウンロード失敗")
        sys.exit(1)
