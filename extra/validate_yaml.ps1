# Simple YAML validation script - checks for common issues in Home Assistant YAML files

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$FilePaths
)

if (-not $FilePaths) {
    $FilePaths = @(
        "packages/climate/friggebod.yaml",
        "ui-climate.yaml",
        "configuration.yaml"
    )
}

function Test-YamlFile {
    param([string]$Path)
    
    Write-Host "`n📄 Checking: $Path" -ForegroundColor Cyan
    
    if (-not (Test-Path $Path)) {
        Write-Host "  ❌ File not found: $Path" -ForegroundColor Red
        return $false
    }
    
    try {
        $content = Get-Content $Path -Raw -Encoding UTF8
        $lines = @(Get-Content $Path)
        
        $issues = @()
        
        # Check 1: Duplicate top-level keys
        $topLevelKeys = @()
        foreach ($line in $lines) {
            if ($line -match '^\w+:$') {
                $key = $line -replace ':\s*$', ''
                if ($key -in $topLevelKeys) {
                    $issues += "Duplicate top-level key: '$key' at line $($lines.IndexOf($line) + 1)"
                } else {
                    $topLevelKeys += $key
                }
            }
        }
        
        # Check 2: Tab characters (YAML doesn't allow tabs)
        $tabLines = @()
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match "`t") {
                $tabLines += ($i + 1)
            }
        }
        if ($tabLines) {
            $issues += "Tab characters found on lines: $($tabLines -join ', ')"
        }
        
        # Check 3: Basic indentation consistency (2-space rule)
        $indentIssues = @()
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            if ($line -match '^\s+') {
                $match = $line -match '^( +)'
                $spaces = $matches[1].Length
                if ($spaces % 2 -ne 0) {
                    $indentIssues += "Line $($i + 1): Odd indentation ($spaces spaces)"
                }
            }
        }
        if ($indentIssues.Count -lt 10) {
            $issues += $indentIssues
        } elseif ($indentIssues.Count -gt 0) {
            $issues += "$($indentIssues.Count) lines with odd indentation (showing first 10):"
            $issues += $indentIssues[0..9]
        }
        
        # Check 4: Unmatched quotes
        $quoteIssues = @()
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            $doubleQuotes = [regex]::Matches($line, '"').Count
            $singleQuotes = [regex]::Matches($line, "'").Count
            if ($doubleQuotes % 2 -ne 0) {
                $quoteIssues += "Line $($i + 1): Unmatched double quotes"
            }
            if ($singleQuotes % 2 -ne 0) {
                # Allow mismatched single quotes in Jinja templates
                if (-not ($line -contains '{%' -or $line -contains '{{')) {
                    $quoteIssues += "Line $($i + 1): Unmatched single quotes"
                }
            }
        }
        if ($quoteIssues.Count -lt 10) {
            $issues += $quoteIssues
        }
        
        if ($issues.Count -eq 0) {
            Write-Host "  ✅ PASS - No obvious YAML syntax issues" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ⚠️  Found $($issues.Count) potential issues:" -ForegroundColor Yellow
            foreach ($issue in $issues) {
                Write-Host "     - $issue" -ForegroundColor Yellow
            }
            return $false
        }
    }
    catch {
        Write-Host "  ❌ Error reading file: $_" -ForegroundColor Red
        return $false
    }
}

Write-Host "🔍 Home Assistant YAML Validation" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

$results = @()
foreach ($filePath in $FilePaths) {
    $results += (Test-YamlFile $filePath)
}

Write-Host "`n📊 Summary" -ForegroundColor Cyan
Write-Host "==========" -ForegroundColor Cyan
$passed = ($results | Where-Object { $_ -eq $true } | Measure-Object).Count
$failed = ($results | Where-Object { $_ -eq $false } | Measure-Object).Count
Write-Host "✅ Passed: $passed" -ForegroundColor Green
Write-Host "❌ Failed: $failed" -ForegroundColor Red

if ($failed -eq 0) {
    Write-Host "`n🎉 All files passed validation!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️  Some files have issues. Check above for details." -ForegroundColor Yellow
    exit 1
}
