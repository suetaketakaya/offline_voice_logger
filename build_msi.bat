@echo off
chcp 65001 >nul
echo ==========================================
echo OfflineVoiceLogger MSIビルドスクリプト
echo ==========================================
echo.

REM WiX Toolsetのパスを設定
set WIX_PATH=C:\Program Files (x86)\WiX Toolset v3.14\bin
set PATH=%WIX_PATH%;%PATH%

REM WiXがインストールされているか確認
where candle.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] WiX Toolsetが見つかりません
    echo.
    echo WiX Toolsetをインストールしてください:
    echo https://github.com/wixtoolset/wix3/releases
    echo.
    pause
    exit /b 1
)

echo [1/5] WiX Toolset確認...
echo       WiX Toolset: OK
echo.

echo [2/5] 出力ディレクトリ作成...
if not exist "msi_output" mkdir msi_output
if not exist "wix_obj" mkdir wix_obj
echo       ディレクトリ作成: OK
echo.

echo [3/5] Heat.exeでファイル一覧を生成中...
echo       これには数分かかる場合があります...
heat dir "dist\OfflineVoiceLogger" -cg DistFiles -gg -sfrag -srd -sr -template fragment -out "DistFiles.wxs" -dr INSTALLFOLDER -var var.DistDir

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Heat.exeでエラーが発生しました
    pause
    exit /b 1
)

heat dir "models\large-v3" -cg ModelFiles -gg -sfrag -srd -sr -template fragment -out "ModelFiles.wxs" -dr INSTALLFOLDER -var var.ModelDir

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Heat.exeでエラーが発生しました（モデルファイル）
    pause
    exit /b 1
)

echo       ファイル一覧生成: OK
echo.

echo [4/5] Candle.exeでコンパイル中...
candle Product.wxs DistFiles.wxs ModelFiles.wxs -out wix_obj\ -ext WixUIExtension -ext WixUtilExtension -dDistDir="dist\OfflineVoiceLogger" -dModelDir="models\large-v3" -arch x64

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Candle.exeでエラーが発生しました
    pause
    exit /b 1
)

echo       コンパイル: OK
echo.

echo [5/5] Light.exeでMSI作成中...
echo       これには10-15分かかります（large-v3モデル同梱のため）...
light wix_obj\Product.wixobj wix_obj\DistFiles.wixobj wix_obj\ModelFiles.wixobj -out msi_output\OfflineVoiceLogger_v1.0.0.msi -ext WixUIExtension -ext WixUtilExtension -cultures:ja-JP -loc Product_ja-JP.wxl

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Light.exeでエラーが発生しました
    pause
    exit /b 1
)

echo.
echo [SUCCESS] MSI作成完了！
echo.
echo 出力先: msi_output\OfflineVoiceLogger_v1.0.0.msi
echo.
dir /B msi_output\OfflineVoiceLogger_v1.0.0.msi
echo.

echo ==========================================
echo ビルド完了
echo ==========================================
echo.
echo 次のステップ:
echo 1. MSIファイルをテストインストール
echo 2. アンインストールをテスト
echo 3. GitHub Releasesにアップロード
echo.
pause
