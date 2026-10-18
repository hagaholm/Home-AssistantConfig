# Frigate configuration backups

## Before you run the backup

The scripts are for Windows and expect the Frigate source config at:

`I:\ccab4aaf_frigate\config.yaml`

Make sure the `I:` drive is connected and the source file is accessible.

## Run the complete backup

Open PowerShell or Command Prompt and run the batch file:

```powershell
& "\\192.168.1.9\config\backup\backup_frigate_config.bat"
```

Alternatively, open `backup_frigate_config.bat` from File Explorer.

The batch file launches `backup_frigate_config.ps1`. The PowerShell script:

1. Creates a timestamped raw copy under
   `C:\Users\micke\Documents\backup\home_assistant\frigate\`.
   Raw copies contain credentials. Keep them private.
2. Masks RTSP credentials and `user`/`password` values and saves a safe copy
   under `backup\frigate\`.
3. Skips copies whose content is unchanged from the latest corresponding
   backup.
4. If a new safe copy is created, automatically runs
   `generate_camera_comparison.ps1` and writes a report under `backup\`.

The safe copy and report share a timestamp:

- `backup\frigate\config_safe_YYYY-MM-DD_HH-mm-ss.yaml`
- `backup\CAMERA_COMPARISON_YYYY-MM-DD_HH-mm-ss.md`

If the safe config has not changed, the script skips both the new safe copy
and report. The raw copy is checked independently against its latest backup.

## Run the comparison script manually

Usually this is not necessary because the backup script runs it automatically
when it creates a new safe copy. To regenerate a report or compare an existing
safe config, pass that config's full path and the matching timestamp:

```powershell
$config = "\\192.168.1.9\config\backup\frigate\config_safe_2026-10-18_19-22-58.yaml"
$timestamp = "2026-10-18_19-22-58"
& powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "\\192.168.1.9\config\backup\generate_camera_comparison.ps1" `
  -ConfigFile $config `
  -Timestamp $timestamp
```

Replace the example timestamp with the timestamp in the safe config filename.
The report is saved one folder above the config, in `backup\`.

The comparison script uses the newest other `config_safe_*.yaml` in
`backup\frigate\` as the previous config. For meaningful change results, run
it with the newest safe copy after the backup step.

## Outputs and credential safety

- `backup\frigate\config_safe_*.yaml`: masked copies suitable for review and
  version control. Check masking before sharing or committing.
- `backup\CAMERA_COMPARISON_*.md`: camera settings comparison reports.
- `C:\Users\micke\Documents\backup\home_assistant\frigate\config_*.yaml`:
  unmasked raw copies. Do not commit or share these files.

Reports summarize selected camera settings; they are not a complete YAML
diff. Review the safe YAML files directly when you need to identify every
configuration change.
