$ws = New-Object -ComObject WScript.Shell
$startupFolder = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupFolder "VirtualBoxDiscordRPC.lnk"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$shortcut = $ws.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "C:\Python314\pythonw.exe"
$shortcut.Arguments = "`"$scriptDir\vbox_rpc.py`""
$shortcut.WorkingDirectory = $scriptDir
$shortcut.Description = "Oracle VM VirtualBox Discord Rich Presence"
$shortcut.Save()

Write-Host "[OK] Added to Windows Startup: $shortcutPath" -ForegroundColor Green
