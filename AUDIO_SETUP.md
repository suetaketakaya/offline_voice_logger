# オーディオデバイスの設定ガイド

## 対応デバイスタイプ

### 1. マイク入力
通常のマイクデバイスから音声をキャプチャします。
- 使用例: 会議での発言、音声メモ、インタビュー

### 2. スクリーンキャプチャー/システムオーディオ（ループバック）
**画面録画の音声**や**PC全体の音声**をキャプチャします。
- ステレオミキサー
- Stereo Mix
- What U Hear

#### スクリーンキャプチャーの使い方
1. オーディオデバイスで「スクリーンキャプチャー/システムオーディオ」と表示されているデバイスを選択
2. 録音開始ボタンをクリック
3. 画面上で再生される動画、ブラウザ、Teams等の音声が自動的に文字起こしされます

**注意**: システムオーディオを選択すると、PC全体の音（通知音、BGMなど）もすべて録音されます。

## アプリケーション固有のオーディオキャプチャ

ブラウザやTeamsなど、特定のアプリケーションのみの音声をキャプチャする場合は、以下の方法があります：

### 方法1: Virtual Audio Cable (推奨)
1. Virtual Audio Cable (VB-Cable) をインストール
   - ダウンロード: https://vb-audio.com/Cable/
2. アプリケーション（ブラウザ、Teamsなど）のオーディオ出力をVirtual Cableに設定
3. OfflineVoiceLoggerでVirtual Cableを入力デバイスとして選択

### 方法2: Voicemeeter
1. Voicemeeter をインストール
   - ダウンロード: https://vb-audio.com/Voicemeeter/
2. Voicemeeterでオーディオルーティングを設定
3. 特定のアプリケーションの出力をVoicemeeterの特定チャンネルに割り当て
4. OfflineVoiceLoggerでVoicemeeter Outputを入力デバイスとして選択

### 方法3: Windows 11のアプリ音量設定
Windows 11では、アプリごとの音量とデバイス設定が可能です：
1. 設定 > システム > サウンド > アプリの音量とデバイスの設定
2. 特定のアプリの出力デバイスを変更
3. Virtual Audio Cableなどの仮想デバイスに割り当て

## 設定例

### Teamsの会議を文字起こしする場合
1. Virtual Audio Cable (VB-Cable) をインストール
2. Teamsの設定でスピーカーを「CABLE Input」に変更
3. OfflineVoiceLoggerでデバイスを「CABLE Output」に選択
4. 録音開始

### ブラウザの動画を文字起こしする場合
1. Voicemeeterをインストール
2. ブラウザのオーディオ出力をVoicemeeter Inputに設定
3. OfflineVoiceLoggerで「Voicemeeter Output」を選択
4. 録音開始
