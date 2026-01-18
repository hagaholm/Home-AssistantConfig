# Frigate Configuration Backup System

## Requirements

**This script must be run from:**
1. **A Windows computer** - The script is a batch file (.bat) and requires Windows
2. **Connected to your Home Assistant network** - Must have network access to the Home Assistant server
3. **Running on/from the Home Assistant server** - The source config file path (`I:\ccab4aaf_frigate\config.yaml`) must be accessible from your Windows computer (typically via network share or mapped drive from the Home Assistant server)

**Prerequisites:**
- Network access to Home Assistant server filesystem
- Windows batch and PowerShell execution enabled
- PowerShell 4.0 or higher (for `Get-FileHash` cmdlet)
- Read access to Frigate config file location

## Overview

The Frigate configuration backup system automatically creates versioned backups of your Frigate NVR config with masked credentials, and generates a detailed camera configuration comparison report.

## How It Works

### Step 1: Run the Backup Script

Execute the batch script from the backup folder:
```bash
cd C:\Users\micke\Documents\GitHub\Home-AssistantConfig\backup
backup_frigate_config.bat
```

### Step 2: Safe Copy Creation (Masked Credentials)

The script reads the source config file and:
1. **Masks RTSP credentials**: Replaces `rtsp://user:password@host/` with `rtsp://***MASKED***/`
2. **Masks user/password lines**: Replaces actual values with `***MASKED***`
3. **Creates temp file**: Writes masked content to a temporary file
4. **Hash comparison**: Compares temp file hash with the latest `config_safe_*.yaml`
   - **If identical**: Skips creating new safe copy and comparison (avoids duplicates)
   - **If different**: Saves as `config_safe_TIMESTAMP.yaml` in `backup/frigate/`

### Step 3: Camera Comparison Report

When a new safe copy is created, the script automatically:
1. **Parses YAML**: Extracts all 5 camera sections (cam3, cam5, cam6, cam7, cam8)
2. **Detects changes**: Compares current vs previous backup configuration
3. **Generates markdown**: Creates `CAMERA_COMPARISON_TIMESTAMP.md` with:
   - **Changes section**: Shows what changed from previous backup with line numbers
   - **Configuration table**: All camera settings side-by-side
   - **Sensitivity analysis**: Highlights min_area, min_score, thresholds
   - **Configuration patterns**: Shows what's shared vs unique per camera

### Step 4: Timestamped Backup (External)

If a previous timestamped backup exists:
- **Hash compare**: Checks if source file differs from latest backup
  - **Same**: Skips creating new timestamped backup
  - **Different**: Creates `config_TIMESTAMP.yaml` in `C:\Users\micke\Documents\backup\home_assistant\frigate\`

If no previous backup exists:
- **Creates first backup**: Establishes baseline for future comparisons

## File Structure

```
Home-AssistantConfig/
├── backup/
│   ├── backup_frigate_config.bat           # Main script
│   ├── generate_camera_comparison.ps1      # YAML parser & comparison engine
│   ├── frigate/
│   │   ├── config_safe_2026-01-18_13-01-54.yaml
│   │   ├── config_safe_2026-01-18_13-02-15.yaml
│   │   └── ...
│   └── CAMERA_COMPARISON_2026-01-18_13-01-54.md
│   └── CAMERA_COMPARISON_2026-01-18_13-02-15.md
└── BACKUP_SYSTEM.md                        # This file
```

## Safe Copies Location

**Git-safe location** (masked credentials, safe to commit):
- `backup/frigate/config_safe_*.yaml`

**External backups** (full credentials, NOT in git):
- `C:\Users\micke\Documents\backup\home_assistant\frigate\config_*.yaml`

## What Gets Masked

| Type | Original | Masked |
|------|----------|--------|
| RTSP URL | `rtsp://admin:password@192.168.1.22/h264Preview_01_main` | `rtsp://***MASKED***/h264Preview_01_main` |
| User field | `user: admin` | `user: ***MASKED***` |
| Password field | `password: secret123` | `password: ***MASKED***` |

## Camera Comparison Report Features

### Changes Section
When a config is updated, the report shows:
```markdown
### **cam3 Changes**

- **min_score**: `0.4` → `0.5` (Line(s): 192)
- **motion_threshold**: `30` → `25` (Line(s): 210)
```

### Configuration Table
All 5 cameras with all key settings:
- Enabled status
- Detection FPS, width, height
- Min area, min score, threshold
- Person mask, motion settings
- Snapshot retention
- Zone names

### Sensitivity Analysis
Identifies which cameras are most/least sensitive:
- **Most sensitive** (lowest thresholds): Typically rear entrance
- **Least sensitive** (highest thresholds): Typically rear yard
- Helps debug detection issues

## Key Settings Tracked

For each camera:
- `enabled` - Whether camera is active
- `fps` - Detection frame rate
- `width` / `height` - Detection resolution
- `min_area` - Minimum object size in pixels
- `min_score` - Confidence threshold (0.0-1.0)
- `threshold` - Classification threshold
- `motion_threshold` - Motion sensitivity (0-255, lower = more sensitive)
- `contour_area` - Motion contour minimum
- `clean_copy` - Whether snapshots exclude bounding boxes
- `person_mask` - Whether person detection is masked
- `zone_name` - Zone identifier

## Duplicate Prevention

The script prevents creating redundant files:
1. **Safe copy**: Only created if masked content differs from latest safe copy
2. **Comparison report**: Only created when safe copy is created
3. **Timestamped backup**: Only created if external config differs from latest backup

Run the script twice with no source changes → no new files created on second run.

## Usage Workflow

### Initial Setup
```bash
cd backup
backup_frigate_config.bat
# Creates first safe copy and comparison report
```

### Regular Backup
```bash
backup_frigate_config.bat
# Skips if no changes, creates new files if changes detected
```

### View Changes
Open the latest `CAMERA_COMPARISON_*.md` file in VS Code to see:
- What changed since last backup
- Line numbers of changes
- Current configuration comparison
- Sensitivity analysis

## Troubleshooting

**Issue**: Files created every run
- **Solution**: Ensure source file is unchanged; script should skip on 2nd run

**Issue**: Hash compare fails
- **Solution**: Falls back to safe; check PowerShell version (PS 4.0+)

**Issue**: Credentials leak
- **Solution**: All files in `backup/frigate/` are masked; never commit external backups

**Issue**: Comparison report missing
- **Solution**: Check `generate_camera_comparison.ps1` exists in backup folder; check PowerShell execution policy

## Timestamps Format

All files use format: `YYYY-MM-DD_HH-MM-SS`
- Example: `2026-01-18_13-01-54`
- Consistent across safe copies and comparisons
- Allows easy correlation between backup and report

## Next Steps

1. **Schedule backups**: Set Windows task scheduler to run daily
2. **Commit safe copies**: Add `backup/frigate/` to Git (credentials masked)
3. **Review changes**: Check new comparison reports for unexpected modifications
4. **Archive external backups**: Backup the external folder to external storage
