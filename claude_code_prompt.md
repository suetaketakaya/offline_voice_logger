# OfflineVoiceLogger - リアルタイム音声文字起こしツール（MSIインストーラー版）の作成

## アプリケーション名
**OfflineVoiceLogger**（オフラインボイスロガー）

## 概要
Windowsのデスクトップ上で流れている音声データ（システム音声）をリアルタイムでキャプチャし、faster-whisperを使用して日本語または英語の発声を文字起こしする**完全オフライン動作**のツールを作成してください。

**重要**: 本ツールは社外秘情報を扱うため、インターネット接続を一切行わず、すべての処理をローカル環境で完結させる必要があります。MSIインストーラーでの配布を前提とし、エンドユーザーが簡単にインストール・使用できる状態にしてください。

## 参考記事
https://qiita.com/87Gihara/items/5f386619c1ba07786ded

### 参考記事からの主な変更点
1. **録音ファイル処理 → リアルタイム処理**
   - 参考記事: 録音済みファイルを文字起こし
   - 本ツール: デスクトップ音声をリアルタイムでキャプチャ＆文字起こし

2. **オンライン動作 → 完全オフライン動作**
   - 参考記事: モデルダウンロードにインターネット接続が必要
   - 本ツール: モデルファイルをインストーラーに同梱、完全オフライン動作

3. **スクリプト実行 → MSIインストーラー配布**
   - 参考記事: Pythonスクリプトとして実行
   - 本ツール: MSIインストーラーでワンクリックインストール

4. **日本語のみ → 日本語/英語切り替え**
   - 参考記事: 日本語のみ対応
   - 本ツール: GUI上で日本語/英語を選択可能

5. **議事録作成 → リアルタイム文字起こし**
   - 参考記事: 文字起こし後にLLMで議事録作成
   - 本ツール: リアルタイム文字起こしに特化（LLM要約は含まない）

## 要件

### セキュリティ要件（最重要）
**本アプリケーションは社外秘情報を扱うため、完全にローカル環境のみで動作すること**

1. **ネットワーク通信の完全遮断**
   - インターネット接続を一切行わない
   - モデルファイルは事前にダウンロードしてインストーラーに同梱
   - 初回起動時も外部通信なしで動作可能
   - ネットワークアクセスを試みる場合はエラーを出す

2. **データの完全ローカル保存**
   - すべての音声データ、文字起こし結果はローカルディスク上のみに保存
   - クラウドストレージへのアップロード機能は実装しない
   - 一時ファイルもすべてローカルに保存

3. **外部サービスの不使用**
   - 外部API呼び出しなし
   - アップデートチェック機能なし
   - テレメトリー送信なし
   - ログやクラッシュレポートの外部送信なし

### 機能要件

1. **音声キャプチャ**
   - Windowsのデスクトップ音声（システム音声/ループバック音声）をリアルタイムでキャプチャ
   - PyAudioまたはsounddeviceライブラリを使用してWASAPI経由で音声取得
   - サンプリングレート: 16kHz（whisperの推奨値）
   - チャンネル: モノラル
   - **音声入力レベルのリアルタイムモニタリング（視覚的なレベルメーター）**
   - **無音検出機能（VADしきい値の調整可能）**
   - **音声デバイスの自動再接続（デバイス切断時）**

2. **リアルタイム文字起こし**
   - faster-whisperを使用して音声をテキスト化
   - モデル: large-v3 または medium（パフォーマンスとのバランスを考慮）
   - **言語: 日本語（ja）または英語（en）を選択可能**
   - 言語はGUIで切り替え可能（ドロップダウンメニュー）
   - VADフィルター有効化（vad_filter=True）でノイズ除去
   - ハルシネーション抑制（hallucination_silence_threshold設定）
   - 音声データを適切な長さのバッファリング（例: 5-10秒単位）で処理
   - **処理進捗の表示（プログレスバーまたはスピナー）**
   - **文字起こし中の一時停止・再開機能**

3. **GUI表示**
   - PyQt5でシンプルなGUIを実装
   - リアルタイムで文字起こし結果を表示（スクロール可能）
   - タイムスタンプ付きで表示
   - 開始/停止/一時停止ボタン
   - 音声入力デバイス選択機能
   - **言語選択機能**（日本語/英語の切り替えドロップダウン）
   - **保存先ディレクトリ選択機能**
     - テキストボックスで保存先パスを表示
     - 「参照」ボタンでフォルダ選択ダイアログを開く
     - デフォルトはマイドキュメントまたは実行ファイルと同じディレクトリ
   - **メニューバーの実装**
     - ファイル: 保存、名前を付けて保存、終了
     - 編集: コピー、全選択、検索
     - 表示: フォントサイズ、自動スクロール、ダークモード
     - ツール: 設定、ログ表示
     - ヘルプ: 使い方、キーボードショートカット、バージョン情報
   - 結果をテキストファイルに保存する機能（保存先はユーザー指定）
   - **文字起こし結果の基本的な編集機能（選択、コピー、削除）**
   - **検索機能（文字起こし結果内のテキスト検索）**
   - **フォントサイズの変更機能**
   - **自動スクロールのON/OFF切り替え**

4. **ファイル保存・管理**
   - **複数のエクスポート形式に対応**
     - TXTファイル（プレーンテキスト、UTF-8）
     - SRTファイル（字幕形式、タイムスタンプ付き）
     - JSONファイル（構造化データ、タイムスタンプとメタデータ含む）
   - **ファイル名のテンプレート機能**
     - デフォルト: `transcript_YYYYMMDD_HHMMSS.txt`
     - カスタマイズ可能: 接頭辞、日時形式、連番など
   - **自動保存機能**
     - 一定間隔（5分ごと等）で自動保存
     - クラッシュ時のデータ復旧用
     - 自動保存インジケーターの表示
   - **ファイル上書き確認ダイアログ**
   - **エンコーディング選択（UTF-8、Shift-JIS、EUC-JP等）**
   - **保存履歴の表示**
     - 最近保存したファイルのリスト（最大10件）
     - クイックアクセス機能

