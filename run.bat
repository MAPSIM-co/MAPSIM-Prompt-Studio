@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

rem Thin wrapper around run.ps1 so the app can be started by double-clicking.
rem Everything is passed through: run.bat -Port 8005   /   run.bat -Tests

where powershell.exe >nul 2>nul
if errorlevel 1 (
    echo PowerShell 5.1 or newer is required, and this Windows install does not have it.
    echo Install the Windows Management Framework or the .NET desktop runtime, then try again.
    pause
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
set "EXITCODE=%ERRORLEVEL%"

if not "%~1"=="" endlocal & exit /b %EXITCODE%

echo.
if "%EXITCODE%"=="0" (
    echo MAPSIM Prompt Studio stopped.
) else (
    echo MAPSIM Prompt Studio exited with code %EXITCODE% - see the message above.
)
pause >nul
endlocal & exit /b %EXITCODE%
