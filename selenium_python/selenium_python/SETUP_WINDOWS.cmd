@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
where py >nul 2>&1
if errorlevel 1 goto use_python
py -3 -m venv .venv
goto venv_done
:use_python
python -m venv .venv
:venv_done
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" run_labs.py --check %*
if errorlevel 1 goto failed
echo Setup and environment check completed. Use START_LABS.cmd for class.
pause
exit /b 0
:failed
echo Setup failed. Read the message above and README.md.
echo Python 3.10+ and Chrome are required. Edge: SETUP_WINDOWS.cmd --browser edge
pause
exit /b 1
