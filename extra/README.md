# Extra tools

This folder contains helper scripts/docs used to keep the Home Assistant config maintainable.

## Standards

- Automation / package documentation standard: `../automations.md`
- Full template reference: `AUTOMATION_TEMPLATE.md`

## Audits

### `ha_audit.py`
Lightweight repo scan for:
- Duplicate automation `id:` values
- Duplicate helper keys (`script:`, `input_boolean:`, `input_select:`, etc.)
- Missing references to `script.*`, `input_boolean.*`, `input_select.*`

Run:
- `py extra/ha_audit.py`
- `py extra/ha_audit.py --style`

### Registry inventory export + usage audit
These two scripts are used together to understand what entity IDs/devices exist in Home Assistant vs what is referenced in this repo.

1) Export registries (sanitized):
- `py -3 extra/ha_export_registry.py --storage-dir <path-to-.storage>`

2) Audit inventory vs repo usage:
- `py -3 extra/ha_inventory_audit.py --inventory-json <path-to-ha_inventory.sanitized.json>`

Notes:
- “Unused in repo” is heuristic; always verify in the HA UI before deleting entities.

### `audit_ui_automation.py`
Compares `ui-automation.yaml` references (`automation.*`) vs YAML-defined automations (by `alias:` → slug).

Run:
- `py -3 extra/audit_ui_automation.py`

## Docs sync

### `ha_docs_sync.py`
Keeps GitHub-facing documentation in sync with the repo structure.

Currently it maintains the auto-generated package index inside `SYSTEM_OVERVIEW.md`.

Run:
- `py extra/ha_docs_sync.py` (updates the file)
- `py extra/ha_docs_sync.py --check` (fails if the file is out of date; good for CI)

## Git hooks (optional)

If you commit + push directly (no PRs), you can enable the tracked hooks in `githooks/`:

- Enable once: `git config core.hooksPath githooks`
- Disable: `git config --unset core.hooksPath`

## VS Code tasks

This repo includes VS Code tasks under `.vscode/tasks.json`.

How to run:

1) In VS Code open the Command Palette
2) Run: `Tasks: Run Task`
3) Pick one:
	- `HA: Docs + Audit` (recommended)
	- `HA: Docs Sync`
	- `HA: Audit`
	- `HA: Audit (Style)`

## Files

- `AUTOMATION_TEMPLATE.md` – canonical header/template
- `ha_export_registry.py` – exports sanitized HA registry inventory
- `ha_inventory_audit.py` – usage audit against the exported inventory
- `audit_ui_automation.py` – UI automation dashboard reference audit
- `add_id_2_automations.py` – one-off helper (legacy)
