@echo off
setlocal
set "AHK=C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
set "SCRIPT=%~dp0clipboard_triplets.ahk"

if not exist "%AHK%" (
    echo AutoHotkey v2 not found at: %AHK%
    echo Please install AutoHotkey v2 from https://www.autohotkey.com
    pause
    exit /b 1
)

if not exist "%SCRIPT%" (
    echo Script not found at: %SCRIPT%
    pause
    exit /b 1
)

start "" "%AHK%" "%SCRIPT%"
