@echo off
setlocal
cd /d "%~dp0"
title ZhiShuCiXun 3.0 - One Click Start
echo ============================================
echo    ZhiShuCiXun 3.0 (CET-4 adaptive learning)
echo    One-click start for a NEW computer
echo ============================================
echo.

set "PORT=8002"
set "URL=http://127.0.0.1:%PORT%"

rem ---- if already running, just open browser ----
powershell -NoProfile -Command "(Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue) -ne $null" >nul 2>&1
if %errorlevel%==0 goto already

rem ---- find Python 3.12+ ----
set "PY="
python --version >nul 2>&1 && set "PY=python"
if not defined PY py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY (
  echo [ERROR] Python 3.12+ was not found.
  echo Install Python 3.12 from https://www.python.org/downloads/
  echo and tick "Add python.exe to PATH". Then run this file again.
  pause
  exit /b 1
)

rem ---- rebuild venv if missing or broken ----
set "NEED_VENV=0"
if not exist ".venv\Scripts\python.exe" set "NEED_VENV=1"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" --version >nul 2>&1
  if errorlevel 1 set "NEED_VENV=1"
)
if "%NEED_VENV%"=="1" (
  echo [1/5] Rebuilding virtual environment ...
  if exist ".venv" rmdir /s /q ".venv"
  %PY% -m venv .venv
  if errorlevel 1 goto fail
) else (
  echo [1/5] Virtual environment is OK.
)

echo [2/5] Installing Python packages (first time needs internet) ...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail

echo [3/5] Preparing database ...
".venv\Scripts\python.exe" manage.py migrate
if errorlevel 1 goto fail

if not exist "db.sqlite3" (
  echo Importing built-in CET-4 word bank ...
  ".venv\Scripts\python.exe" manage.py seed_words
)

echo [4/5] Starting server on %URL% ...
echo [5/5] Opening browser ...
echo Close this window to stop the server.
echo.
if not "%CT4_NO_BROWSER%"=="1" (
  start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process '%URL%'"
)
".venv\Scripts\python.exe" manage.py runserver 127.0.0.1:%PORT%
echo.
echo Server stopped.
pause
exit /b 0

:already
echo Port %PORT% is already in use. The server is probably running.
if not "%CT4_NO_BROWSER%"=="1" start "" "%URL%"
pause
exit /b 0

:fail
echo.
echo [ERROR] Setup failed. Please check the messages above.
pause
exit /b 1