param(
    [Parameter(Mandatory=$true)]
    [string]$ConfigFile,
    
    [Parameter(Mandatory=$true)]
    [string]$Timestamp
)

# Output file
$outputFile = Join-Path (Split-Path $ConfigFile -Parent) "..\CAMERA_COMPARISON_$Timestamp.md"

Write-Host "Reading config from: $ConfigFile"
Write-Host "Output file: $outputFile"

# Find the previous backup file (excluding the current one)
$configDir = Split-Path $ConfigFile -Parent
$previousBackup = $null
$latestBackups = @(Get-ChildItem -Path "$configDir" -Filter "config_safe_*.yaml" | Sort-Object -Property Name -Descending | Select-Object -First 2)

if ($latestBackups.Count -gt 1) {
    $previousBackup = $latestBackups[1].FullName
    Write-Host "Previous backup found: $previousBackup"
}

function ParseCameraConfig {
    param([string]$content)
    
    $cameras = @{}
    $cameraNames = @('cam5', 'cam6', 'cam8', 'cam9', 'cam10')
    $contentLines = $content -split "`r?`n"
    
    foreach ($camName in $cameraNames) {
        $cameras[$camName] = @{}
        
        # Find the camera section by looking for "  cam#:" pattern
        $startIdx = -1
        for ($i = 0; $i -lt $contentLines.Count; $i++) {
            if ($contentLines[$i] -match "^  $camName\s*:") {
                $startIdx = $i
                break
            }
        }
        
        if ($startIdx -ge 0) {
            # Extract lines from this camera until the next camera or end
            $endIdx = $contentLines.Count - 1
            for ($i = $startIdx + 1; $i -lt $contentLines.Count; $i++) {
                if ($contentLines[$i] -match "^  cam[0-9]+\s*:" -or ($contentLines[$i] -match "^  \S" -and $contentLines[$i] -notmatch "^    ")) {
                    $endIdx = $i - 1
                    break
                }
            }
            
            $camSection = $contentLines[$startIdx..$endIdx] -join "`n"
            
            # Extract values
            $cameras[$camName]['enabled'] = if ($camSection -match "enabled:\s*(true|false)") { $matches[1] } else { 'N/A' }
            $cameras[$camName]['fps'] = if ($camSection -match "fps:\s*(\d+)") { $matches[1] } else { 'N/A' }
            $cameras[$camName]['width'] = if ($camSection -match "width:\s*(\d+)") { $matches[1] } else { 'N/A' }
            $cameras[$camName]['height'] = if ($camSection -match "height:\s*(\d+)") { $matches[1] } else { 'N/A' }
            $cameras[$camName]['min_area'] = if ($camSection -match "min_area:\s*(\d+)") { $matches[1] } else { 'N/A' }
            $cameras[$camName]['min_score'] = if ($camSection -match "min_score:\s*([\d.]+)") { $matches[1] } else { 'N/A' }
            $cameras[$camName]['threshold'] = if ($camSection -match "threshold:\s*([\d.]+)") { $matches[1] } else { 'N/A' }
            $cameras[$camName]['motion_threshold'] = if ($camSection -match "motion:[\s\S]*?threshold:\s*(\d+)") { $matches[1] } else { 'N/A' }
            $cameras[$camName]['contour_area'] = if ($camSection -match "contour_area:\s*(\d+)") { $matches[1] } else { 'N/A' }
            $cameras[$camName]['person_max_ratio'] = if ($camSection -match "person:[\s\S]*?max_ratio:\s*([\d.]+)") { $matches[1] } else { 'N/A' }
            $cameras[$camName]['clean_copy'] = if ($camSection -match "clean_copy:\s*(true|false)") { $matches[1] } else { 'false' }
            $cameras[$camName]['person_mask'] = if ($camSection -match "person:[\s\S]*?mask:") { 'true' } else { 'false' }
            $cameras[$camName]['zone_name'] = if ($camSection -match "zones:\s*\r?\n\s+(\w+):") { $matches[1] } else { 'N/A' }
        } else {
            # Camera not found, set all to N/A
            foreach ($key in @('enabled', 'fps', 'width', 'height', 'min_area', 'min_score', 'threshold', 'motion_threshold', 'contour_area', 'person_max_ratio', 'clean_copy', 'person_mask', 'zone_name')) {
                $cameras[$camName][$key] = 'N/A'
            }
        }
    }
    
    return $cameras
}

