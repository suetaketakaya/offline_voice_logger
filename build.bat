@echo off
chcp 65001 >nul
echo ==========================================
echo OfflineVoiceLogger ビルドスクリプト
echo ==========================================
echo.

echo [1/3] クリーンアップ...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo       クリーンアップ完了

echo.
echo [2/3] PyInstallerでEXE作成中...
echo       これには数分かかる場合があります...
pyinstaller OfflineVoiceLogger.spec

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ビルドに失敗しました
    pause
    exit /b 1
)

echo.
echo [3/3] 完了確認...
if exist "dist\OfflineVoiceLogger\OfflineVoiceLogger.exe" (
    echo [SUCCESS] ビルド成功！
    echo.
    echo 出力先: dist\OfflineVoiceLogger\
    echo EXEファイル: dist\OfflineVoiceLogger\OfflineVoiceLogger.exe
) else (
    echo [ERROR] EXEファイルが見つかりません
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ビルド完了
echo ==========================================
echo.
echo 次のステップ:
echo 1. dist\OfflineVoiceLogger\ フォルダにモデルをコピー
echo 2. Inno Setupでインストーラを作成
echo    (installer_script.iss を実行)
echo.
pause
