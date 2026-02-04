param(
    [string]$Root = "c:\\Users\\micke\\Documents\\GitHub\\Home-AssistantConfig",
    [string]$OutCsv = "c:\\Users\\micke\\Documents\\GitHub\\Home-AssistantConfig\\docs\\labels_mapping.csv"
)

Write-Host "Scanning repo for entity IDs and proposing labels..." -ForegroundColor Cyan

# Ensure output directory exists
$outDir = Split-Path -Path $OutCsv -Parent
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

# Entity ID regex (common HA domains)
$entityPattern = '\b(?<domain>light|sensor|switch|binary_sensor|media_player|fan|input_boolean|input_select|automation|script|device_tracker|button|lock|cover|person)\.(?<name>[a-z0-9_\.]+)'

# Label rules (Swedish taxonomy)
$roomRules = @(
    @{ Pattern = 'andreas'; Label = 'Andreas rum' },
    @{ Pattern = 'louise'; Label = 'Louise rum' },
    @{ Pattern = 'vardagsrum'; Label = 'Vardagsrum' },
    @{ Pattern = 'sovrum'; Label = 'Sovrum' },
    @{ Pattern = 'hall'; Label = 'Hall' },
    @{ Pattern = 'kok|kök'; Label = 'Kök' },
    @{ Pattern = 'uterum'; Label = 'Uterum' },
    @{ Pattern = 'friggebod'; Label = 'Friggebod' },
    @{ Pattern = 'forrad|förråd'; Label = 'Förråd' },
    @{ Pattern = 'tvattstuga'; Label = 'Tvättstuga' },
    @{ Pattern = 'badrum'; Label = 'Badrum' },
    @{ Pattern = 'garage'; Label = 'Garage' },
    @{ Pattern = 'ute_|_ute|utomhus|fasad'; Label = 'Ute' }
)

$functionRules = @(
    @{ Pattern = 'jul|christmas|gran|stjärn'; Label = 'Jul' },
    @{ Pattern = 'fonster|fönster'; Label = 'Fönsterljus' },
    @{ Pattern = 'fasad'; Label = 'Fasad' },
    @{ Pattern = 'vitrin'; Label = 'Vitrinskåp' },
    @{ Pattern = 'tradgard|träd'; Label = 'Trädgård' },
    @{ Pattern = 'spabad'; Label = 'Spabad' },
    @{ Pattern = 'led'; Label = 'LED' }
)

$typeRules = @(
    @{ Pattern = 'temperature|temperatur'; Label = 'Temperatur' },
    @{ Pattern = 'humidity|luftfuktighet|rh'; Label = 'Luftfuktighet' },
    @{ Pattern = 'illuminance|ljusstyrka'; Label = 'Ljusstyrka' },
    @{ Pattern = 'battery|batteri'; Label = 'Batteri' },
    @{ Pattern = 'pressure|tryck'; Label = 'Tryck' }
)

$integrationRules = @(
    @{ Pattern = 'shelly'; Label = 'Shelly' },
    @{ Pattern = 'frigate'; Label = 'Frigate' },
    @{ Pattern = 'reolink'; Label = 'Reolink' },
    @{ Pattern = 'tellstick'; Label = 'Tellstick' },
    @{ Pattern = 'mqtt'; Label = 'MQTT' },
    @{ Pattern = 'volvo'; Label = 'Volvo' },
    @{ Pattern = 'zwift'; Label = 'Zwift' },
    @{ Pattern = 'tts|google_home|nest_hub|media_player'; Label = 'Media/TTS' },
    @{ Pattern = 'harmony'; Label = 'Harmony' }
)

$domainLabels = @{ 
    'light' = 'Belysning'; 'switch' = 'Strömbrytare'; 'sensor' = 'Sensor'; 'binary_sensor' = 'Sensor';
    'media_player' = 'Media'; 'fan' = 'Fläkt'; 'input_boolean' = 'Helper'; 'input_select' = 'Helper';
    'automation' = 'Automation'; 'script' = 'Script'; 'device_tracker' = 'Spårning'; 'button' = 'Knapp';
    'lock' = 'Lås'; 'cover' = 'Solskydd'; 'person' = 'Person'
}

