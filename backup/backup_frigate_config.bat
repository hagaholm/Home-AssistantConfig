@echo off
REM Backup script for Frigate config

REM Source file
set SOURCE=I:\ccab4aaf_frigate\config.yaml

REM Destination directory
set DEST_DIR=C:\Users\micke\Documents\backup\home_assistant\frigate

REM Create destination directory if it doesn't exist
if not exist "%DEST_DIR%" mkdir "%DEST_DIR%"

REM Generate timestamp (format: YYYY-MM-DD_HH-MM-SS)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%-%datetime:~12,2%

REM Destination filename with timestamp
set DEST_FILE=%DEST_DIR%\config_%TIMESTAMP%.yaml

REM Check if source file exists
if not exist "%SOURCE%" (
    echo Error: Source file not found: %SOURCE%
    pause
    exit /b 1
)

REM Find the most recent backup file
set LATEST_BACKUP=
for /f "delims=" %%F in ('dir /b /o-d "%DEST_DIR%\config_*.yaml" 2^>nul') do (
    set LATEST_BACKUP=%DEST_DIR%\%%F
    goto :found
)
:found

REM --- Create masked safe copy only when it differs from the latest safe copy ---
set REPO_BACKUP_DIR=C:\Users\micke\Documents\GitHub\Home-AssistantConfig\backup\frigate
set REPO_BACKUP_FILE=%REPO_BACKUP_DIR%\config_safe_%TIMESTAMP%.yaml
if not exist "%REPO_BACKUP_DIR%" mkdir "%REPO_BACKUP_DIR%"

set ACTION=
set SAFE_FILE=
set TMP_OUT=%REPO_BACKUP_DIR%\_tmp_safe_out.txt
if exist "%TMP_OUT%" del "%TMP_OUT%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$src='%SOURCE%'; $dir='%REPO_BACKUP_DIR%'; $ts='%TIMESTAMP%'; $target = Join-Path $dir ('config_safe_' + $ts + '.yaml'); $latest = Get-ChildItem -Path $dir -Filter 'config_safe_*.yaml' -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1; $tmp = [IO.Path]::GetTempFileName(); $content = Get-Content $src -Raw; $content = $content -replace 'rtsp://[^/]*@[^/]*/','rtsp://***MASKED***/'; $content = $content -replace '(\s+user:\s+).*','$1***MASKED***'; $content = $content -replace '(\s+password:\s+).*','$1***MASKED***'; $content | Set-Content $tmp -NoNewline; $create = $true; if ($latest) { if ((Get-FileHash -LiteralPath $tmp -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath $latest.FullName -Algorithm SHA256).Hash) { $create = $false; $target = $latest.FullName } }; if ($create) { Move-Item -Force $tmp $target; 'ACTION=CREATE' } else { Remove-Item -Force $tmp; 'ACTION=SKIP' }; 'SAFE=' + $target" > "%TMP_OUT%"

for /f "usebackq tokens=1* delims==" %%A in ("%TMP_OUT%") do (
        if /I "%%A"=="ACTION" set ACTION=%%B
        if /I "%%A"=="SAFE" set SAFE_FILE=%%B
)
if exist "%TMP_OUT%" del "%TMP_OUT%"

if /I "%ACTION%"=="CREATE" (
        echo Safe copy created: %SAFE_FILE%
        echo Generating camera comparison report...
        powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0generate_camera_comparison.ps1" -ConfigFile "%SAFE_FILE%" -Timestamp "%TIMESTAMP%"
        if %errorlevel% equ 0 (
                echo Camera comparison report created successfully
        ) else (
                echo Warning: Failed to create camera comparison report
        )
) else (
        echo Safe copy unchanged; skipping new safe copy and comparison.
)

REM --- Now check if timestamped backup is needed ---
REM Compare with latest backup if it exists
set CREATE_BACKUP=0
if defined LATEST_BACKUP (
    echo Checking if file has changed since last backup (hash compare)...
    set HASH_COMPARE=
    for /f "usebackq" %%H in (`powershell -NoProfile -Command "^$src='""%SOURCE%""'; ^$dst='""%LATEST_BACKUP%""'; try { if ((Get-FileHash -LiteralPath ^$src -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath ^$dst -Algorithm SHA256).Hash) { 'SAME' } else { 'DIFF' } } catch { 'ERROR' }"`) do set HASH_COMPARE=%%H

    echo Hash compare result: %HASH_COMPARE%

    if /I "%HASH_COMPARE%"=="SAME" (
        echo No changes detected since last timestamped backup.
        echo Latest backup: %LATEST_BACKUP%
    ) else if /I "%HASH_COMPARE%"=="DIFF" (
        echo Changes detected. Creating new timestamped backup...
        set CREATE_BACKUP=1
    ) else (
        echo Warning: Hash compare failed or returned nothing; skipping new timestamped backup to avoid duplicates.
    )
) else (
    echo No previous backup found. Creating first timestamped backup...
    set CREATE_BACKUP=1
)

if %CREATE_BACKUP% equ 1 (
    REM Copy the file
    copy "%SOURCE%" "%DEST_FILE%"
    if %errorlevel% equ 0 (
        echo Timestamped backup successful!
        echo File copied to: %DEST_FILE%
    ) else (
        echo ERROR: Failed to create timestamped backup
    )
)

REM Keep terminal open to see the result
pause
