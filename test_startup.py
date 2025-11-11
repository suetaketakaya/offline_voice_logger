"""
起動テストスクリプト - 段階的にモジュールをテスト
"""
import sys

print("=" * 60)
print("起動テスト開始")
print("=" * 60)

# テスト1: 基本インポート
print("\nテスト1: 基本インポートテスト")
try:
    import sys
    import os
    from pathlib import Path
    print("  [OK] 標準ライブラリ")
except Exception as e:
    print(f"  [ERROR] 標準ライブラリ: {e}")
    sys.exit(1)

# テスト2: PyQt5インポート
print("\nテスト2: PyQt5インポートテスト")
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    print("  [OK] PyQt5インポート")
except Exception as e:
    print(f"  [ERROR] PyQt5インポート: {e}")
    sys.exit(1)

# テスト3: PyQt5初期化
print("\nテスト3: PyQt5初期化テスト")
try:
    app = QApplication(sys.argv)
    print("  [OK] PyQt5初期化")
except Exception as e:
    print(f"  [ERROR] PyQt5初期化: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# テスト4: プロジェクトモジュールインポート
print("\nテスト4: プロジェクトモジュールインポートテスト")
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from logger import setup_global_logger, get_logger
    print("  [OK] logger")
except Exception as e:
    print(f"  [ERROR] logger: {e}")
    import traceback
    traceback.print_exc()

try:
    from config_manager import ConfigManager
    print("  [OK] config_manager")
except Exception as e:
    print(f"  [ERROR] config_manager: {e}")
    import traceback
    traceback.print_exc()

try:
    from audio_capture import AudioCapture
    print("  [OK] audio_capture")
except Exception as e:
    print(f"  [ERROR] audio_capture: {e}")
    import traceback
    traceback.print_exc()

try:
    from file_manager import FileManager
    print("  [OK] file_manager")
except Exception as e:
    print(f"  [ERROR] file_manager: {e}")
    import traceback
    traceback.print_exc()

try:
    from gui import MainWindow
    print("  [OK] gui")
except Exception as e:
    print(f"  [ERROR] gui: {e}")
    import traceback
    traceback.print_exc()

# テスト5: 簡単なGUIテスト
print("\nテスト5: 簡単なGUIウィンドウ作成テスト")
try:
    from PyQt5.QtWidgets import QMainWindow, QLabel

    class SimpleWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("テストウィンドウ")
            self.setGeometry(100, 100, 400, 300)
            label = QLabel("起動テスト成功！", self)
            label.move(150, 130)

    window = SimpleWindow()
    window.show()
    print("  [OK] GUIウィンドウ作成")
    print("\nテストウィンドウを表示しています...")
    print("ウィンドウを閉じるとテストが完了します。")

    sys.exit(app.exec_())

except Exception as e:
    print(f"  [ERROR] GUIウィンドウ作成: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
