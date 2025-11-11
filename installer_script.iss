; Inno Setup Script for OfflineVoiceLogger
; このスクリプトを使用するには、Inno Setupをインストールしてください
; https://jrsoftware.org/isdl.php

#define MyAppName "OfflineVoiceLogger"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "OfflineVoiceLogger Project"
#define MyAppURL "https://github.com/yourproject/OfflineVoiceLogger"
#define MyAppExeName "OfflineVoiceLogger.exe"

[Setup]
; アプリケーション情報
AppId={{68a8b756-fa1c-430e-a11a-43a0ede6e945}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; ライセンスファイル（後で作成）
LicenseFile=LICENSE.txt
; 出力設定
OutputDir=installer_output
OutputBaseFilename=OfflineVoiceLogger_Setup_v{#MyAppVersion}
; アイコン設定
SetupIconFile=app_icon.ico
; 圧縮
Compression=lzma
SolidCompression=yes
; Windows Vista以降
MinVersion=6.1
; 64ビット版のみ
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; 権限
PrivilegesRequired=lowest
; アンインストーラ設定
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; メインアプリケーション（PyInstallerの出力）
Source: "dist\OfflineVoiceLogger\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; ドキュメント
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "AUDIO_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion
; large-v3モデル（2.9GB）
Source: "models\large-v3\*"; DestDir: "{app}\models\large-v3"; Flags: ignoreversion recursesubdirs createallsubdirs
; モデルダウンロードスクリプト（バックアップ用）
Source: "download_base_model.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "download_medium_model.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "auto_download_model.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  if not IsDotNetInstalled(net45, 0) then begin
    MsgBox('Microsoft .NET Framework 4.5 以降が必要です。' + #13#13 +
           'インストールを続行するには、先に .NET Framework をインストールしてください。',
           mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // インストール後のメッセージ
    MsgBox('インストールが完了しました！' + #13#13 +
           '✓ Whisper large-v3モデルが同封されています。' + #13 +
           '✓ すぐに高精度な文字起こしを開始できます。' + #13#13 +
           'アプリケーションを起動して、音声デバイスを選択してください。',
           mbInformation, MB_OK);
  end;
end;
