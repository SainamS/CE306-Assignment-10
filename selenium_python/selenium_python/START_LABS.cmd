@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo The instructor must run SETUP_WINDOWS.cmd before class.
  echo See README.md for installation and macOS/Linux commands.
  pause
  exit /b 2
)
".venv\Scripts\python.exe" run_labs.py %*
set "lab_exit=%ERRORLEVEL%"
pause
exit /b %lab_exit%
