@echo off
setlocal
rem ExecutionPolicy applies only to this recording process, never the user's settings.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Record-Windows-Session.ps1"
set "night_tide_record_exit=%ERRORLEVEL%"
if not "%night_tide_record_exit%"=="0" echo Recording incomplete. Keep the results folder and this message.
pause
exit /b %night_tide_record_exit%
