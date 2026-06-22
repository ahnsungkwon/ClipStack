@echo off
setlocal

set "SCRIPT=E:\GoogleDrive\code\application_renamer\run_rename_original_images.py"

if not "%~1"=="" (
    set "TARGET=%~1"
) else (
    set "TARGET=%~dp0."
)

echo ==========================================================
echo   Original application image rename helper
echo ==========================================================
echo [INFO] script: %SCRIPT%
echo [INFO] target: %TARGET%
echo.

where py >nul 2>nul
if "%ERRORLEVEL%"=="0" (
    py -3 "%SCRIPT%" "%TARGET%"
) else (
    python "%SCRIPT%" "%TARGET%"
)
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo [BAT] ERROR. Exit code: %EXIT_CODE%
) else (
    echo.
    echo [BAT] Done.
)
pause
exit /b %EXIT_CODE%