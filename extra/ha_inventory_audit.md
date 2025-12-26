# HA inventory audit (used vs unused)

This script scans this repo for entity-id references (e.g. `light.kok`, `automation.xxx`) and compares them to the exported HA registry inventory.

Goal: help you identify **cleanup candidates** (entities/devices that appear not referenced anywhere in your config files), and make future dashboard/entity-id refactors much easier.

## Inputs

- `exports/ha_inventory/ha_inventory.sanitized.json`
  - Produced by [extra/ha_export_registry.py](extra/ha_export_registry.py)

## Outputs

Written to `exports/ha_inventory/`:

- `ha_inventory.usage_report.json`
  - Full report with summary + example references per entity
- `entities_usage.csv`
  - Compact report for sorting in Excel / grep
- `devices_usage.csv`
  - Devices marked as cleanup candidates if none of their entities are referenced

## How to run

From repo root:

- `py -3 extra/ha_inventory_audit.py`

If your inventory file is somewhere else:

- `py -3 extra/ha_inventory_audit.py --inventory-json <path>`

## Notes / limitations

- **Unused-in-repo is a heuristic.** It only means this repo scan didn’t find references.
  - Entities can still be used by:
    - UI-created dashboards / helpers
    - Integrations
    - Scripts/automations created in the HA UI
- For safe cleanup, always confirm in HA:
  - Settings → Devices & services → Entities
  - check where it’s used, and check logs

## Suggested workflow

1) Export registries (sanitized)
2) Run audit
3) Review `entities_usage.csv` (filter `used_in_repo=false`)
4) Delete true orphans in HA UI (removes from registry)
5) Re-export and re-audit to confirm
