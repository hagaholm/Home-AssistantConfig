# Home Assistant – Automations & Package Standard

This repo uses **packages** as the primary structure. Automations, scripts, helpers, and templates should live under `packages/` grouped by domain (e.g. `packages/lights/`, `packages/alerts/`, `packages/climate/`, `packages/ventilation/`).

The canonical, full template is: `extra/AUTOMATION_TEMPLATE.md`.

## 1) File structure (packages)

### Naming
- Prefer: `packages/<domain>/<topic>.yaml` (example: `packages/lights/inside.yaml`, `packages/climate/garage.yaml`).
- Keep one “topic” per file when possible.
- Don't add a domain prefix to the filename when the folder already names the domain (`packages/climate/garage.yaml`, not `packages/climate/climate_garage.yaml`). Keep a prefix (e.g. `frigate_`) only when several files in the same folder would otherwise be hard to tell apart in an editor tab list.

### Splitting a package into helpers / automation / scripts
Split a package file into three when it meets **at least one** of:
- the file is over ~200 lines, or
- the file contains 3 or more `script:` entries

into:
- `packages/<domain>/helpers/<topic>.yaml` — `input_select`/`input_boolean`/template sensors
- `packages/<domain>/<topic>.yaml` — entities + resolver automation(s)
- `packages/scripts/<domain>/<topic>.yaml` — scripts

Smaller packages keep the single-file layout below. Always preserve existing `id:`/`entity_id` values when splitting a file — never renumber or rename them.

### Naming new automations/scripts/entities
This applies only to **newly created** ids/aliases — never rename an existing `id:` or `entity_id`.
- New automation/script `id:` and `alias:` use consistent Swedish, pattern `<rum/domän>_<syfte>` (e.g. `kok_satt_korrekt_lage`), instead of mixed Swenglish.
- Entity friendly names must describe **function**, not just placement (e.g. a switch that physically powers a radio should say so, not just describe its location).

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

## 6) Shared templates (custom_templates)

For Jinja logic that's duplicated across 2+ package files (e.g. dew point calculation, time-of-day windows, "seconds since home_status changed"), define it once as a macro in `custom_templates/<topic>.jinja` and import it where needed:

```jinja
{% from 'dew_point.jinja' import dew_point %}
{{ dew_point(states('sensor.x_temperature'), states('sensor.x_humidity')) }}
```

Don't extract logic that's only used in one file — inline templates are fine for one-off cases.

## 7) Notes
- Some integration-focused package files may intentionally be “light” on metadata. For automation-heavy files, prefer the full header standard.

## Appendix: Lighting package convention

Most files under `packages/lights/` follow a consistent pattern:

- **Helper**: an `input_select.*` is the source of truth (manual override allowed).
- **Resolver**: an automation triggers on relevant state changes and calls a `script.*_set_correct_mode` script.
- **Decision**: `*_set_correct_mode` is the only place that decides and updates the `input_select`.
- **State machine**: a separate automation listens to the `input_select` and runs the matching “effect” script.

For UI “restore now”, `packages/lights/restore_all.yaml` provides `script.lights_set_correct_modes` which calls all `*_set_correct_mode` scripts.
