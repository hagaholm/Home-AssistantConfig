# Contributing

This repository is a Home Assistant configuration organized around **packages**.

## Documentation

- Standards (how to write/structure automations, templates, packages): see `automations.md`
- Full header/template reference: `extra/AUTOMATION_TEMPLATE.md`

## Structure rules (practical)

- Prefer adding new logic under `packages/<domain>/...`.
- Keep package files focused (one topic per file when reasonable).
- Split a package into `helpers/` + topic file + `packages/scripts/<domain>/` once it passes ~200 lines or has 3+ scripts — see `automations.md` §1.
- Preserve existing `id:` values when moving/consolidating automations.
- Extract Jinja that's duplicated across 2+ files into a `custom_templates/*.jinja` macro instead of copy-pasting — see `automations.md` §6.

## Safety rules

- When templating numbers: guard `unknown/unavailable/''` before `|float`.
- For `device_class: timestamp` templates: never return the string `unavailable`.

## Validation

Run the local audit script before committing:

- `py extra/ha_audit.py`
- `py extra/ha_audit.py --style`

## Keeping docs in sync

I (Copilot) will update docs when I change logic in this repo during a session, but there is no background “auto-update” after that.

To prevent docs drift over time:

- Refresh the package index in `SYSTEM_OVERVIEW.md`: `py extra/ha_docs_sync.py`
- Or validate without modifying files (useful in CI): `py extra/ha_docs_sync.py --check`

Rule of thumb: if you add/remove package files or make a behavior change that affects how the system works, update `SYSTEM_OVERVIEW.md` (high-level) and the local file header comments (low-level).

### Optional: automatic checks on commit/push (no PR needed)

If you commit + push directly (no PRs), you can still automate consistency checks locally using tracked git hooks.

This repo includes hooks under `githooks/`:

- `pre-commit`: runs `extra/ha_docs_sync.py` and stages `SYSTEM_OVERVIEW.md`
- `pre-push`: runs docs `--check` + `extra/ha_audit.py` (+ `--style`) and aborts push on failure

Enable them once:

- `git config core.hooksPath githooks`

Disable later (if needed):

- `git config --unset core.hooksPath`

Home Assistant UI:

- Developer Tools → YAML → Check Configuration