# Collect files (YAML and UI configs, plus optional md/ps1/py for references)
$files = Get-ChildItem -Path $Root -Recurse -File | Where-Object {
    $_.Extension -in @('.yaml','.yml','.md','.txt','.ps1','.py')
}

# Deduplicate per entity_id
$found = @{}

foreach ($file in $files) {
    try {
        $content = Get-Content -Path $file.FullName -Encoding UTF8 -ErrorAction Stop
    } catch {
        continue
    }

    foreach ($line in $content) {
        $ms = [regex]::Matches($line, $entityPattern)
        foreach ($m in $ms) {
            $eid = $m.Value
            if (-not $found.ContainsKey($eid)) {
                $found[$eid] = @{
                    EntityId = $eid
                    SourceFiles = [System.Collections.Generic.HashSet[string]]::new()
                    Labels = [System.Collections.Generic.HashSet[string]]::new()
                    Domain = $m.Groups['domain'].Value
                }
            }
            $null = $found[$eid].SourceFiles.Add($file.FullName.Replace($Root + "\", ''))

            $idLower = $eid.ToLower()
            $pathLower = $file.FullName.ToLower()

            # Domain-based label
            if ($domainLabels.ContainsKey($found[$eid].Domain)) { $null = $found[$eid].Labels.Add($domainLabels[$found[$eid].Domain]) }

            foreach ($r in $roomRules) {
                if ($idLower -match $r.Pattern -or $pathLower -match $r.Pattern) {
                    # Prefer area-prefixed labels to keep taxonomy concise
                    $null = $found[$eid].Labels.Add("Area: " + $r.Label)
                }
            }
            foreach ($r in $functionRules) { if ($idLower -match $r.Pattern -or $pathLower -match $r.Pattern) { $null = $found[$eid].Labels.Add($r.Label) } }
            foreach ($r in $typeRules) { if ($idLower -match $r.Pattern -or $pathLower -match $r.Pattern) { $null = $found[$eid].Labels.Add($r.Label) } }
            foreach ($r in $integrationRules) { if ($idLower -match $r.Pattern -or $pathLower -match $r.Pattern) { $null = $found[$eid].Labels.Add($r.Label) } }
        }
    }
}

# Prepare CSV rows
$rows = @()
foreach ($k in $found.Keys | Sort-Object) {
    $info = $found[$k]
    $rows += [PSCustomObject]@{
        EntityId   = $info.EntityId
        Labels     = ([string]::Join('; ', ($info.Labels | Sort-Object)))
        Domain     = $info.Domain
        SourceFile = ([string]::Join(' | ', ($info.SourceFiles | Sort-Object)))
    }
}

# Write CSV
if ($rows.Count -gt 0) {
    $rows | Export-Csv -Path $OutCsv -NoTypeInformation -Encoding UTF8
    Write-Host "Wrote label suggestions to: $OutCsv" -ForegroundColor Green
    Write-Host ("Total entities: {0}" -f $rows.Count) -ForegroundColor Green
} else {
    Write-Host "No entity IDs detected. Check regex or file filters." -ForegroundColor Yellow
}

# Top labels summary
$labelSummary = @{}
foreach ($row in $rows) {
    foreach ($l in $row.Labels -split ';\s*') {
        if ([string]::IsNullOrWhiteSpace($l)) { continue }
        if (-not $labelSummary.ContainsKey($l)) { $labelSummary[$l] = 0 }
        $labelSummary[$l] += 1
    }
}
if ($rows.Count -gt 0) {
    Write-Host "\nLabel distribution (top 20):" -ForegroundColor Cyan
    foreach ($kv in ($labelSummary.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 20)) {
        Write-Host ("  - {0}: {1}" -f $kv.Key, $kv.Value)
    }
}
