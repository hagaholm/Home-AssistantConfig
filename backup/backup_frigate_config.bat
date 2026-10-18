@echo off
setlocal

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0backup_frigate_config.ps1"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo Frigate backup failed with exit code %EXIT_CODE%.
)

exit /b %EXIT_CODE%
