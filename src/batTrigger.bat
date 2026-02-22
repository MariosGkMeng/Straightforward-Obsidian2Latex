@echo off
setlocal

set "HERE=%~dp0"
set "SCRIPT=%HERE%triggerObsidianNoteOnClick.py"

echo HERE   = "%HERE%"
echo SCRIPT = "%SCRIPT%"

if not exist "%SCRIPT%" (
  echo.
  echo ERROR: Script not found at:
  echo   "%SCRIPT%"
  echo.
  pause
  exit /b 1
)

rem Use the Python launcher if available (often more reliable than "python")
py "%SCRIPT%" %*