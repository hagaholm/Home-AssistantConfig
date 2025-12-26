# HA registry export (sanitized)

This repo is YAML-heavy, so when you rename/move automations or sensors, Home Assistant can keep old entity IDs in the entity registry.
That often leads to `unavailable` entities and dashboard drift (e.g. `ui-automation.yaml` referencing old `automation.*`).

This script exports a **sanitized inventory** from HA’s registry files so you can:

- Diff *real* entity IDs over time
- Map entity IDs to `unique_id`
- See devices/areas/entities without sharing raw identifiers
- Keep a commit-able snapshot for future refactors

## What it reads

On the HA host, the registries are typically here:

- `/config/.storage/core.entity_registry`
- `/config/.storage/core.device_registry`
- `/config/.storage/core.area_registry`

## What it writes

Default output folder: `exports/ha_inventory/`

- `ha_inventory.sanitized.json` (safe-ish to commit)
- `entities.csv`, `devices.csv`, `areas.csv` (handy for git diffs)

## How to run

### Option A (recommended): run on a machine that has the HA config files

1) Copy the `.storage` directory from your HA host to your repo (or point directly at it).
2) Run:

- `py -3 extra/ha_export_registry.py --storage-dir <path-to-.storage>`

Example (if you copied it into the repo under `ha_storage/.storage`):

- `py -3 extra/ha_export_registry.py --storage-dir ha_storage/.storage`

### Option B: run on the HA host

If you have Python available on the HA host/container, run:

- `python3 /config/extra/ha_export_registry.py --storage-dir /config/.storage`

(Depending on your install, Python may not be present. In that case, use Option A.)

## Redaction / safety

The script **hashes** most values to avoid leaking:

- device identifiers
- connections (MAC/IP)
- other long strings

Entity IDs like `automation.*`, `sensor.*`, etc. are kept as-is since they are needed for dashboards.

You can also set a stable salt:

- env var: `HA_EXPORT_SALT`
- or flag: `--salt "my-salt"`

## Notes

- This does not export runtime states (those change constantly). It focuses on the registries (stable identity).
- After exporting, you can run the usage audit to see what’s referenced in this repo:
	- See: extra/ha_inventory_audit.md
- If you want a state snapshot too, tell me and I’ll add an optional `/api/states` exporter (requires a long-lived access token).
