@echo off
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq " 2>nul
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*virtualbox_rpc*' -or $_.CommandLine -like '*vbox_rpc*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" 2>nul