try {
    # Read the current YAML config file
    $content = Get-Content $ConfigFile -Raw -Encoding UTF8
    $contentLines = $content -split "`r?`n"
    $cameras = ParseCameraConfig -content $content
    
    # Read previous backup if available
    $previousCameras = $null
    $previousLines = $null
    if ($previousBackup) {
        $previousContent = Get-Content $previousBackup -Raw -Encoding UTF8
        $previousLines = $previousContent -split "`r?`n"
        $previousCameras = ParseCameraConfig -content $previousContent
    }
    
    # Detect changes
    $changesSectionMarkdown = ""
    if ($previousCameras) {
        $changesSectionMarkdown = "## Changes from Previous Backup`n`n"
        $hasChanges = $false
        
        # Compare each camera's settings
        foreach ($camName in @('cam5', 'cam6', 'cam8', 'cam9', 'cam10')) {
            $camChanges = @()
            
            foreach ($key in $cameras[$camName].Keys) {
                $currentVal = $cameras[$camName][$key]
                $previousVal = $previousCameras[$camName][$key]
                
                if ($currentVal -ne $previousVal) {
                    $hasChanges = $true
                    $camChanges += @{
                        Setting = $key
                        OldValue = $previousVal
                        NewValue = $currentVal
                    }
                }
            }
            
            if ($camChanges.Count -gt 0) {
                $changesSectionMarkdown += "`n### **$camName Changes**`n`n"
                foreach ($change in $camChanges) {
                    $changesSectionMarkdown += "- **$($change.Setting)**: ``$($change.OldValue)`` → ``$($change.NewValue)``"
                    
                    # Find line numbers with changes
                    $lineChanges = @()
                    for ($i = 0; $i -lt $contentLines.Count; $i++) {
                        if ($contentLines[$i] -match $change.Setting -and $contentLines[$i] -match $change.NewValue) {
                            $lineChanges += ($i + 1)
                        }
                    }
                    
                    if ($lineChanges.Count -gt 0) {
                        $changesSectionMarkdown += " (Line(s): $($lineChanges -join ', '))`n"
                    } else {
                        $changesSectionMarkdown += "`n"
                    }
                }
            }
        }
        
        if (-not $hasChanges) {
            $changesSectionMarkdown = "## Changes from Previous Backup`n`nNo changes detected. Configuration is identical to previous backup.`n`n"
        } else {
            $changesSectionMarkdown += "`n"
        }
    }
    
    # Generate markdown
    $markdown = @"
# Camera Comparison Analysis

**Generated from**: ``config_safe_$Timestamp.yaml``  
**Date**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

$changesSectionMarkdown

## Complete Camera Configuration Comparison Table

This table shows all Frigate configuration values for each camera, making it easy to see differences:

| Configuration Parameter | Cam5 | Cam6 | Cam8 | Cam9 | Cam10 |
|---|---|---|---|---|---|
| **ENABLED** |
| Camera Enabled | $($cameras['cam5']['enabled']) | $($cameras['cam6']['enabled']) | $($cameras['cam8']['enabled']) | $($cameras['cam9']['enabled']) | $($cameras['cam10']['enabled']) |
| **DETECTION** |
| Detection FPS | $($cameras['cam5']['fps']) | $($cameras['cam6']['fps']) | $($cameras['cam8']['fps']) | $($cameras['cam9']['fps']) | $($cameras['cam10']['fps']) |
| Detection Width | $($cameras['cam5']['width']) | $($cameras['cam6']['width']) | $($cameras['cam8']['width']) | $($cameras['cam9']['width']) | $($cameras['cam10']['width']) |
| Detection Height | $($cameras['cam5']['height']) | $($cameras['cam6']['height']) | $($cameras['cam8']['height']) | $($cameras['cam9']['height']) | $($cameras['cam10']['height']) |
| **DETECTION FILTERS - ALL OBJECTS** |
| Min Area (pixels) | **$($cameras['cam5']['min_area'])** | **$($cameras['cam6']['min_area'])** ⬆️ | **$($cameras['cam8']['min_area'])** ⬇️ | **$($cameras['cam9']['min_area'])** | **$($cameras['cam10']['min_area'])** |
| Min Score | **$($cameras['cam5']['min_score'])** | **$($cameras['cam6']['min_score'])** | **$($cameras['cam8']['min_score'])** | **$($cameras['cam9']['min_score'])** | **$($cameras['cam10']['min_score'])** |
| Threshold | **$($cameras['cam5']['threshold'])** | **$($cameras['cam6']['threshold'])** | **$($cameras['cam8']['threshold'])** | **$($cameras['cam9']['threshold'])** | **$($cameras['cam10']['threshold'])** |
| **DETECTION FILTERS - PERSON** |
| Person Max Ratio | $($cameras['cam5']['person_max_ratio']) | $($cameras['cam6']['person_max_ratio']) | $($cameras['cam8']['person_max_ratio']) | $($cameras['cam9']['person_max_ratio']) | $($cameras['cam10']['person_max_ratio']) |
| Person Mask | $(if ($cameras['cam5']['person_mask'] -eq 'true') {'✅ Yes'} else {'❌ No'}) | $(if ($cameras['cam6']['person_mask'] -eq 'true') {'✅ Yes'} else {'❌ No'}) | $(if ($cameras['cam8']['person_mask'] -eq 'true') {'✅ Yes'} else {'❌ No'}) | $(if ($cameras['cam9']['person_mask'] -eq 'true') {'✅ Yes'} else {'❌ No'}) | $(if ($cameras['cam10']['person_mask'] -eq 'true') {'✅ Yes'} else {'❌ No'}) |
| **MOTION DETECTION** |
| Motion Threshold | **$($cameras['cam5']['motion_threshold'])** | **$($cameras['cam6']['motion_threshold'])** | **$($cameras['cam8']['motion_threshold'])** | **$($cameras['cam9']['motion_threshold'])** | **$($cameras['cam10']['motion_threshold'])** |
| Motion Contour Area | **$($cameras['cam5']['contour_area'])** | **$($cameras['cam6']['contour_area'])** | **$($cameras['cam8']['contour_area'])** | **$($cameras['cam9']['contour_area'])** | **$($cameras['cam10']['contour_area'])** |
| **SNAPSHOTS** |
| Clean Copy | $(if ($cameras['cam5']['clean_copy'] -eq 'true') {'✅ Yes'} else {'❌ No'}) | $(if ($cameras['cam6']['clean_copy'] -eq 'true') {'✅ Yes'} else {'❌ No'}) | $(if ($cameras['cam8']['clean_copy'] -eq 'true') {'✅ Yes'} else {'❌ No'}) | $(if ($cameras['cam9']['clean_copy'] -eq 'true') {'✅ Yes'} else {'❌ No'}) | $(if ($cameras['cam10']['clean_copy'] -eq 'true') {'✅ Yes'} else {'❌ No'}) |
| **ZONES** |
| Zone Name | $($cameras['cam5']['zone_name']) | $($cameras['cam6']['zone_name']) | $($cameras['cam8']['zone_name']) | $($cameras['cam9']['zone_name']) | $($cameras['cam10']['zone_name']) |

---

## Key Differences Highlighted

### 🔴 Most Sensitive Settings (Lowest Thresholds)

| Setting | Camera | Value | Why? |
|---------|--------|-------|------|
| Min Area (smallest) | **Cam6** | $($cameras['cam6']['min_area']) | Rear entrance - needs to catch close-up detections |
| Min Score (lowest) | **Cam6, Cam8, Cam9** | $($cameras['cam6']['min_score']) | More permissive detection |

### 🟢 Least Sensitive Settings (Highest Thresholds)

| Setting | Camera | Value | Why? |
|---------|--------|-------|------|
| Min Area (largest) | **Cam5** | $($cameras['cam5']['min_area']) | Rear yard - avoids distant noise |
| Min Score (highest) | **Cam10** | $($cameras['cam10']['min_score']) | More strict detection |

### 📊 Sensitivity Summary Table

| Camera | Min Area | Min Score | Motion Threshold | Contour Area |
|--------|----------|-----------|------------------|--------------|
| **Cam5** (Rear Yard) | $($cameras['cam5']['min_area']) | $($cameras['cam5']['min_score']) | $($cameras['cam5']['motion_threshold']) | $($cameras['cam5']['contour_area']) |
| **Cam6** (Rear Entrance) | $($cameras['cam6']['min_area']) | $($cameras['cam6']['min_score']) | $($cameras['cam6']['motion_threshold']) | $($cameras['cam6']['contour_area']) |
| **Cam8** (Main Entrance) | $($cameras['cam8']['min_area']) | $($cameras['cam8']['min_score']) | $($cameras['cam8']['motion_threshold']) | $($cameras['cam8']['contour_area']) |
| **Cam9** (Garden Shed) | $($cameras['cam9']['min_area']) | $($cameras['cam9']['min_score']) | $($cameras['cam9']['motion_threshold']) | $($cameras['cam9']['contour_area']) |
| **Cam10** (Driveway) | $($cameras['cam10']['min_area']) | $($cameras['cam10']['min_score']) | $($cameras['cam10']['motion_threshold']) | $($cameras['cam10']['contour_area']) |

---

## Configuration Patterns

### Pattern: Where Cameras Differ
❌ **Min Area**: $($cameras['cam5']['min_area']) vs $($cameras['cam6']['min_area']) vs $($cameras['cam8']['min_area']) vs $($cameras['cam9']['min_area']) vs $($cameras['cam10']['min_area'])  
❌ **Min Score**: $($cameras['cam5']['min_score']) vs $($cameras['cam6']['min_score']) vs $($cameras['cam8']['min_score']) vs $($cameras['cam9']['min_score']) vs $($cameras['cam10']['min_score'])  
❌ **Motion Threshold**: $($cameras['cam5']['motion_threshold']) vs $($cameras['cam6']['motion_threshold']) vs $($cameras['cam8']['motion_threshold']) vs $($cameras['cam9']['motion_threshold']) vs $($cameras['cam10']['motion_threshold'])  
❌ **Motion Contour Area**: $($cameras['cam5']['contour_area']) vs $($cameras['cam6']['contour_area']) vs $($cameras['cam8']['contour_area']) vs $($cameras['cam9']['contour_area']) vs $($cameras['cam10']['contour_area'])  
❌ **Clean Copy**: Cam5, Cam6, Cam8, Cam9, Cam10 = $($cameras['cam5']['clean_copy']) / $($cameras['cam6']['clean_copy']) / $($cameras['cam8']['clean_copy']) / $($cameras['cam9']['clean_copy']) / $($cameras['cam10']['clean_copy'])  
❌ **Person Mask**: Cam5, Cam6, Cam8, Cam9, Cam10 = $($cameras['cam5']['person_mask']) / $($cameras['cam6']['person_mask']) / $($cameras['cam8']['person_mask']) / $($cameras['cam9']['person_mask']) / $($cameras['cam10']['person_mask'])

---

**Source File**: ``config_safe_$Timestamp.yaml``  
**Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@

    # Write to file
    $markdown | Out-File -FilePath $outputFile -Encoding UTF8
    Write-Host "Camera comparison report created: $outputFile"
    exit 0
    
} catch {
    Write-Error "Failed to generate camera comparison: $_"
    exit 1
}