4b. **音声データの管理とストレージ最適化**
   - **一時音声データの管理**
     - 音声バッファの一時保存場所: `%TEMP%\OfflineVoiceLogger\audio_buffer\`
     - バッファサイズ制限: メモリの10%まで（最大1GB）
     - 処理済みバッファの即時削除
     - メモリ不足時の自動フラッシュ
   
   - **ディスク容量の監視と管理**
     - **リアルタイム容量チェック**
       - 録音開始時: 保存先ドライブの空き容量確認（最低1GB必要）
       - 録音中: 30秒ごとに空き容量チェック
       - 警告しきい値: 500MB未満で警告表示
       - 停止しきい値: 100MB未満で自動停止
     - **容量不足時の対応**
       - 警告ダイアログの表示
       - 保存先変更の提案
       - 古いバックアップファイルの削除提案
       - 一時ファイルのクリーンアップ
   
   - **メモリ使用量の管理**
     - **メモリ使用量の監視**
       - 起動時: システムメモリの確認
       - 実行中: メモリ使用量のリアルタイム監視
       - 警告しきい値: システムメモリの80%
       - 緊急しきい値: システムメモリの90%
     - **メモリ不足時の対応**
       - 自動的にバッファサイズを縮小
       - ガベージコレクションの強制実行
       - 軽量モデル（medium）への切り替え提案
       - 他のアプリケーションを閉じることを提案
   
   - **音声データの保存タイミング**
     - **文字起こし結果の保存**
       - リアルタイム保存: 各セグメント処理後に即座にメモリ上に保持
       - 自動保存: 設定した間隔（デフォルト5分）でファイルに書き込み
       - 手動保存: ユーザーが「保存」ボタンを押したとき
       - 終了時保存: アプリ終了時に未保存データを自動保存
     - **音声ファイルの保存（オプション機能）**
       - デバッグモード有効時のみ
       - WAV形式で保存
       - ファイルサイズ制限: 1ファイル100MBまで
       - 保存場所: `%APPDATA%\OfflineVoiceLogger\audio_debug\`
   
   - **一時ファイルのクリーンアップ**
     - **自動クリーンアップ**
       - アプリ終了時: TEMPディレクトリ配下の一時ファイルを削除
       - 起動時: 前回の残存ファイルをチェックして削除
       - 定期クリーンアップ: 24時間以上古い一時ファイルを削除
     - **手動クリーンアップ**
       - メニュー→ツール→一時ファイルのクリーンアップ
       - クリーンアップ対象:
         - 一時音声バッファ
         - 古いバックアップファイル（10件超）
         - 古いログファイル（5件超）
         - 古いクラッシュレポート（10件超）
       - 削除前に確認ダイアログを表示
       - 削除後の空き容量を表示
   
   - **データ保持ポリシー**
     - **文字起こし結果**: ユーザーが削除するまで永続保持
     - **自動保存ファイル**: ユーザーが削除するまで保持
     - **バックアップファイル**: 最新10件まで保持、古いものは自動削除
     - **ログファイル**: 最新5件まで保持（合計50MB制限）
     - **クラッシュレポート**: 最新10件まで保持
     - **一時音声バッファ**: 処理完了後即座に削除
     - **デバッグ音声ファイル**: 手動削除のみ（自動削除なし）
   
   - **ストレージ効率化**
     - **ファイル圧縮（将来機能）**
       - 古い文字起こし結果の自動圧縮
       - ZIP形式での保存
     - **重複排除**
       - 同じ内容のバックアップを検出
       - ファイルハッシュによる重複チェック
   
   - **ストレージ統計情報**
     - メニュー→ツール→ストレージ情報
     - 表示内容:
       - 文字起こし結果: ファイル数、合計サイズ
       - バックアップ: ファイル数、合計サイズ
       - ログファイル: ファイル数、合計サイズ
       - 一時ファイル: ファイル数、合計サイズ
       - 合計使用量
       - 保存先ドライブの空き容量

5. **設定管理**
   - **設定の永続化（config.iniファイル）**
     - 保存場所: `%APPDATA%\OfflineVoiceLogger\config.ini`
     - 保存項目:
       - 前回使用したデバイス
       - 言語設定
       - 保存先パス
       - ウィンドウサイズと位置
       - バッファサイズ
       - モデル選択
       - 自動保存間隔
       - フォントサイズ
       - テーマ（ライト/ダーク）
       - 最近使用したファイルリスト
       - **ストレージ管理設定**:
         - 最大メモリ使用量（MB）
         - 最大バッファサイズ（秒）
         - ディスク容量警告しきい値（MB）
         - 自動クリーンアップ有効/無効
         - バックアップ最大保持数
         - ログファイル最大保持数
         - デバッグ音声保存有効/無効
   - **設定画面の実装**
     - 詳細設定ダイアログ（メニュー→ツール→設定）
     - タブ形式のUI:
       - 一般タブ: 言語、保存先、自動保存
       - 音声タブ: デバイス、バッファサイズ、VADしきい値
       - 文字起こしタブ: モデル選択、言語、オプション
       - 表示タブ: フォントサイズ、テーマ、自動スクロール
       - **ストレージタブ**: メモリ使用量制限、ディスク容量管理、クリーンアップ設定
       - 詳細タブ: ログレベル、パフォーマンス設定
   - **設定のリセット機能（デフォルトに戻す）**
   - **設定のインポート/エクスポート**
     - 他のPCへの設定移行用

6. **エラーハンドリングとログ**
   - **包括的なエラーハンドリング**
     - 音声デバイスが見つからない場合の対応
       - エラーダイアログ表示
       - 使用可能なデバイスの一覧表示
       - トラブルシューティングガイドへのリンク
     - モデルファイルが見つからない場合の対応
       - 詳細なエラーメッセージ
       - モデルファイルの配置場所を表示
       - 再インストールの案内
     - 保存先へのアクセス権限エラー
       - 権限の確認方法を表示
       - 別の保存先の選択を促す
     - メモリ不足エラー
       - 現在のメモリ使用状況を表示
       - 他のアプリケーションを閉じることを提案
       - 軽量モデルへの切り替えを提案
     - ディスク容量不足エラー
       - 空き容量の表示
       - 不要なファイルの削除を提案
   - **エラーメッセージの表示**
     - ユーザーフレンドリーなエラーダイアログ
     - 問題の説明
     - 解決方法の具体的な提案
     - エラーコードの表示（サポート用）
     - 「詳細を表示」ボタンでスタックトレース表示
   - **ローカルログファイルの生成**
     - ログファイル: `%APPDATA%\OfflineVoiceLogger\logs\app.log`
     - ログレベル: DEBUG, INFO, WARNING, ERROR, CRITICAL
     - ログフォーマット: `[YYYY-MM-DD HH:MM:SS] [LEVEL] [Module] Message`
     - ログローテーション（ファイルサイズ10MB超で新規作成）
     - 最大5ファイルまで保持（app.log, app.log.1, ..., app.log.4）
     - **外部送信は一切しない（完全ローカル）**
     - ログビューアー機能（メニュー→ツール→ログ表示）
   - **クラッシュレポート（ローカル保存のみ）**
     - クラッシュ時にスタックトレースをローカル保存
     - 保存場所: `%APPDATA%\OfflineVoiceLogger\crash_reports\`
     - 次回起動時に復旧オプションを表示
     - クラッシュレポートの内容をユーザーが確認可能

7. **ヘルプとドキュメント**
   - **組み込みヘルプ機能**
     - メニューバーに「ヘルプ」メニュー
     - 「使い方」ダイアログ（HTML形式で見やすく）
       - 基本操作の説明（画像付き）
       - 各機能の詳細説明
       - よくある質問（FAQ）
     - 「キーボードショートカット一覧」
       - 一覧表形式で表示
       - 印刷可能
     - 「トラブルシューティング」
       - 問題別の解決方法
       - チェックリスト形式
   - **バージョン情報ダイアログ**
     - アプリ名: OfflineVoiceLogger
     - バージョン番号（例: v1.0.0）
     - ビルド日時
     - 使用ライブラリのバージョン情報
       - Python version
       - faster-whisper version
       - tkinter/PyQt5 version
       - その他依存ライブラリ
     - ライセンス情報へのリンク
     - 「システム情報」ボタン
       - OS情報
       - CPU情報
       - メモリ情報
       - ディスク情報
   - **初回起動時のセットアップウィザード**
     - ウェルカム画面
     - 音声デバイスの選択と確認
       - テスト録音機能
       - 音声レベルの確認
     - 保存先の設定
       - デフォルト保存先の説明
       - カスタム保存先の選択
     - モデル選択
       - large-v3とmediumの違いを説明
       - システムスペックに応じた推奨を表示
     - 簡単なチュートリアル
       - 基本的な使い方のデモ
     - 「次回から表示しない」オプション
     - 設定の確認画面

8. **ステータス表示と通知**
   - **詳細なステータス表示**
     - ステータスバー（ウィンドウ下部）
       - 現在の状態（待機中/録音中/処理中/エラー）
       - アイコンと色で視覚的に表示
     - 処理時間の表示
       - 経過時間（録音開始からの時間）
       - 推定残り時間（バッファ処理中）
     - 処理済み文字数
       - リアルタイムで更新
     - CPUとメモリの使用状況（簡易表示）
       - パーセンテージ表示
       - グラフ表示（オプション）
   - **システムトレイ通知**
     - Windows通知センターへの通知
     - 処理完了時の通知
       - 文字起こし完了
       - ファイル保存完了
     - エラー発生時の通知
       - 重要なエラーのみ
     - 自動保存完了時の通知（オプション）
   - **プログレスバー**
     - バッファ蓄積中の進捗
       - 円形プログレス表示
     - 文字起こし処理の進捗
       - 水平プログレスバー
     - 長時間処理時の「キャンセル」ボタン

9. **データバックアップと復旧**
   - **自動バックアップ機能**
     - 文字起こし結果の定期バックアップ
     - バックアップ先: `%APPDATA%\OfflineVoiceLogger\backup\`
     - バックアップタイミング:
       - 自動保存時
       - 手動保存時
       - アプリ終了時
     - 最大保持数: 10件
     - 古いバックアップの自動削除
   - **復旧機能**
     - クラッシュ後の自動復旧
       - 次回起動時に復旧ダイアログを表示
       - 最後の状態からの再開オプション
     - バックアップファイルからの復元機能
       - バックアップ一覧の表示
       - プレビュー機能
       - 選択して復元

10. **アクセシビリティとユーザビリティ**
    - **キーボードショートカット**
      - Ctrl+S: 手動保存
      - Ctrl+Shift+S: 名前を付けて保存
      - Ctrl+R: 録音開始/停止
      - Space: 一時停止/再開
      - Ctrl+C: 選択テキストのコピー
      - Ctrl+F: 検索
      - Ctrl+A: 全選択
      - Ctrl+ (+/-): フォントサイズ変更
      - F1: ヘルプ
      - F5: 更新
      - Ctrl+Q: 終了
      - Ctrl+,: 設定
    - **ツールチップ**
      - すべてのボタンとコントロールに説明を表示
      - ホバー時に0.5秒後に表示
      - 分かりやすい日本語で説明
    - **高DPI対応**
      - 4K/5Kディスプレイでの適切な表示
      - スケーリング対応
      - アイコンの高解像度版を使用
    - **タブ操作対応**
      - すべてのコントロールがTabキーで移動可能
      - フォーカス表示が明確
    - **スクリーンリーダー対応（オプション）**
      - ARIA属性の設定
      - 適切なラベル付け
    - **ダークモード対応**
      - システム設定に追従または手動切り替え
      - 目に優しい配色
      - すべてのUI要素がダークモード対応

11. **パフォーマンス監視**
    - **リソース使用状況の表示**
      - CPU使用率
      - メモリ使用量
      - ディスクI/O
      - 処理速度（文字/秒）
    - **パフォーマンス警告**
      - CPU使用率が80%超で警告
      - メモリ使用量が90%超で警告
      - ディスク容量が1GB未満で警告
    - **最適化の提案**
      - 軽量モデルへの切り替え提案
      - バッファサイズの調整提案

12. **CPU最適化**
4. **CPU最適化**
   - CPU使用（compute_type="int8"）
   - GPUは使用しない想定
   - マルチスレッド処理で音声キャプチャと文字起こしを分離

5. **EXE化とリリース準備**
   - PyInstallerを使用してEXEファイル化
   - ワンファイル形式（--onefile）または、必要に応じてワンディレクトリ形式
   - アイコンファイル（.ico）の設定
   - 必要なモデルファイルや依存関係を含める
   - リリース用のZIP圧縮ファイルを作成
     - README.txt（使用方法、システム要件）
     - EXEファイル
     - ライセンス情報（必要に応じて）
   - 配布用ディレクトリ構造の整理

6. **MSIインストーラーの作成**
   - WiX Toolsetまたは他のインストーラー作成ツール（Inno Setup、Advanced Installerなど）を使用
   - インストール機能
     - プログラムファイルへのインストール（デフォルト: C:\Program Files\）
     - faster-whisperモデルファイルの同梱とインストール
     - スタートメニューへのショートカット作成
     - デスクトップアイコン作成（オプション）
     - ユーザーデータディレクトリの作成（マイドキュメント配下など）
   - アンインストール機能
     - コントロールパネルからのアンインストール対応
     - プログラムファイルの完全削除
     - レジストリエントリのクリーンアップ
     - ユーザーデータは保持（オプションで削除可能）
   - インストール要件チェック
     - Windows 10/11 64bit確認
     - 必要なディスク容量チェック（最低5GB推奨）
     - 管理者権限での実行

### 技術仕様

#### 必要なライブラリ
```
faster-whisper
pyaudio または sounddevice
numpy
tkinter（標準ライブラリ）
threading
queue
pyinstaller（EXE化用）
```

#### MSIインストーラー作成ツール（以下のいずれか）
- **WiX Toolset** (推奨): XMLベースの強力なインストーラー作成ツール
- **Inno Setup**: スクリプトベースの無料インストーラー作成ツール
- **Advanced Installer**: GUI操作可能（Free版でも十分）
- **cx_Freeze + WiX**: Pythonアプリ用の選択肢

### 性能面の見通し

#### faster-whisperモデルサイズと性能比較

**推奨モデル: large-v3**（精度とパフォーマンスのバランスが良い）

```
モデルサイズ別の性能目安（参考記事の環境: i7-12650H、32GB RAM）:

