@echo off
chcp 65001 >nul
setlocal
if not exist "%~dp0night-tide.exe" (
  echo Keep this file beside night-tide.exe and night-tide.pck.
  pause
  exit /b 2
)
echo Local automated test. Existing campaign saves are not used.
echo Please keep the external display connected. The test will close the game when finished.
set "night_tide_log=%TEMP%\night-tide-acceptance-%RANDOM%-%RANDOM%.log"
start "" /wait "%~dp0night-tide.exe" --log-file "%night_tide_log%" -- --acceptance-test
set "night_tide_exit=%ERRORLEVEL%"
findstr /C:"NATIVE_ACCEPTANCE: passed=true windows=true" "%night_tide_log%" >nul
if errorlevel 1 (
  echo Automated test failed or did not finish. Read the log below.
  set "night_tide_exit=1"
) else (
  echo Native Windows automated checks passed. Human sound and usability review remain separate.
)
echo Test exit code: %night_tide_exit%
echo Log: %night_tide_log%
explorer "%APPDATA%\Godot\app_userdata\夜潮事务所\diagnostics"
pause
exit /b %night_tide_exit%
