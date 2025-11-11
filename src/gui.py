"""
OfflineVoiceLogger - GUI モジュール (PyQt5版)

基本的なユーザーインターフェース
- メインウィンドウ
- デバイス選択
- 言語選択
- 録音開始/停止
- リアルタイム文字起こし表示
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QFileDialog,
    QLineEdit, QProgressBar, QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

try:
    from .logger import get_logger
except ImportError:
    from logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""

    # シグナル定義
    start_recording_signal = pyqtSignal()
    stop_recording_signal = pyqtSignal()
    save_file_signal = pyqtSignal()
    reset_text_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OfflineVoiceLogger v1.0.0")
        self.setGeometry(100, 100, 800, 600)

        # セントラルウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # レイアウト
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # UI要素の初期化
        self.setup_device_selection(main_layout)
        self.setup_control_buttons(main_layout)
        self.setup_audio_level_display(main_layout)
        self.setup_transcription_display(main_layout)
        self.setup_status_bar()

        # 録音状態
        self.is_recording = False

        logger.info("GUI初期化完了")

    def setup_device_selection(self, layout):
        """デバイス選択UI"""
        device_layout = QHBoxLayout()

        # デバイス選択
        device_label = QLabel("音声デバイス:")
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(350)
        self.device_combo.setToolTip(
            "マイク: マイクからの音声を録音\n"
            "スクリーンキャプチャー/システムオーディオ: PC画面の音声を録音\n"
            "（画面録画、ブラウザ、Teams等の音声）"
        )
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combo)

        device_layout.addSpacing(20)

        # 言語選択
        language_label = QLabel("言語:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("日本語", "ja")
        self.language_combo.addItem("English", "en")
        self.language_combo.setMinimumWidth(120)
        device_layout.addWidget(language_label)
        device_layout.addWidget(self.language_combo)

        device_layout.addStretch()

        layout.addLayout(device_layout)

        # 保存先選択
        save_layout = QHBoxLayout()
        save_label = QLabel("保存先:")
        self.save_path_edit = QLineEdit()
        self.save_path_edit.setPlaceholderText("保存先ディレクトリを選択...")
        self.browse_button = QPushButton("参照")
        self.browse_button.clicked.connect(self.browse_save_directory)

        save_layout.addWidget(save_label)
        save_layout.addWidget(self.save_path_edit)
        save_layout.addWidget(self.browse_button)

        layout.addLayout(save_layout)

    def setup_control_buttons(self, layout):
        """コントロールボタンUI"""
        button_layout = QHBoxLayout()

        # 録音開始ボタン
        self.start_button = QPushButton("● 録音開始")
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #3D8B40;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        self.start_button.clicked.connect(self.on_start_recording)

        # 停止ボタン
        self.stop_button = QPushButton("■ 停止")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #C62828;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        self.stop_button.clicked.connect(self.on_stop_recording)

        # 保存ボタン
        self.save_button = QPushButton("💾 保存")
        self.save_button.setMinimumHeight(40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.save_button.clicked.connect(self.on_save_file)

        # リセットボタン
        self.reset_button = QPushButton("🗑️ リセット")
        self.reset_button.setMinimumHeight(40)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
            QPushButton:pressed {
                background-color: #616161;
            }
        """)
        self.reset_button.clicked.connect(self.on_reset_text)

        # アプリ選択ヘルプボタン
        self.app_help_button = QPushButton("📱 アプリ選択ガイド")
        self.app_help_button.setMinimumHeight(40)
        self.app_help_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        self.app_help_button.clicked.connect(self.show_app_selection_guide)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.app_help_button)

        layout.addLayout(button_layout)

    def setup_audio_level_display(self, layout):
        """音声レベル表示UI"""
        level_layout = QHBoxLayout()

        level_label = QLabel("音声レベル:")
        self.audio_level_bar = QProgressBar()
        self.audio_level_bar.setMaximum(100)
        self.audio_level_bar.setValue(0)
        self.audio_level_bar.setTextVisible(True)
        self.audio_level_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)

        level_layout.addWidget(level_label)
        level_layout.addWidget(self.audio_level_bar)

        layout.addLayout(level_layout)

        # ローディング表示UI
        loading_layout = QHBoxLayout()
        self.loading_label = QLabel("⏳ 準備中...")
        self.loading_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2196F3;
                padding: 5px;
            }
        """)
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)  # 無限ループアニメーション
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setMaximumHeight(20)
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                background-color: #E3F2FD;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)

        loading_layout.addWidget(self.loading_label)
        loading_layout.addWidget(self.loading_bar)

        self.loading_widget = QWidget()
        self.loading_widget.setLayout(loading_layout)
        self.loading_widget.setVisible(False)  # 初期状態は非表示

        layout.addWidget(self.loading_widget)

    def setup_transcription_display(self, layout):
        """文字起こし結果表示UI"""
        # ラベル
        display_label = QLabel("文字起こし結果:")
        layout.addWidget(display_label)

        # テキスト表示エリア
        self.transcription_text = QTextEdit()
        self.transcription_text.setReadOnly(True)
        self.transcription_text.setPlaceholderText("文字起こし結果がここに表示されます...")

        # フォント設定
        font = QFont("Yu Gothic UI", 10)
        self.transcription_text.setFont(font)

        layout.addWidget(self.transcription_text)

    def setup_status_bar(self):
        """ステータスバー"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # モデル状態ラベル（右側に固定表示）
        self.model_status_label = QLabel("モデル: 未ロード")
        self.model_status_label.setStyleSheet("""
            QLabel {
                padding: 2px 10px;
                background-color: #FFF3CD;
                border: 1px solid #FFC107;
                border-radius: 3px;
                color: #856404;
            }
        """)
        self.status_bar.addPermanentWidget(self.model_status_label)

        self.update_status("待機中", "")

    def on_start_recording(self):
        """録音開始ボタンハンドラ"""
        logger.info("録音開始ボタンがクリックされました")
        # ここではボタン状態の最小限のみ変更し、実際の開始時の切り替えはメイン側で行う
        self.start_button.setEnabled(False)
        # 停止ボタンは実際にキャプチャ開始まで無効のまま
        self.stop_button.setEnabled(False)
        self.update_status("準備中...", "blue")
        self.start_recording_signal.emit()

    def on_stop_recording(self):
        """停止ボタンハンドラ"""
        logger.info("停止ボタンがクリックされました")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.is_recording = False
        self.update_status("停止", "orange")
        self.stop_recording_signal.emit()

    def on_save_file(self):
        """保存ボタンハンドラ"""
        logger.info("保存ボタンがクリックされました")
        self.save_file_signal.emit()

    def on_reset_text(self):
        """リセットボタンハンドラ"""
        logger.info("リセットボタンがクリックされました")

        # 確認ダイアログを表示
        reply = QMessageBox.question(
            self,
            "文字起こし結果をリセット",
            "文字起こし結果の履歴をすべて削除しますか？\n\nこの操作は取り消せません。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            logger.info("リセット確認: はい")
            self.reset_text_signal.emit()
        else:
            logger.info("リセット確認: キャンセル")

    def browse_save_directory(self):
        """保存先ディレクトリ選択"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "保存先ディレクトリを選択",
            self.save_path_edit.text() or ""
        )
        if directory:
            self.save_path_edit.setText(directory)
            logger.info(f"保存先を選択: {directory}")

    def add_transcription_text(self, text: str, timestamp: str = None):
        """文字起こし結果を追加

        Args:
            text (str): テキスト
            timestamp (str): タイムスタンプ (オプション)
        """
        if timestamp:
            formatted_text = f"[{timestamp}] {text}"
        else:
            formatted_text = text

        self.transcription_text.append(formatted_text)

        # 自動スクロール
        scrollbar = self.transcription_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_transcription_text(self):
        """文字起こし結果をクリア"""
        self.transcription_text.clear()

    def update_audio_level(self, level: float):
        """音声レベルを更新

        Args:
            level (float): 音声レベル (0.0～1.0)
        """
        level_percent = int(level * 100)
        self.audio_level_bar.setValue(level_percent)

    def show_loading(self, message: str = "準備中..."):
        """ローディング表示を表示

        Args:
            message (str): ローディング中のメッセージ
        """
        self.loading_label.setText(f"⏳ {message}")
        self.loading_widget.setVisible(True)
        logger.info(f"ローディング表示: {message}")

    def hide_loading(self):
        """ローディング表示を非表示"""
        self.loading_widget.setVisible(False)
        logger.info("ローディング非表示")

    def update_status(self, message: str, color: str = "black"):
        """ステータスバーを更新

        Args:
            message (str): ステータスメッセージ
            color (str): テキスト色
        """
        self.status_bar.showMessage(message)
        self.status_bar.setStyleSheet(f"color: {color};")

    def update_device_list(self, devices: list):
        """デバイスリストを更新

        Args:
            devices (list): デバイス情報のリスト
        """
        self.device_combo.clear()
        for device in devices:
            device_name = device.get('name', '')
            device_id = device.get('id', -1)
            type_display = device.get('type_display', '')

            # デバイスタイプを表示名に含める
            if type_display:
                display_name = f"[{type_display}] {device_name}"
            else:
                display_name = device_name

            self.device_combo.addItem(display_name, device_id)

        logger.info(f"デバイスリスト更新: {len(devices)}個")

    def get_selected_device_id(self) -> int:
        """選択されたデバイスIDを取得

        Returns:
            int: デバイスID
        """
        return self.device_combo.currentData()

    def get_selected_language(self) -> str:
        """選択された言語を取得

        Returns:
            str: 言語コード ("ja" or "en")
        """
        return self.language_combo.currentData()

    def get_save_directory(self) -> str:
        """保存先ディレクトリを取得

        Returns:
            str: ディレクトリパス
        """
        return self.save_path_edit.text()

    def set_save_directory(self, directory: str):
        """保存先ディレクトリを設定

        Args:
            directory (str): ディレクトリパス
        """
        self.save_path_edit.setText(directory)

    def show_error(self, title: str, message: str):
        """エラーダイアログを表示

        Args:
            title (str): タイトル
            message (str): メッセージ
        """
        QMessageBox.critical(self, title, message)
        logger.error(f"エラーダイアログ表示: {title} - {message}")

    def show_info(self, title: str, message: str):
        """情報ダイアログを表示

        Args:
            title (str): タイトル
            message (str): メッセージ
        """
        QMessageBox.information(self, title, message)
        logger.info(f"情報ダイアログ表示: {title} - {message}")

    def show_warning(self, title: str, message: str):
        """警告ダイアログを表示

        Args:
            title (str): タイトル
            message (str): メッセージ
        """
        QMessageBox.warning(self, title, message)
        logger.warning(f"警告ダイアログ表示: {title} - {message}")

    def update_model_status(self, status: str, color: str = "gray"):
        """モデル状態を更新

        Args:
            status (str): ステータステキスト ("未ロード", "ロード中...", "ロード完了", "エラー")
            color (str): 色 ("gray", "blue", "green", "red")
        """
        self.model_status_label.setText(f"モデル: {status}")

        # 色に応じたスタイル
        styles = {
            "gray": {
                "bg": "#E0E0E0",
                "border": "#BDBDBD",
                "text": "#616161"
            },
            "blue": {
                "bg": "#E3F2FD",
                "border": "#2196F3",
                "text": "#0D47A1"
            },
            "green": {
                "bg": "#E8F5E9",
                "border": "#4CAF50",
                "text": "#1B5E20"
            },
            "red": {
                "bg": "#FFEBEE",
                "border": "#F44336",
                "text": "#B71C1C"
            },
            "orange": {
                "bg": "#FFF3E0",
                "border": "#FF9800",
                "text": "#E65100"
            }
        }

        style = styles.get(color, styles["gray"])
        self.model_status_label.setStyleSheet(f"""
            QLabel {{
                padding: 2px 10px;
                background-color: {style['bg']};
                border: 1px solid {style['border']};
                border-radius: 3px;
                color: {style['text']};
                font-weight: bold;
            }}
        """)

        logger.info(f"モデル状態更新: {status}")

    def show_app_selection_guide(self):
        """アプリケーション選択ガイドを表示"""
        guide_text = """
<h2>📱 特定アプリの音声を録音する方法</h2>

<h3>Windows 10/11の設定を使用する方法：</h3>
<ol>
<li><b>Windowsの設定を開く</b><br>
   設定 → システム → サウンド → アプリの音量とデバイスの基本設定</li>

<li><b>録音したいアプリを探す</b><br>
   例: Chrome, Microsoft Teams, Zoom など</li>

<li><b>出力デバイスを変更</b><br>
   アプリの出力を「ステレオミキサー」または仮想デバイスに設定</li>

<li><b>OfflineVoiceLoggerで録音</b><br>
   オーディオデバイスで設定したデバイスを選択して録音開始</li>
</ol>

<h3>仮想デバイスを使用する方法（推奨）：</h3>
<ol>
<li><b>VB-Cable (Virtual Audio Cable) をインストール</b><br>
   ダウンロード: https://vb-audio.com/Cable/</li>

<li><b>録音したいアプリの音声出力を設定</b><br>
   アプリの設定で、音声出力を「CABLE Input」に変更<br>
   例: Teamsの設定 → デバイス → スピーカー → CABLE Input</li>

<li><b>OfflineVoiceLoggerでCable Outputを選択</b><br>
   オーディオデバイスで「CABLE Output」を選択</li>

<li><b>録音開始</b><br>
   該当アプリの音声のみが録音されます</li>
</ol>

<h3>対応アプリケーション例：</h3>
<ul>
<li>🌐 ブラウザ (Chrome, Edge, Firefox)</li>
<li>📞 Microsoft Teams</li>
<li>💬 Zoom</li>
<li>🎵 Spotify</li>
<li>▶️ VLC Media Player</li>
</ul>

<p><b>注意</b>: アプリ単位の録音には、Windowsの設定変更または仮想オーディオデバイスが必要です。</p>
"""

        msg = QMessageBox(self)
        msg.setWindowTitle("アプリケーション選択ガイド")
        msg.setTextFormat(Qt.RichText)
        msg.setText(guide_text)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        logger.info("アプリ選択ガイドを表示")

    def closeEvent(self, event):
        """ウィンドウクローズイベント"""
        if self.is_recording:
            reply = QMessageBox.question(
                self,
                "確認",
                "録音中です。終了してもよろしいですか?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.stop_recording_signal.emit()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


# 使用例
if __name__ == "__main__":
    from logger import setup_global_logger

    setup_global_logger("DEBUG")

    app = QApplication(sys.argv)
    window = MainWindow()

    # テスト用デバイスリスト
    test_devices = [
        {"id": 0, "name": "マイク (Realtek Audio)", "is_loopback": False},
        {"id": 1, "name": "ステレオミキサー (Realtek Audio)", "is_loopback": True},
    ]
    window.update_device_list(test_devices)

    # テスト用文字起こし結果
    window.add_transcription_text("こんにちは、テストです。", "00:00:05")
    window.add_transcription_text("音声認識のテストを行っています。", "00:00:12")

    window.show()
    sys.exit(app.exec_())