┌──────────┬────────┬──────────┬──────────────┬────────┐
│ モデル   │ サイズ │ メモリ   │ 処理時間     │ 精度   │
├──────────┼────────┼──────────┼──────────────┼────────┤
│ tiny     │ 75MB   │ ~1GB     │ 0.3x リアル  │ ★★☆☆☆ │
│ base     │ 145MB  │ ~1GB     │ 0.5x リアル  │ ★★★☆☆ │
│ small    │ 466MB  │ ~2GB     │ 1.0x リアル  │ ★★★☆☆ │
│ medium   │ 1.5GB  │ ~4GB     │ 2.0x リアル  │ ★★★★☆ │
│ large-v3 │ 3GB    │ ~8GB     │ 2.5x リアル  │ ★★★★★ │
└──────────┴────────┴──────────┴──────────────┴────────┘

処理時間の説明:
- 0.3x リアル = 10秒の音声を3秒で処理
- 2.5x リアル = 10秒の音声を25秒で処理

注意: CPUのみ使用時、リアルタイム処理には遅延が発生します
```

#### リアルタイム処理の実現可能性

**バッファ方式での実装**
```
推奨設定:
- バッファサイズ: 10秒
- オーバーラップ: 2秒
- 処理方式: 非同期（別スレッド）

実際の動作:
1. 10秒分の音声を蓄積
2. バックグラウンドで文字起こし（25秒程度かかる）
3. 次の10秒分を並行して蓄積
4. 結果をGUIに随時表示

遅延:
- 初回表示まで: 約10秒
- 以降の更新: 10秒ごと
- トータル遅延: 15-30秒（処理時間による）

※完全なリアルタイム（1秒以内の遅延）は難しいが、
  実用的な準リアルタイム処理は可能
```

#### システム要件と性能予測

**最小要件**（smallモデル使用時）
```
CPU: Intel Core i5 第8世代以上 / AMD Ryzen 5 3000シリーズ以上
メモリ: 8GB RAM
ストレージ: 5GB 空き容量（モデル含む）
OS: Windows 10 64bit以降

予測性能:
- 遅延: 20-40秒
- CPU使用率: 40-60%
- メモリ使用量: 3-4GB
```

**推奨要件**（large-v3モデル使用時）
```
CPU: Intel Core i7 第10世代以上 / AMD Ryzen 7 3000シリーズ以上
メモリ: 16GB RAM以上
ストレージ: 10GB 空き容量
OS: Windows 10/11 64bit

