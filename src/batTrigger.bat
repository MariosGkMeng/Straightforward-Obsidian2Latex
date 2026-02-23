@echo off
setlocal EnableExtensions

set "HERE=%~dp0"
set "SCRIPT=%HERE%triggerObsidianNoteOnClick.py"
set "LOG=%HERE%batTrigger.log"

(
  echo ==============================
  echo %date% %time%
  echo HERE   = "%HERE%"
  echo SCRIPT = "%SCRIPT%"
  where py
  where python
  echo.

  if not exist "%SCRIPT%" (
    echo ERROR: Script not found at "%SCRIPT%"
    exit /b 1
  )

  echo Running:
  echo py "%SCRIPT%" %*
  echo.

  py "%SCRIPT%" %*
  echo.
  echo ExitCode: %errorlevel%
) >> "%LOG%" 2>&1

exit /b
