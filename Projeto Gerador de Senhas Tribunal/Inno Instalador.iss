[Setup]
AppName=Sistema de Senhas
AppVersion=1.0
AppPublisher=Cartório
DefaultDirName={pf}\SistemaSenhasCartorio
DefaultGroupName=Cartório
OutputDir=dist
OutputBaseFilename=instalador_cartorio
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
DisableWelcomePage=no
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
SetupIconFile="C:\Users\Juliano\OneDrive - FAESA\Área de Trabalho\Nova pasta\dist\assinatura.ico"
UninstallDisplayIcon={app}\assinatura.ico

[Files]
Source: "C:\Users\Juliano\OneDrive - FAESA\Área de Trabalho\Nova pasta\dist\Gerador_Senhas.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Juliano\OneDrive - FAESA\Área de Trabalho\Nova pasta\dist\assinatura.ico"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}"; Permissions: everyone-full

[Icons]
Name: "{group}\Sistema de Senhas"; Filename: "{app}\Gerador_Senhas.exe"; IconFilename: "{app}\assinatura.ico"
Name: "{commondesktop}\Sistema de Senhas"; Filename: "{app}\Gerador_Senhas.exe"; IconFilename: "{app}\assinatura.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Opções adicionais:"

[Run]
Filename: "{app}\Gerador_Senhas.exe"; Description: "Executar o programa agora"; Flags: nowait postinstall skipifsilent runasoriginaluser