予測性能:
- 遅延: 15-25秒
- CPU使用率: 50-70%
- メモリ使用量: 6-8GB
```

**高性能環境**
```
CPU: Intel Core i9 / AMD Ryzen 9
メモリ: 32GB RAM以上
ストレージ: SSD 10GB以上

予測性能:
- 遅延: 10-20秒
- CPU使用率: 40-60%
- メモリ使用量: 6-10GB
- より短いバッファ間隔での処理が可能
```

#### パフォーマンスチューニング戦略

**1. バッファサイズの調整**
```
短いバッファ（5秒）:
- メリット: 遅延が少ない
- デメリット: CPU使用率上昇、文脈が短くなり精度低下

長いバッファ（15秒）:
- メリット: CPU使用率低下、文脈が長く精度向上
- デメリット: 遅延増加
```

**2. マルチスレッド最適化**
```
推奨構成:
- メインスレッド: GUI処理
- スレッド1: 音声キャプチャ
- スレッド2: faster-whisper処理
- スレッド3: ファイル書き込み（非同期）

注意点:
- GIL（Global Interpreter Lock）の影響
- I/O操作は別スレッド化で効果大
- CPU集約処理（whisper）は並列化が難しい
```

**3. メモリ管理**
```
対策:
- 音声バッファのサイズ制限
- 処理済みデータの即時解放
- 長時間使用時のメモリリーク監視
- ガベージコレクションの明示的呼び出し

目標:
- 連続8時間使用でメモリ使�
## 実装の優先順位とロードマップ

### Phase 1: 基本機能実装（MVP - Minimum Viable Product）
**目標**: 基本的な文字起こし機能の実現
**期間**: 2-3週間

必須機能:
- [ ] 音声キャプチャ（基本）
- [ ] faster-whisper統合
- [ ] 基本的なGUI
- [ ] ファイル保存（TXT形式）
- [ ] 設定の永続化（基本）
- [ ] エラーハンドリング（基本）
- [ ] EXE化

成果物:
- 動作する基本版EXEファイル
- 基本的なREADME

### Phase 2: 機能拡張とMSI化
**目標**: ユーザビリティ向上と配布準備
**期間**: 2-3週間

追加機能:
- [ ] 言語選択機能
- [ ] 保存先指定機能
- [ ] 複数エクスポート形式（SRT, JSON）
- [ ] 音声レベルメーター
- [ ] プログレスバー
- [ ] メニューバー
- [ ] MSIインストーラー作成
- [ ] 初回セットアップウィザード

成果物:
- 機能拡張版EXEファイル
- MSIインストーラー
- ユーザーマニュアル（初版）

### Phase 3: 品質向上とセキュリティ強化
**目標**: エンタープライズレベルの品質
**期間**: 2週間

追加機能:
- [ ] 包括的なエラーハンドリング
- [ ] ログ機能
- [ ] 自動保存
- [ ] バックアップ・復旧
- [ ] ヘルプ機能
- [ ] トラブルシューティングガイド
- [ ] セキュリティ監査（ネットワーク分離確認）

成果物:
- 安定版リリース v1.0.0
- 完全なドキュメント一式
- セキュリティ検証報告書

### Phase 4: 高度な機能（オプション）
**目標**: ユーザー要望対応と差別化
**期間**: 継続的

追加機能:
- [ ] ダークモード
- [ ] 検索機能
- [ ] フォントサイズ変更
- [ ] キーボードショートカット拡張
- [ ] パフォーマンスモニター
- [ ] データ暗号化（オプション）
- [ ] 多言語UI（英語対応）

成果物:
- マイナーバージョンアップ（v1.1.0, v1.2.0...）

### 各フェーズの完了基準

**Phase 1完了基準:**
- 基本的な文字起こしが動作する
- EXEファイルが起動する
- 最低限のエラーハンドリング
- 基本的なドキュメント

**Phase 2完了基準:**
- すべての必須機能が実装されている
- MSIインストーラーでインストール可能
- ユーザーマニュアルが完成
- 別のPCで動作確認済み

**Phase 3完了基準:**
- すべてのテストが完了
- セキュリティ監査が完了（ネットワーク分離確認）
- ドキュメントが完全
- リリース可能な状態
- GitHub Releasesでリリース準備完了

**Phase 4完了基準:**
- ユーザーフィードバックに基づく改善
- 追加機能の実装
- 継続的な品質向上

## 重要な実装ガイドライン

### コーディング規約
```python
# Pythonコーディング規約（PEP 8準拠）

# 1. インポート順序
import os  # 標準ライブラリ
import sys

import numpy as np  # サードパーティ

from audio_capture import AudioCapture  # ローカルモジュール
from transcriber import Transcriber

# 2. クラス名: PascalCase
class AudioCapture:
    pass

# 3. 関数名・変数名: snake_case
def capture_audio():
    buffer_size = 1024

# 4. 定数: UPPER_CASE
MAX_BUFFER_SIZE = 4096

# 5. ドキュメンテーション
def transcribe_audio(audio_data, language="ja"):
    """
    音声データを文字起こしする
    
    Args:
        audio_data (np.ndarray): 音声データ
        language (str): 言語コード（"ja" or "en"）
    
    Returns:
        str: 文字起こし結果
    
    Raises:
        ValueError: 無効な言語コードの場合
    """
    pass

# 6. エラーハンドリング
try:
    result = transcribe_audio(data)
except Exception as e:
    logger.error(f"Transcription failed: {e}")
    raise

# 7. ロギング
import logging
logger = logging.getLogger(__name__)
logger.info("Processing started")
```

### セキュリティチェックリスト
```
実装時の必須チェック項目:

□ ネットワークライブラリ（requests, urllib等）を使用していない
□ faster-whisperのモデルロードでdownload_root=Noneを指定
□ 環境変数でプロキシ設定を無効化
□ 外部APIを呼び出していない
□ クラウドサービスに接続していない
□ テレメトリーデータを送信していない
□ すべてのファイル操作がローカルのみ
□ ログファイルもローカル保存のみ
□ クラッシュレポートもローカル保存のみ
□ 自動更新機能がない
□ オンラインヘルプへのリンクがない
```

### パフォーマンス最適化チェックリスト
```
□ 音声キャプチャと文字起こしが別スレッド
□ GUI更新が適切なタイミング
□ 大きなデータはジェネレータで処理
□ 不要なデータを即座に解放
□ バッファサイズが適切
□ メモリリークがない
□ CPU使用率が許容範囲内
□ 長時間稼働でパフォーマンス低下しない
```

### ユーザビリティチェックリスト
```
□ エラーメッセージが分かりやすい
□ 解決方法が提示されている
□ すべてのボタンにツールチップがある
□ キーボード操作が可能
□ 高DPI環境で適切に表示される
□ ヘルプが充実している
□ 初回起動時のガイドがある
□ 設定が直感的
□ フィードバックが適切（プログレスバー等）
```

## 最終チェックリスト（リリース前）

### 機能チェック
```
□ すべての必須機能が実装されている
□ すべての機能が正常に動作する
□ エラーハンドリングが適切
□ 設定が保存・復元される
□ ファイル保存が正常に動作する
□ 複数のエクスポート形式が動作する
```

### セキュリティチェック
```
□ ネットワーク無効化状態で動作する
□ Wiresharkで外部通信0件を確認
□ ファイアウォールログで外部通信なし
□ モデルファイルがローカルに存在
□ すべてのデータがローカル保存
□ セキュリティ監査完了
```

### パフォーマンスチェック
```
□ ベンチマーク目標値を達成
□ 8時間連続稼働テスト完了
□ メモリリークなし
□ CPU使用率が許容範囲
□ ストレステスト完了
```

### ドキュメントチェック
```
□ ユーザーマニュアル完成
□ README.txt完成
□ トラブルシューティングガイド完成
□ FAQ完成
□ リリースノート完成
□ 既知の問題リスト完成
```

