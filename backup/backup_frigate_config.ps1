$ErrorActionPreference = 'Stop'

$source = 'I:\ccab4aaf_frigate\config.yaml'
$rawBackupDir = 'C:\Users\micke\Documents\backup\home_assistant\frigate'
$safeBackupDir = Join-Path $PSScriptRoot 'frigate'
$reportScript = Join-Path $PSScriptRoot 'generate_camera_comparison.ps1'

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
    throw "Frigate config not found: $source"
}
if (-not (Test-Path -LiteralPath $reportScript -PathType Leaf)) {
    throw "Camera comparison script not found: $reportScript"
}

New-Item -ItemType Directory -Path $rawBackupDir -Force | Out-Null
New-Item -ItemType Directory -Path $safeBackupDir -Force | Out-Null

$timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$rawFile = Join-Path $rawBackupDir "config_$timestamp.yaml"
$safeFile = Join-Path $safeBackupDir "config_safe_$timestamp.yaml"
$reportFile = Join-Path $PSScriptRoot "CAMERA_COMPARISON_$timestamp.md"

while ((Test-Path -LiteralPath $rawFile) -or
    (Test-Path -LiteralPath $safeFile) -or
    (Test-Path -LiteralPath $reportFile)) {
    Start-Sleep -Seconds 1
    $timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
    $rawFile = Join-Path $rawBackupDir "config_$timestamp.yaml"
    $safeFile = Join-Path $safeBackupDir "config_safe_$timestamp.yaml"
    $reportFile = Join-Path $PSScriptRoot "CAMERA_COMPARISON_$timestamp.md"
}

$latestRaw = Get-ChildItem -LiteralPath $rawBackupDir -Filter 'config_*.yaml' -File |
    Sort-Object Name -Descending |
    Select-Object -First 1

$createRawBackup = $true
if ($latestRaw) {
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    $latestRawHash = (Get-FileHash -LiteralPath $latestRaw.FullName -Algorithm SHA256).Hash
    $createRawBackup = $sourceHash -ne $latestRawHash
}

if ($createRawBackup) {
    Copy-Item -LiteralPath $source -Destination $rawFile
    Write-Host "Timestamped backup created: $rawFile"
} else {
    Write-Host "Raw config unchanged; no timestamped backup created."
}

$latestSafe = Get-ChildItem -LiteralPath $safeBackupDir -Filter 'config_safe_*.yaml' -File |
    Sort-Object Name -Descending |
    Select-Object -First 1

$temporarySafeFile = Join-Path $safeBackupDir ".tmp_safe_$timestamp.yaml"
try {
    $content = [IO.File]::ReadAllText($source)
    $content = [regex]::Replace($content, 'rtsp://[^/]*@[^/]*/', 'rtsp://***MASKED***/')
    $content = [regex]::Replace($content, '(\s+user:\s+).*', '$1***MASKED***')
    $content = [regex]::Replace($content, '(\s+password:\s+).*', '$1***MASKED***')
    [IO.File]::WriteAllText($temporarySafeFile, $content, [Text.UTF8Encoding]::new($false))

    $createSafeBackup = $true
    if ($latestSafe) {
        $currentSafeHash = (Get-FileHash -LiteralPath $temporarySafeFile -Algorithm SHA256).Hash
        $latestSafeHash = (Get-FileHash -LiteralPath $latestSafe.FullName -Algorithm SHA256).Hash
        $createSafeBackup = $currentSafeHash -ne $latestSafeHash
    }

    if ($createSafeBackup) {
        Move-Item -LiteralPath $temporarySafeFile -Destination $safeFile
        Write-Host "Masked safe copy created: $safeFile"
        & $reportScript -ConfigFile $safeFile -Timestamp $timestamp
        if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
            throw "Camera comparison report failed with exit code $LASTEXITCODE."
        }
        Write-Host "Camera comparison report created: $reportFile"
    } else {
        Write-Host "Masked config unchanged; no safe copy or comparison report created."
    }
} finally {
    if (Test-Path -LiteralPath $temporarySafeFile) {
        Remove-Item -LiteralPath $temporarySafeFile
    }
}
