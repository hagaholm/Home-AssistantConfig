# Home Assistant – Automations & Package Standard

This repo uses **packages** as the primary structure. Automations, scripts, helpers, and templates should live under `packages/` grouped by domain (e.g. `packages/lights/`, `packages/alerts/`, `packages/climate/`, `packages/ventilation/`).

The canonical, full template is: `extra/AUTOMATION_TEMPLATE.md`.

## 1) File structure (packages)

### Naming
- Prefer: `packages/<domain>/<topic>.yaml` (example: `packages/lights/inside.yaml`, `packages/climate/garage.yaml`).
- Keep one “topic” per file when possible.

### Order inside a package file
Use a consistent top-to-bottom order so files are easy to scan:
1. Header block (documentation)
2. Helpers (`input_boolean`, `input_select`, `input_number`, `timer`, etc.)
3. Entities (`sensor`, `binary_sensor`, `template`, etc.)
4. `automation:`
5. `script:`

## 2) Header/comment standard

### Recommended (full) header
Use the banner style + the metadata blocks from `extra/AUTOMATION_TEMPLATE.md`.

At minimum, include:
- `Källor:` (where it came from / what it replaces)
- `BESKRIVNING:` (what it does and why)

### Metadata
Add `METADATA:` (or at least `Skapad:`) when a file is actively maintained.

### Inline comments
- Prefer comments that explain **why** (constraints, safety, edge cases), not “what” the YAML already shows.

## 3) Automation standards (rules of thumb)

### Required fields
- Every automation should have:
  - `alias:` (Swedish UI-friendly name)
  - `id:` (preserve the existing ID when migrating/consolidating)
  - `mode:` explicitly set

### Choose blocks
- If you use `choose:`, set an `alias:` for each branch.

### Safer triggers (startup robustness)
If an entity may be missing/unavailable at startup (common for some integrations), prefer `template` triggers/conditions:
- Use guards like: `states('sensor.x') not in ['unknown','unavailable','']` before converting to `|float`.

## 4) Template sensor standards

### Numeric sensors
If you set `device_class: temperature` or rely on numeric state:
- Ensure the template always returns a number (e.g. `|float(0)`) **and** set `availability:` so it becomes unavailable cleanly.

### Timestamp sensors
If `device_class: timestamp`:
- Do **not** return the string `unavailable`.
- Prefer:
  - `availability:` guarding the source
  - `state:` returning a real datetime object or a proper ISO timestamp

## 5) Quick checks

### Local audit script
Run:
- `py extra/ha_audit.py` (duplicates + missing script/helper references)
- `py extra/ha_audit.py --style` (best-effort header/comment consistency check for `packages/*.yaml`)

## 6) Notes
- Some integration-focused package files may intentionally be “light” on metadata. For automation-heavy files, prefer the full header standard.