### インストーラーチェック
```
□ EXEファイルが起動する
□ MSIインストールが成功する
□ スタートメニューに登録される
□ アンインストールが正常に動作する
□ 複数のPCで動作確認済み
□ クリーンインストール確認済み
```

### 最終リリースチェック（個人開発版）
```
□ すべてのテスト完了
□ セルフレビュー完了
□ セキュリティチェック完了（ネットワーク分離確認）
□ ドキュメント完成（README.md、CHANGELOG.md等）
□ GitHub Releasesページ作成
□ リリースノート記載
□ インストーラーと実行ファイルのアップロード
□ Issuesで報告されたバグが解決済み
□ リリース準備完了
```

---

**以上で完全な実装プロンプトです。このプロンプトをClaude Code CLIに渡してください。**

よろしくお願いします。
         │
└─────────────────────────────────────────────────┘
```

### デザイン仕様

#### UIデザイン指針
**コンセプト**: プロフェッショナル、信頼性、シンプル、視認性重視

#### カラースキーム
```
プライマリカラー:
- ベース背景: #F5F5F5 (ライトグレー)
- ウィンドウ背景: #FFFFFF (ホワイト)
- テキスト: #212121 (ダークグレー)

アクセントカラー:
- 開始ボタン: #4CAF50 (グリーン) / ホバー時: #45A049
- 停止ボタン: #F44336 (レッド) / ホバー時: #E53935
- リンク・選択: #2196F3 (ブルー)

セカンダリカラー:
- ボーダー: #E0E0E0 (ライトグレー)
- 無効状態: #BDBDBD (グレー)
- ステータスバー: #FAFAFA (オフホワイト)
```

#### タイポグラフィ
```
フォント:
- Windows標準: Yu Gothic UI (游ゴシック UI)
- フォールバック: Meiryo UI, MS Gothic

サイズ:
- タイトル/見出し: 12pt (Bold)
- 本文/ラベル: 9pt (Regular)
- 文字起こし結果: 10pt (Regular)
- ステータスバー: 8pt (Regular)
- ボタンテキスト: 10pt (Bold)

行間:
- 文字起こし表示エリア: 1.5倍
```

#### レイアウト詳細
```
ウィンドウサイズ:
- 初期サイズ: 800px × 600px
- 最小サイズ: 600px × 400px
- リサイズ可能

マージン・パディング:
- ウィンドウ内側マージン: 15px
- セクション間マージン: 10px
- ボタン間隔: 8px
- ラベルとコントロール間: 5px

コントロールサイズ:
- ドロップダウン: 幅250px、高さ28px
- テキストボックス: 幅500px、高さ28px
- ボタン: 幅100px、高さ35px
- 参照ボタン: 幅70px、高さ28px
```

#### UI要素の仕様
```
ボタン:
- 角丸: 4px
- 影: 軽いドロップシャドウ (0 2px 4px rgba(0,0,0,0.1))
- ホバー時: 明度10%増加
- クリック時: 軽く押し込まれる効果

入力フィールド:
- ボーダー: 1px solid #E0E0E0
- フォーカス時: 2px solid #2196F3
- 角丸: 3px
- パディング: 8px

スクロールバー:
- 幅: 12px
- カスタムスタイル（Windows標準でも可）
- トラック背景: #F5F5F5
- サム（つまみ）: #BDBDBD

ステータスバー:
- 高さ: 25px
- 背景: #FAFAFA
- ボーダー上部: 1px solid #E0E0E0
- アイコン表示: 状態に応じて色変化
  - 待機中: グレー
  - 処理中: グリーン（アニメーション）
  - エラー: レッド
