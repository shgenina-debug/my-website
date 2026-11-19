@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title Maps Leads
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PY="

rem 1) Python inside the tool folder (installed by this script before)
if exist "%~dp0python\python.exe" set "PY=%~dp0python\python.exe"

rem 2) Python already installed on the computer (3.9 or newer)
if not defined PY (
  py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1 && set "PY=py -3"
)
if not defined PY (
  python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1 && set "PY=python"
)

rem 3) Not found: download and install Python into the tool folder (one time only)
if not defined PY (
  echo.
  echo  Python is not installed. Downloading it now, one time only - please wait...
  echo.
  set "PYURL=https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
  if /i "%PROCESSOR_ARCHITECTURE%"=="x86" set "PYURL=https://www.python.org/ftp/python/3.12.8/python-3.12.8.exe"
  call :download
  if not exist "%TEMP%\maps-leads-python.exe" (
    echo  Download failed. Check the internet connection and run again.
    pause
    exit /b 1
  )
  echo  Installing Python...
  "%TEMP%\maps-leads-python.exe" /quiet InstallAllUsers=0 PrependPath=0 Include_launcher=0 Include_test=0 Include_doc=0 Include_tcltk=0 Shortcuts=0 AssociateFiles=0 TargetDir="%~dp0python"
  del "%TEMP%\maps-leads-python.exe" >nul 2>&1
  if exist "%~dp0python\python.exe" set "PY=%~dp0python\python.exe"
)
if not defined PY (
  echo  Could not install Python automatically.
  echo  Install it from https://www.python.org/downloads/ then run this file again.
  pause
  exit /b 1
)

echo  Starting... the tool will open in the browser.
if "%PY%"=="py -3" (py -3 app.py) else if "%PY%"=="python" (python app.py) else ("%PY%" app.py)
if errorlevel 1 pause
exit /b 0

:download
where curl >nul 2>&1 && curl -L -s -o "%TEMP%\maps-leads-python.exe" "%PYURL%"
if exist "%TEMP%\maps-leads-python.exe" exit /b 0
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol='Tls12'; Invoke-WebRequest -UseBasicParsing -Uri '%PYURL%' -OutFile '%TEMP%\maps-leads-python.exe'"
exit /b 0
