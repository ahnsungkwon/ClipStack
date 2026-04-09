@echo off
setlocal
set "AHK=C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
set "SCRIPT=%~dp0clipboard_triplets.ahk"

if not exist "%AHK%" (
    echo AutoHotkey v2 실행 파일을 찾을 수 없습니다.
    echo 경로: %AHK%
    pause
    exit /b 1
)

if not exist "%SCRIPT%" (
    echo 스크립트를 찾을 수 없습니다.
    echo 경로: %SCRIPT%
    pause
    exit /b 1
)

start "" "%AHK%" "%SCRIPT%"