```

#### アイコン・グラフィック
```
アプリケーションアイコン:
- サイズ: 256x256px (複数サイズ生成: 16, 32, 48, 256)
- デザイン: マイクのシンプルなアイコン + 南京錠（セキュリティ）
- カラー: ダークブルー系 (#1976D2)
- フォーマット: .ico

UI内アイコン:
- 参照ボタン: フォルダアイコン (16x16px)
- 開始: 再生アイコン (16x16px)
- 停止: 停止アイコン (16x16px)
- 状態表示: ドットまたは小さいアイコン (12x12px)

スタイル:
- Material Design Icons または Fluent UI Icons
- モノクローム（状態に応じて色変化）
```

#### アクセシビリティ
```
- 最小コントラスト比: 4.5:1 (WCAG AA準拠)
- キーボード操作対応: Tab、Enter、Space、矢印キー
- ショートカットキー:
  - Ctrl+S: 開始/停止
  - Ctrl+O: 保存先選択
  - Ctrl+L: 言語切り替え
- フォーカス表示: 明確なアウトライン
- ツールチップ: 全ての操作可能要素に説明
```

#### ブランディング要素
```
アプリ名表示:
- 位置: ウィンドウタイトルバー
- フォーマット: "OfflineVoiceLogger v1.0.0"

ロゴ配置（オプション）:
- About画面に表示
- サイズ: 128x128px
- 位置: ダイアログ中央上部

バージョン情報:
- ステータスバー右端に小さく表示
- または「ヘルプ」→「バージョン情報」メニュー
```

#### インストーラーデザイン
```
ウィザード画面:
- サイズ: 500x400px
- バナー画像: 500x60px
- サイドイメージ: 164x314px
- ボタン配置: 右下（標準的なウィザード配置）

カラースキーム:
- アプリと統一（ブルー系）
- プロフェッショナルで清潔感のある印象
```

### 実装のポイント

1. **セキュリティとオフライン動作（最優先）**
   - faster-whisperのモデルロード時に`download_root`パラメータでローカルパスを指定
   - ネットワークライブラリ（requests、urllib等）の使用を最小限に
   - コード内でHTTP/HTTPS接続を試みる箇所を完全排除
   - 環境変数でプロキシ設定を無効化
   - ファイアウォールテストの実装（外部通信の試みを検出）

2. **音声デバイスの検出**
   - Windowsのループバック音声デバイス（ステレオミキサーまたはWASAPI Loopback）を自動検出
   - デバイスが見つからない場合のエラーハンドリングとユーザーガイド表示

3. **バッファ管理**
   - 音声データを適切なサイズでバッファリング
   - オーバーラップ処理で文の途切れを防ぐ
   - メモリ効率を考慮したバッファサイズ設定

4. **パフォーマンス**
   - 音声キャプチャと文字起こしを別スレッドで実行
   - Queueを使用してスレッド間でデータをやり取り
   - CPU使用率の最適化

5. **エラーハンドリング**
   - モデルファイルが見つからない場合の対応
   - 音声デバイスが取得できない場合の対応
   - メモリ不足時の対応
   - 保存先ディレクトリの権限エラー処理

6. **MSIインストーラー設計**
   - インストール先の選択可能化
   - モデルファイルの効率的なパッケージング
   - レジストリへの適切な登録
   - アンインストール時のクリーンアップ処理
   - インストール進捗表示

7. **ユーザビリティ**
   - 初回起動時のセットアップウィザード
   - 分かりやすいエラーメッセージ
   - 日本語UIの適切な表示（フォント設定）

### 実装手順

1. 必要なライブラリのインストールスクリプト作成
2. **faster-whisperモデルの事前ダウンロード**
   - large-v3モデルをローカルにダウンロード
   - models/ディレクトリに配置
   - モデルファイルのパス設定（ローカルパス使用）
3. 音声キャプチャモジュールの実装
   - WASAPIループバック音声のキャプチャ
   - リアルタイムバッファリング
   - **ネットワークアクセスなしで動作確認**
4. 文字起こしモジュールの実装
   - faster-whisperの初期化（ローカルモデルを使用）
   - バッファからの音声データ処理
   - 言語切り替え機能
   - **外部通信を行わないことを確認**
5. GUIの実装
   - 基本的なウィンドウ作成
   - リアルタイム表示機能
   - デバイス選択とコントロール
   - **言語選択ドロップダウン（日本語/英語）**
   - **保存先指定機能**
     - パス表示用テキストボックス
     - フォルダ参照ダイアログ（tkinter.filedialog.askdirectory）
     - 保存先の検証とエラーハンドリング
6. **ローカル環境専用動作の検証**
   - ネットワークを無効化した状態でのテスト
   - すべての機能が外部通信なしで動作することを確認
   - ファイアウォールログで外部接続の試みがないことを確認
7. メインプログラムの統合とテスト
8. **EXE化**
   - PyInstallerの設定ファイル（.spec）作成
   - モデルファイルを含めたEXEビルド
   - `pyinstaller --onefile --windowed --add-data "models;models" main.py`
   - 動作確認（ネットワーク無効化状態でテスト）
9. **MSIインストーラーの作成**
   - WiX ToolsetまたはInno Setupの設定ファイル作成
   - インストーラーのビルド
   - インストール/アンインストールのテスト
   - 別のクリーンなPCでの動作確認
   - **ネットワーク無効化状態でのインストール・動作テスト**
10. **エンドユーザー向けドキュメント作成**
    - README.txt（セキュリティ要件を明記）
    - インストールガイド
    - 使用方法マニュアル
11. **最終リリースパッケージ作成**
    - MSIファイル
    - README.txt
    - インストールガイドPDF（オプション）
    - 配布用ZIP作成

### 注意事項

#### セキュリティ関連（最重要）
- **完全オフライン動作必須**
  - インターネット接続を一切行わない設計
  - faster-whisperのモデルファイルは事前ダウンロードしてインストーラーに同梱
  - 初回起動時も外部通信なしで動作
  - コード内でネットワーク接続を試みる部分は完全に削除または無効化
- **データの機密性保護**
  - すべての音声データと文字起こし結果はローカルストレージのみに保存
  - クラウドサービスへの接続機能は一切実装しない
  - 一時ファイルも含め、すべてのデータをローカルで完結
- **検証方法**
  - ネットワークアダプタを無効化した状態でのテスト必須
  - Wiresharkやファイアウォールログで外部通信がないことを確認
  - 社外秘情報を扱うため、データ流出リスクゼロを保証

#### 技術要件
- Windows 10/11 (64bit)環境での実行を想定
- Python 3.9以上を推奨（開発時）
- CPUのみで動作（GPU不使用）
- 推奨スペック
  - CPU: Intel Core i5以上（第8世代以降）
  - メモリ: 8GB以上（16GB推奨）
  - ストレージ空き容量: 5GB以上（モデルファイル含む）

#### EXE化・インストーラー関連
- **MSIインストーラー**
  - 管理者権限でのインストールが必要
  - Program Filesへのインストール
  - スタートメニューへの自動登録
  - アンインストール機能完備
- **EXEファイル**
  - ファイルサイズが大きい（1-3GB程度、モデル含む）
  - ウイルス対策ソフトに誤検知される可能性
    - コード署名の検討
    - Windows Defenderの除外設定案内
  - 初回起動時の動作確認必須

#### 保存先とファイル管理
- 保存先ディレクトリへの書き込み権限を確認
- 無効なパスが指定された場合のエラーハンドリング
- ファイル名の重複処理（タイムスタンプ付与など）
- ファイル名に機密度マーク（CONFIDENTIAL等）を自動付与するオプション検討

#### モデルファイル管理
- faster-whisperのlarge-v3モデル（約3GB）をインストーラーに同梱
- インストール時に適切な場所（Program Files配下）に配置
- モデルファイルの整合性チェック機能の実装を推奨

### オプション機能（余裕があれば）

#### セキュリティ強化
- ファイル名に機密度マーク自動付与（CONFIDENTIAL、SECRET等）
- 保存ファイルの暗号化（AES-256）
- アクセスログ記録（誰がいつ使用したか）
- パスワード保護起動オプション

#### 機能拡張
- 文字起こし結果の編集機能（GUI上で直接編集）
- ファイル名のカスタマイズ機能（接頭辞、日時形式など）
- 音声の録音機能（デバッグ用、WAVファイルとして保存）
- 複数形式でのエクスポート（TXT、SRT、VTT、DOCX）
- 設定ファイル（config.ini）でモデルサイズやバッファサイズを変更可能に
- 言語の自動検出機能
- 話者分離（pyannoteを使用、ローカル動作のみ）
- ダークモード対応
- 多言語UI（日本語/英語切り替え）

#### 管理機能
- 使用統計の表示（処理時間、ファイル数など、ローカル保存のみ）
- バックアップ・復元機能
- 一括処理機能（複数音声ファイルの処理）

**注意**: 以下の機能は実装しないこと
- ❌ 自動更新チェック機能（外部通信が必要）
- ❌ クラウドストレージ連携
- ❌ オンライン辞書連携
- ❌ テレメトリー送信
- ❌ 外部APIとの連携


## 詳細設計情報

### データ構造設計

#### 文字起こし結果のデータ構造
```json
{
  "metadata": {
    "version": "1.0.0",
    "created_at": "2025-11-09T10:30:00",
    "device_name": "Stereo Mix",
    "language": "ja",
    "model": "large-v3",
    "duration_seconds": 3600
  },
  "segments": [
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
  ],
  "statistics": {
    "total_segments": 150,
    "total_characters": 4500,
    "average_confidence": 0.93
  }
}
```

#### 設定ファイル（config.ini）の構造
```ini
[General]
version = 1.0.0
first_run = False
language = ja

[Audio]
device_name = Stereo Mix
sample_rate = 16000
buffer_size_seconds = 10
vad_threshold = 0.5

[Transcription]
model = large-v3
language = ja
beam_size = 5
vad_filter = True
hallucination_threshold = 0.2

[UI]
window_width = 800
window_height = 600
window_x = 100
window_y = 100
font_size = 10
theme = light
auto_scroll = True

[Files]
save_directory = C:\Users\{username}\Documents\OfflineVoiceLogger
file_name_template = transcript_{YYYYMMDD}_{HHMMSS}.txt
auto_save_enabled = True
auto_save_interval_minutes = 5
encoding = utf-8

[Storage]
max_memory_usage_mb = 1024
max_buffer_size_seconds = 30
disk_warning_threshold_mb = 500
disk_critical_threshold_mb = 100
auto_cleanup_enabled = True
max_backup_files = 10
max_log_files = 5
max_crash_reports = 10
debug_audio_save_enabled = False
temp_directory = %TEMP%\OfflineVoiceLogger

[Advanced]
log_level = INFO
max_log_files = 5
max_backup_files = 10
show_performance_monitor = False
```

#### ログファイルのフォーマット
```
[2025-11-09 10:30:15.234] [INFO] [MainWindow] Application started
[2025-11-09 10:30:16.123] [INFO] [AudioCapture] Initializing audio device: Stereo Mix
[2025-11-09 10:30:17.456] [INFO] [Transcriber] Loading model: large-v3
[2025-11-09 10:30:25.789] [INFO] [Transcriber] Model loaded successfully
[2025-11-09 10:30:30.123] [INFO] [AudioCapture] Recording started
[2025-11-09 10:30:40.234] [INFO] [Transcriber] Processing buffer (10.0s)
[2025-11-09 10:31:05.345] [INFO] [Transcriber] Transcription complete: 45 characters
[2025-11-09 10:31:05.346] [WARNING] [AudioCapture] Buffer overflow detected, dropping 0.2s
[2025-11-09 10:35:00.123] [INFO] [FileManager] Auto-save completed: transcript_20251109_103000.txt
[2025-11-09 10:40:00.234] [ERROR] [AudioCapture] Device disconnected: Stereo Mix
[2025-11-09 10:40:00.456] [INFO] [AudioCapture] Attempting to reconnect...
```

### セキュリティ設計の詳細

#### ネットワーク通信の防止策
```python
# 実装例: ネットワークアクセスを完全に無効化

import os
import sys

# 環境変数でネットワークを無効化
os.environ['no_proxy'] = '*'
os.environ['NO_PROXY'] = '*'
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

# faster-whisperでローカルモデルのみ使用
model = WhisperModel(
    model_size_or_path="./models/large-v3",  # ローカルパス指定
    device="cpu",
    compute_type="int8",
    download_root=None,  # ダウンロード無効化
    local_files_only=True  # ローカルファイルのみ使用
)

# ネットワーク接続の試みを検出
def check_network_access():
    """ネットワークアクセスの試みを検出し、ログに記録"""
    # ファイアウォールログの監視（オプション）
    pass
```

#### データ暗号化（オプション機能）
```python
# 保存ファイルの暗号化（オプション）
from cryptography.fernet import Fernet

def encrypt_file(file_path, key):
    """ファイルを暗号化"""
    f = Fernet(key)
    with open(file_path, 'rb') as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    
    with open(file_path + '.enc', 'wb') as file:
        file.write(encrypted_data)

def decrypt_file(file_path, key):
    """ファイルを復号化"""
    f = Fernet(key)
    with open(file_path, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data
```

#### アクセス制御
```
- 保存先ディレクトリの権限チェック
- 管理者権限不要での動作
- ユーザープロファイル配下のみアクセス
- システムファイルへのアクセス禁止
```

### テスト計画

#### 単体テスト
```
テストフレームワーク: pytest

テスト対象:
1. 音声キャプチャモジュール
   - デバイス検出
   - 音声バッファリング
   - デバイス再接続

2. 文字起こしモジュール
   - モデルロード
   - 音声→テキスト変換
   - 言語切り替え

3. ファイル保存モジュール
   - ファイル書き込み
   - エンコーディング変換
   - エクスポート形式変換

4. 設定管理モジュール
   - 設定の読み書き
   - デフォルト値の適用
   - バリデーション

5. エラーハンドリング
   - 各種エラー状況のシミュレーション
   - エラーメッセージの検証
```

#### 統合テスト
```
1. エンドツーエンドテスト
   - 起動→録音→文字起こし→保存→終了

2. 長時間稼働テスト
   - 8時間連続稼働
   - メモリリークチェック
   - パフォーマンス劣化チェック

3. ストレステスト
   - 大量データ処理
   - 高負荷状態での動作
   - リソース制限下での動作
```

#### セキュリティテスト
```
1. ネットワーク分離テスト
   - ネットワークアダプタ無効化状態での動作確認
   - Wiresharkでのパケットキャプチャ（0件確認）
   - ファイアウォールログの確認

2. データ漏洩テスト
   - 一時ファイルの確認
   - レジストリエントリの確認
   - プロセス間通信の確認

3. 脆弱性スキャン
   - 使用ライブラリの脆弱性チェック
   - バッファオーバーフローチェック
```

#### ユーザビリティテスト
```
1. 初心者ユーザーテスト
   - インストールの容易性
   - 初回起動の分かりやすさ
   - 基本操作の習得時間

2. エラー回復テスト
   - エラーメッセージの分かりやすさ
   - 回復手順の明確さ

3. アクセシビリティテスト
   - キーボード操作のみでの使用
   - 高DPI環境での表示
   - ダークモードの視認性
```

### デプロイメント戦略

#### ビルドパイプライン
```
1. ソースコード準備
   - GitHubからのチェックアウト
   - バージョン番号の更新

2. モデルファイル準備
   - faster-whisper large-v3のダウンロード
   - models/ディレクトリへの配置
   - チェックサムの確認

3. EXEビルド
   - PyInstallerでのビルド
   - 依存関係の確認
   - 起動テスト

4. MSIビルド
   - WiX Toolsetでのビルド
   - インストール/アンインストールテスト
   - 署名（オプション）

5. パッケージング
   - ZIPファイルの作成
   - README.txtの同梱
   - チェックサムファイルの生成

6. 配布
   - 社内共有フォルダへのアップロード
   - バージョン管理
   - 配布記録
```

#### リリースチェックリスト
```
□ 単体テスト完了
□ 統合テスト完了
□ セキュリティテスト完了（ネットワーク分離確認）
□ ユーザビリティテスト完了
□ ドキュメント作成完了
□ モデルファイル同梱確認
□ EXEファイル動作確認
□ MSIインストーラー動作確認
□ アンインストール動作確認
□ 別のクリーンPCでの動作確認
□ ウイルススキャン完了
□ バージョン番号確認
□ CHANGELOG.md更新
□ README.md更新
□ GitHub Releasesでリリースページ作成
```

### メンテナンス計画

#### バージョン管理
```
バージョン番号形式: MAJOR.MINOR.PATCH

MAJOR: 大きな機能追加や互換性のない変更
MINOR: 新機能追加（後方互換性あり）
PATCH: バグフィックスや小さな改善

リリースサイクル:
- メジャーバージョン: 年1回
- マイナーバージョン: 四半期ごと
- パッチバージョン: 必要に応じて
```

#### バグ修正フロー（GitHub Issues経由）
```
1. バグ報告受付
   - GitHub Issuesでバグレポートを作成
   - Issueラベルで分類（bug, critical, enhancement等）
   - 再現手順、環境情報を確認

2. 優先度判定（ラベルで管理）
   - critical: アプリがクラッシュ、データ損失等 → 可能な限り早急に対応
   - high: 主要機能が使用不可 → 1-2週間以内に対応
   - medium: 機能に問題があるが回避策あり → 次回マイナーバージョン
   - low: 軽微な問題、UI改善等 → 次回メジャーバージョン

3. 修正とテスト
   - ブランチ作成（fix/issue-番号-説明）
   - 修正実装
   - 単体テストの追加・更新
   - リグレッションテスト
   - セルフレビュー

4. マージとリリース
   - mainブランチへマージ
   - パッチバージョンのリリース（critical/highの場合）
   - リリースノート作成（CHANGELOG.md更新）
   - GitHub Releasesでリリース
   - Issueをクローズ（Fixed in vX.X.X）

5. フォローアップ
   - バグ報告者に修正を通知
   - 必要に応じてドキュメント更新
```

#### ドキュメント更新
```
更新対象:
- README.md（メイン説明、インストール手順、使い方）
- CHANGELOG.md（バージョン履歴、変更内容）
- docs/（詳細ドキュメント）
  - user-guide.md（ユーザーガイド）
  - troubleshooting.md（トラブルシューティング）
  - faq.md（FAQ）
  - contributing.md（貢献ガイド）※オープンソースの場合
- GitHub Wiki（オプション）
- 既知の問題リスト（GitHub Issues の Known Issues ラベル）

更新タイミング:
- 新機能追加時: README.md、CHANGELOG.md、user-guide.md
- バグ修正時: CHANGELOG.md、troubleshooting.md（必要に応じて）
- よくある質問の追加時: faq.md、README.mdのFAQセクシ�
## 追加情報: 音声データ管理とGitHub運用

### 音声データ管理の実装詳細

#### メモリとディスク容量の監視実装例
```python
import psutil
import os

class ResourceMonitor:
    """システムリソースの監視クラス"""
    
    def __init__(self, warning_threshold_mb=500, critical_threshold_mb=100):
        self.disk_warning_threshold = warning_threshold_mb * 1024 * 1024  # bytes
        self.disk_critical_threshold = critical_threshold_mb * 1024 * 1024
        self.memory_warning_threshold = 0.8  # 80%
        self.memory_critical_threshold = 0.9  # 90%
    
    def check_disk_space(self, path):
        """ディスク空き容量をチェック"""
        stat = psutil.disk_usage(path)
        free_bytes = stat.free
        
        if free_bytes < self.disk_critical_threshold:
            return "critical", free_bytes
        elif free_bytes < self.disk_warning_threshold:
            return "warning", free_bytes
        else:
            return "ok", free_bytes
    
    def check_memory_usage(self):
        """メモリ使用状況をチェック"""
        memory = psutil.virtual_memory()
        usage_percent = memory.percent / 100.0
        
        if usage_percent > self.memory_critical_threshold:
            return "critical", usage_percent
        elif usage_percent > self.memory_warning_threshold:
            return "warning", usage_percent
        else:
            return "ok", usage_percent
    
    def get_temp_directory_size(self, temp_dir):
        """一時ディレクトリのサイズを取得"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(temp_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size

# 使用例
monitor = ResourceMonitor()

# 録音開始時のチェック
status, free_space = monitor.check_disk_space("C:\\")
if status == "critical":
    # エラーダイアログを表示して録音を中止
    show_error("ディスク容量が不足しています。最低100MB必要です。")
elif status == "warning":
    # 警告を表示するが録音は継続可能
    show_warning("ディスク容量が少なくなっています。")

# メモリチェック
mem_status, mem_usage = monitor.check_memory_usage()
if mem_status == "critical":
    # バッファサイズを縮小、軽量モデルへの切り替えを提案
    reduce_buffer_size()
    suggest_lighter_model()
```

#### 音声バッファの自動管理実装例
```python
import collections
import numpy as np
import threading
import queue

class AudioBufferManager:
    """音声バッファの管理クラス"""
    
    def __init__(self, max_memory_mb=1024, buffer_seconds=10, sample_rate=16000):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.buffer_seconds = buffer_seconds
        self.sample_rate = sample_rate
        self.max_samples = buffer_seconds * sample_rate
        
        # バッファ（dequeで効率的なFIFO）
        self.buffer = collections.deque(maxlen=self.max_samples)
        self.lock = threading.Lock()
        
        # 処理キュー
        self.processing_queue = queue.Queue()
    
    def add_audio_data(self, audio_chunk):
        """音声データをバッファに追加"""
        with self.lock:
            # メモリ使用量をチェック
            current_memory = self.get_current_memory_usage()
            
            if current_memory > self.max_memory_bytes:
                # メモリ不足: 古いデータをフラッシュ
                self.flush_oldest_data()
            
            # 新しいデータを追加
            self.buffer.extend(audio_chunk)
    
    def get_buffer_for_transcription(self):
        """文字起こし用にバッファを取得"""
        with self.lock:
            if len(self.buffer) >= self.max_samples:
                # バッファが満杯: データを取り出して返す
                audio_data = np.array(list(self.buffer))
                self.buffer.clear()  # バッファをクリア
                return audio_data
            else:
                return None
    
    def get_current_memory_usage(self):
        """現在のメモリ使用量を計算（バイト）"""
        # numpy配列のサイズを計算
        if len(self.buffer) > 0:
            sample = np.array(list(self.buffer)[:100])
            bytes_per_sample = sample.itemsize
            return len(self.buffer) * bytes_per_sample
        return 0
    
    def flush_oldest_data(self):
        """古いデータをフラッシュ"""
        flush_count = len(self.buffer) // 4  # 25%をフラッシュ
        for _ in range(flush_count):
            if self.buffer:
                self.buffer.popleft()
    
    def cleanup(self):
        """クリーンアップ"""
        with self.lock:
            self.buffer.clear()
```

### GitHub運用ガイド

#### リポジトリ構造
```
OfflineVoiceLogger/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── question.md
│   └── workflows/
│       ├── build.yml       # CI/CD（ビルド＆テスト）
│       └── release.yml     # リリース自動化
├── src/
│   ├── main.py
│   ├── audio_capture.py
│   ├── transcriber.py
│   ├── gui.py
│   └── ...
├── tests/
│   ├── test_audio_capture.py
│   ├── test_transcriber.py
│   └── ...
├── docs/
│   ├── user-guide.md
│   ├── troubleshooting.md
│   └── faq.md
├── installer/
│   ├── installer.wxs
│   └── build_msi.bat
├── models/
│   └── .gitkeep        # モデルファイルは.gitignoreで除外
├── .gitignore
├── README.md
├── CHANGELOG.md
├── LICENSE
├── requirements.txt
└── pyproject.toml      # プロジェクト設定
```

#### Issueテンプレート例

**Bug Report (.github/ISSUE_TEMPLATE/bug_report.md)**
```markdown
---
name: Bug Report
about: バグを報告する
title: '[BUG] '
labels: bug
assignees: ''
---

## バグの説明
バグの内容を簡潔に説明してください。

## 再現手順
1. 
2. 
3. 

## 期待される動作
何が起こるべきだったかを説明してください。

## 実際の動作
実際に何が起こったかを説明してください。

## 環境
- OS: [例: Windows 11 Pro 64bit]
- アプリバージョン: [例: v1.0.0]
- CPU: [例: Intel Core i7-12650H]
- メモリ: [例: 16GB]

## エラーメッセージ（あれば）
```
エラーメッセージをここに貼り付けてください
```

## ログファイル（あれば）
ログファイル（%APPDATA%\OfflineVoiceLogger\logs\app.log）の関連部分を添付してください。

## スクリーンショット（あれば）
問題を示すスクリーンショットを添付してください。

## 追加情報
その他、役立つ可能性のある情報を記載してください。
```

**Feature Request (.github/ISSUE_TEMPLATE/feature_request.md)**
```markdown
---
name: Feature Request
about: 新機能を提案する
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## 機能の説明
実装してほしい機能を説明してください。

## ユースケース
この機能がどのような場面で役立つか説明してください。

## 提案する実装方法（あれば）
実装方法のアイデアがあれば記載してください。

## 代替案（あれば）
他に検討した方法があれば記載してください。

## 追加情報
その他、役立つ可能性のある情報を記載してください。
```

#### GitHub Actions CI/CD例

**.github/workflows/build.yml**
```yaml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

#### リリースプロセス

**ステップ1: バージョンアップ**
```bash
# バージョン番号を更新
# src/__version__.py または pyproject.toml

# CHANGELOG.mdを更新
## [1.1.0] - 2025-11-09
### Added
- 新機能1
- 新機能2
### Fixed
- バグ修正1
### Changed
- 変更1
```

**ステップ2: コミットとタグ**
```bash
git add .
git commit -m "Release v1.1.0"
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main
git push origin v1.1.0
```

**ステップ3: GitHub Releasesでリリース**
```
1. GitHubリポジトリのReleasesページへ
2. "Draft a new release"をクリック
3. タグを選択: v1.1.0
4. リリースタイトル: "OfflineVoiceLogger v1.1.0"
5. リリースノートを記載（CHANGELOG.mdから転記）
6. バイナリファイルをアップロード:
   - OfflineVoiceLogger_v1.1.0.msi
   - OfflineVoiceLogger_v1.1.0.zip
7. "Publish release"をクリック
```

#### コミュニティ対応

**プルリクエストの受け入れ**
```markdown
# CONTRIBUTING.md を作成

## プルリクエストの手順
1. フォークする
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## コーディング規約
- PEP 8に準拠
- 型ヒントを使用
- docstringを記載
- テストを追加

## テストの実行
```bash
pytest tests/
```
```

---

**以上が音声データ管理とGitHub運用の追加情報です。個人開発に最適化された完全なプロンプトが完成しました。**

