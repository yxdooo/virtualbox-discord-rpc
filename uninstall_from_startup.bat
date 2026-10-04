@echo off
echo Removing VirtualBox Discord Rich Presence from Windows Startup...
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\VirtualBoxDiscordRPC.lnk" 2>nul
echo [OK] Removed from Startup.
timeout /t 2 >nul
