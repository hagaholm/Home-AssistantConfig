# Lights packages strategy report

Date: 2026-01-02

This repo uses a consistent “resolver + `*_set_correct_mode` + input_select state machine” strategy for area lighting packages under `packages/lights/`.

## Coverage matrix

| File | Resolver (calls `*_set_correct_mode`) | `*_set_correct_mode` script | State machine (input_select → scripts) | In restore-all (`script.lights_set_correct_modes`) |
|---|---|---|---|---|
| `packages/lights/inside.yaml` | Yes: `Innebelysning resolver` → `script.inside_set_correct_mode` | Yes | Yes | Yes |
| `packages/lights/kitchen.yaml` | Yes: `Köksbelysning resolver` → `script.kitchen_set_correct_mode` | Yes | Yes | Yes |
| `packages/lights/bathroom.yaml` | Yes: `Badrumsbelysning resolver` → `script.bathroom_set_correct_mode` | Yes | Yes | Yes |
| `packages/lights/hall.yaml` | Yes: `Halltak resolver` → `script.hall_set_correct_mode` | Yes | Yes | Yes |
| `packages/lights/garden.yaml` | Yes: `Trädgårdsbelysning resolver` → `script.garden_set_correct_mode` | Yes | Yes | Yes |
| `packages/lights/outdoor_room.yaml` | Yes: `Uterumsbelysning resolver` → `script.uterum_set_correct_mode` | Yes | Yes | Yes |
| `packages/lights/spabad.yaml` | Yes: `Spabad resolver` → `script.spabad_set_correct_mode` | Yes | Yes | Yes |
| `packages/lights/facade.yaml` | Yes: `Fasadbelysning resolver` → `script.facade_set_correct_mode` | Yes | Yes | Yes |
| `packages/lights/restore_all.yaml` | N/A (master) | N/A | N/A | N/A |
| `packages/lights/light_groups_standard.yaml` | N/A (groups) | N/A | N/A | N/A |
| `packages/lights/light_groups_seasonal.yaml` | N/A (groups) | N/A | N/A | N/A |
| `packages/lights/light_entities.yaml` | N/A (entity definitions) | N/A | N/A | N/A |
| `packages/lights/scenes.yaml` | N/A (scenes) | N/A | N/A | N/A |

## Notes / nits

- Naming consistency: `packages/lights/outdoor_room.yaml` uses entity/script names `light_uterum` / `uterum_set_correct_mode` (fine, but easy to mis-search if you expect “outdoor_room”).
- Naming risk: `packages/lights/spabad.yaml` uses `input_select.light_outside` (display name “Spabad”) and scripts `outside_light_on/off`. This is workable, but could become confusing if you ever add other “outside” lights not related to spabad.
- Loop safety: `*_set_correct_mode` scripts gate `input_select.select_option` on `desired_option != current_option`, which avoids obvious feedback loops with the input_select-driven state machines.
- Sensor safety: lux/temp handling generally uses `| float(none)` plus `is number` checks before comparisons.
- Edge behavior: in `packages/lights/spabad.yaml`, `workday_tomorrow` uses `is_state(..., 'on')`; if the sensor is `unknown/unavailable`, it behaves like `False` (so it may allow “Tänd” when you might prefer failing closed).
