# Home Assistant System Overview (Hagaholm)

This document is meant to be a **human-readable, GitHub-visible description** of the Home Assistant system in this repo: what it does, how it is structured, and where to find things.

- Audience: friends, visitors, future-you, and contributors.
- Scope: what’s represented in YAML in this repo (not your full HA UI state or device registries).
- Language: mainly Swedish (with some English where it helps).

> Privacy note
>
> This repo contains configuration patterns and sometimes device/entity names. Keep secrets in `secrets.yaml` (not committed) and be careful with IPs, usernames, camera paths, etc. before making the repo public.

---

## Table of contents

- 1. Quick summary
- 2. How the configuration loads
- 3. Repository layout
- 4. Core “modes”: Home/Away + scenes
- 5. Lighting system (the biggest subsystem)
- 6. Climate & temperature alarms
- 7. Ventilation (FTX)
- 8. Doorbell & camera snapshots
- 9. Media system (Harmony Hub)
- 10. Cameras & Frigate
- 11. System health and maintenance
- 12. Standards & quality gates
- 13. Where to add new features
- 14. Package inventory (index)

---

## 1) Quick summary

This Home Assistant setup is built around a few core goals:

1. **Reliable, predictable lighting** (indoor/outdoor, time-of-day scenes, presence-aware behavior, seasonal switching).
2. **Safety monitoring** (temperature alarms for important areas like fridge/freezer, garage, storage, etc.).
3. **Comfort automation** (ventilation control based on humidity/temperature).
4. **Convenient notifications** (doorbell events, critical alarms, status changes).
5. **Media control** (TV/radio/Chromecast/Spotify via Harmony).
6. **Camera AI events** (Frigate person/animal detection aggregation).

The entire repo uses a **packages-first** architecture so everything related to a topic lives together.

---

## 2) How the configuration loads

The main entrypoint is `configuration.yaml`:

- `homeassistant: packages: !include_dir_named packages` is the primary mechanism.
- Dashboards are YAML-mode dashboards referenced from `configuration.yaml`.
- Legacy include folders are still referenced:
  - `automation: !include_dir_merge_list automations/`
  - `script: !include_dir_merge_named script`

Those legacy folders are kept minimal/empty to avoid duplicate loading after migration to packages.

Key files:
- `configuration.yaml` – base + includes
- `customize.yaml` – entity customization
- `logging/` – recorder/logbook/logger
- `packages/` – the real system

---

## 3) Repository layout

Top level:

- `configuration.yaml` – minimal core config + includes
- `ui-lovelace.yaml`, `ui-camera.yaml`, `ui-automation.yaml`, `ui-ventilation.yaml` – dashboards
- `packages/` – everything grouped by domain/topic
- `automations/` and `script/` – legacy includes (kept minimal)
- `sensor/`, `group/`, `logging/` – smaller include trees
- `esphome/` – ESPHome device configs
- `custom_components/` – custom integrations
- `extra/` – helper scripts and docs (audits, templates)

---

## 4) Core “modes”: Home/Away + scenes

### Home status (central state)

The system uses a helper that acts as a “mode selector” for the household:

- `input_select.home_status` typically has modes like:
  - `Hemma` (active home)
  - `Sover` (home but calm/low activity)
  - `Borta` (away)

Presence detection is done via groups like:

- `group.track_for_home_devices` (device trackers)
- `group.persons` (person entities)

The home/away automation lives in `packages/presence/home_away.yaml` and does:

- Set home status based on group presence
- Allow motion-based “wake up” (e.g., kitchen presence) during daytime
- Turn off media when leaving

This mode is then referenced by many other automations (lighting, doorbell behavior, etc.).

### Phone change procedure

When a person changes to a new phone, keep the setup simple and stable:

1. Add the new phone's device tracker to the same person's entry in `packages/presence/person.yaml`.
2. Keep the old phone tracker for a transition period so presence does not flap during the change.
3. Verify that the person entity still changes to `home`/`not_home` correctly in Home Assistant.
4. Remove the old tracker only after the new one has been working reliably for several days.
5. If the new phone is not detected properly, check that the mobile app is correctly configured, that the tracker entity has the expected name, and that the phone is actually reporting as home/away.

This keeps the presence system reliable without creating a new person entity for every phone change.

---

## 5) Lighting system (the biggest subsystem)

Lighting is intentionally built as **state machines** + **scene scripts**.

For a concise package-by-package checklist (resolver + `*_set_correct_mode` + state machine + restore participation), see:

- `LIGHTS_PACKAGES_STRATEGY_REPORT.md`

### Key ideas

- Use `input_select` as a “desired scene” (source of truth).
- A resolver automation recalculates the correct option and updates the `input_select` via a `*_set_correct_mode` script.
- A state machine automation listens to `input_select` changes and calls the corresponding “effect” script.

### Indoor lighting

The core indoor lighting lives in `packages/lights/inside.yaml`.

Highlights:

- `input_select.light_inside` defines indoor lighting scene options (e.g. morning/day/evening/night/away/window).
- “State machine” automation `alias: Innebelysning` calls:
  - `script.morning_lights_on`, `script.daylights_on`, `script.eveninglights_on`, `script.night_light`, `script.away_lights_on`, `script.window_lights_on`, etc.
- Time-of-day automations set the scene based on `input_select.home_status`.

### Seasonal / Christmas mode

A global boolean toggles seasonal light groups:

- `input_boolean.christmas_light`

Dashboards also include conditional cards that show different entities depending on this boolean.

### Other lighting areas

Lighting is further grouped into separate files by area/topic (examples):

- `packages/lights/kitchen.yaml`
- `packages/lights/bathroom.yaml`
- `packages/lights/hall.yaml`
- `packages/lights/facade.yaml`
- `packages/lights/spabad.yaml`
- `packages/lights/garden.yaml`
- `packages/lights/outdoor_room.yaml`

There are also “infrastructure” files:

- `packages/lights/light_entities.yaml` – switch-as-light entities
- `packages/lights/light_groups_standard.yaml` – normal group definitions
- `packages/lights/light_groups_seasonal.yaml` – Christmas variants
- `packages/lights/scenes.yaml` – scene definitions (if used)

There is also a helper restore script for “fix it now” from the UI:

- `packages/lights/restore_all.yaml` – `script.lights_set_correct_modes` calls all `*_set_correct_mode` scripts

---

## 6) Climate & temperature alarms

Temperature monitoring and alerts are an important safety feature.

### Alarm package

Temperature alarms are consolidated into `packages/alerts/temperature.yaml`.

Typical behavior:

- Triggers for high/low temperature thresholds
- “for:” delays to avoid flapping
- Mobile notification via `notify.mobile_app_…`
- Guarded template triggers are used where sensors may be `unknown/unavailable` at startup

Covered zones include examples like:

- Förråd (storage)
- Friggebod
- Frys (freezer)
- Kyl (fridge)
- Uterum

### Climate packages

Some climate logic is in dedicated packages:

- `packages/climate/garage.yaml`
- `packages/climate/friggebod.yaml`

These typically coordinate heaters, thresholds, and safe fallback behavior.

---

## 7) Ventilation (FTX)

Ventilation control is a full subsystem.

- Main package: `packages/ventilation_system.yaml`
- Supporting scripts: `packages/ventilation/fan.yaml`
- Template sensors: `packages/template_ventilation_system.yaml`

Core behavior:

- Switches between normal and forced ventilation using a Shelly relay:
  - `switch.shelly1_c45bbe77099d`
- Uses humidity (bathroom) + temperature sensors to force high speed when needed
- Includes safety timers:
  - max timer (prevents forced mode forever)
  - stability timer (prevents rapid toggling)
- Diagnostic booleans track alarms and conditions

This is a good example of the repo’s “safety first” pattern: timers + explicit states + redundancy.

---

## 8) Doorbell & camera snapshots

Doorbell automation is in `packages/notifications/doorbell.yaml`.

What it does:

- Listens to doorbell switches (e.g. laundry/hall)
- Blinks a light as a local “chime” when people are home
- Takes camera snapshots to `/media/...` and sends a push notification with the image
- Behavior depends on `input_select.home_status` (day/night/away paths)

This ties together:

- Switches (doorbell input)
- Cameras
- `/media` storage
- Mobile app notifications

---

## 9) Media system (Harmony Hub)

Harmony control is in `packages/harmony_hub.yaml`.

It provides scripts like:

- `script.harmony_tv`
- `script.harmony_radio`
- `script.harmony_chromecast`
- `script.harmony_spotify`
- `script.harmony_off`

Automations also react to activity changes to manage related devices (like the subwoofer power).

Notes:

- Activity IDs are used (reliable, explicit)
- `mode: single` for scripts prevents collisions
- Delays are used to avoid IR conflicts

---

## 10) Cameras & Frigate

Frigate integration is represented via a set of package files:

- `packages/frigate_sensors.yaml` – aggregates counts and creates “any camera active” binary sensors
- `packages/frigate_person_detected.yaml`
- `packages/frigate_animal_detected.yaml`
- `packages/frigate_media.yaml`

The idea is to make “raw camera detections” easier to consume by:

- Creating summary counts (e.g. total persons detected across multiple cameras)
- Creating summary binary_sensors (e.g. any person active)

Some of these packages also include “reaction” automations (e.g. lighting + notifications) built on top of the summary sensors.

These summary sensors can be used by dashboards, notifications, and other automations.

---

## 11) System health and maintenance

System monitoring lives in `packages/system_info.yaml` (+ templates in `packages/template_system_info.yaml`).

It includes:

- Version sensors (installed vs current)
- Start/shutdown notifications
- Update-available notifications
- Optional (commented) SSH-based Raspberry Pi temperature monitoring

Logging is configured under `logging/`:

- `logging/recorder.yaml`
- `logging/logger.yaml`
- `logging/logbook.yaml`

---

## 12) Standards & quality gates

To keep the repo maintainable, there are a few “project rules”:

- Standards doc: `automations.md`
- Full canonical template: `extra/AUTOMATION_TEMPLATE.md`
- Contributing workflow: `CONTRIBUTING.md`
- Tools index: `extra/README.md`

There is also a repo audit script used to detect common configuration issues:

- `extra/ha_audit.py`

Typical checks include:

- Duplicate automation IDs
- Duplicate helper keys
- Missing/unknown references (best effort)
- Style/header consistency for package files

---

## 13) Where to add new features

Rule of thumb:

- If it’s a “topic” (lights, climate, ventilation, alerts, notifications): create/update a file under `packages/<domain>/`.
- Keep all related helpers + automations + scripts together in the same package file when practical.
- Preserve existing automation `id:` values when refactoring.

Examples:

- New temperature alarm → add to `packages/alerts/temperature.yaml`
- New room lighting behavior → add to `packages/lights/<room>.yaml` or to `packages/lights/inside.yaml` if it’s an indoor-scene feature
- New “push notification” behavior → `packages/notifications/<topic>.yaml`

---

## 14) Package inventory (index)

This is an index of what exists under `packages/`.

It is auto-generated to avoid documentation drift.
If you add/remove package files, refresh it with:

- `py extra/ha_docs_sync.py`

To validate in CI (or before committing) without modifying files:

- `py extra/ha_docs_sync.py --check`

<!-- AUTO:PACKAGE_INVENTORY_START -->

This section is auto-generated from the filesystem.
Run `py extra/ha_docs_sync.py` to refresh it.

### Top-level package files
- [packages/frigate_animal_detected.yaml](packages/frigate_animal_detected.yaml)
- [packages/frigate_media.yaml](packages/frigate_media.yaml)
- [packages/frigate_person_detected.yaml](packages/frigate_person_detected.yaml)
- [packages/frigate_sensors.yaml](packages/frigate_sensors.yaml)
- [packages/google.yaml](packages/google.yaml)
- [packages/harmony_hub.yaml](packages/harmony_hub.yaml)
- [packages/light_switch.yaml](packages/light_switch.yaml)
- [packages/lights_debug.yaml](packages/lights_debug.yaml)
- [packages/ljusstyrka_thresholds.yaml](packages/ljusstyrka_thresholds.yaml)
- [packages/person.yaml](packages/person.yaml)
- [packages/sensor_reading_missing.yaml](packages/sensor_reading_missing.yaml)
- [packages/system_info.yaml](packages/system_info.yaml)
- [packages/template_aqara_fp2_kitchen.yaml](packages/template_aqara_fp2_kitchen.yaml)
- [packages/template_harmony_hub.yaml](packages/template_harmony_hub.yaml)
- [packages/template_ljusstyrka.yaml](packages/template_ljusstyrka.yaml)
- [packages/template_lumi_ht_agl02_hall_is_not_working.yaml](packages/template_lumi_ht_agl02_hall_is_not_working.yaml)
- [packages/template_lumi_ht_agl02_livingroom.yaml](packages/template_lumi_ht_agl02_livingroom.yaml)
- [packages/template_lumi_weather_bathroom.yaml](packages/template_lumi_weather_bathroom.yaml)
- [packages/template_lumi_weather_uterum.yaml](packages/template_lumi_weather_uterum.yaml)
- [packages/template_sensor_reading_missing.yaml](packages/template_sensor_reading_missing.yaml)
- [packages/template_system_info.yaml](packages/template_system_info.yaml)
- [packages/template_ventilation_system.yaml](packages/template_ventilation_system.yaml)
- [packages/template_xiaomi_lumi_mgl01_hall.yaml](packages/template_xiaomi_lumi_mgl01_hall.yaml)
- [packages/template_xiaomi_lumi_mgl01_livingroom.yaml](packages/template_xiaomi_lumi_mgl01_livingroom.yaml)
- [packages/template_xiaomi_lumi_mgl01_louise_room_is_not_working.yaml](packages/template_xiaomi_lumi_mgl01_louise_room_is_not_working.yaml)
- [packages/tests.yaml](packages/tests.yaml)
- [packages/ventilation_system.yaml](packages/ventilation_system.yaml)
- [packages/ventilation_tuning.yaml](packages/ventilation_tuning.yaml)
- [packages/volvo.yaml](packages/volvo.yaml)
- [packages/working_at_home.yaml](packages/working_at_home.yaml)
- [packages/zwift.yaml](packages/zwift.yaml)

### Package folders
- **packages/alerts/**
  - [packages/alerts/devices_offline.yaml](packages/alerts/devices_offline.yaml)
  - [packages/alerts/temperature.yaml](packages/alerts/temperature.yaml)
- **packages/automations/**
  - [packages/automations/input_select_light_control.yaml](packages/automations/input_select_light_control.yaml)
- **packages/climate/**
  - [packages/climate/friggebod.yaml](packages/climate/friggebod.yaml)
  - [packages/climate/garage.yaml](packages/climate/garage.yaml)
- **packages/helpers/**
  - [packages/helpers/input_booleans.yaml](packages/helpers/input_booleans.yaml)
  - [packages/helpers/input_selects.yaml](packages/helpers/input_selects.yaml)
- **packages/integrations/**
  - [packages/integrations/media_player.yaml](packages/integrations/media_player.yaml)
  - [packages/integrations/mqtt.yaml](packages/integrations/mqtt.yaml)
  - [packages/integrations/tellstick.yaml](packages/integrations/tellstick.yaml)
  - [packages/integrations/tts.yaml](packages/integrations/tts.yaml)
- **packages/lights/**
  - [packages/lights/bathroom.yaml](packages/lights/bathroom.yaml)
  - [packages/lights/debug.yaml](packages/lights/debug.yaml)
  - [packages/lights/facade.yaml](packages/lights/facade.yaml)
  - [packages/lights/garden.yaml](packages/lights/garden.yaml)
  - [packages/lights/hall.yaml](packages/lights/hall.yaml)
  - [packages/lights/inside.yaml](packages/lights/inside.yaml)
  - [packages/lights/kitchen.yaml](packages/lights/kitchen.yaml)
  - [packages/lights/light_entities.yaml](packages/lights/light_entities.yaml)
  - [packages/lights/light_groups_seasonal.yaml](packages/lights/light_groups_seasonal.yaml)
  - [packages/lights/light_groups_standard.yaml](packages/lights/light_groups_standard.yaml)
  - [packages/lights/outdoor_room.yaml](packages/lights/outdoor_room.yaml)
  - [packages/lights/restore_all.yaml](packages/lights/restore_all.yaml)
  - [packages/lights/scenes.yaml](packages/lights/scenes.yaml)
  - [packages/lights/spabad.yaml](packages/lights/spabad.yaml)
- **packages/notifications/**
  - [packages/notifications/doorbell.yaml](packages/notifications/doorbell.yaml)
- **packages/presence/**
  - [packages/presence/home_away.yaml](packages/presence/home_away.yaml)
- **packages/scripts/**
  - [packages/scripts/godnatt.yaml](packages/scripts/godnatt.yaml)
- **packages/sensors/**
  - [packages/sensors/command_line_sensors.yaml](packages/sensors/command_line_sensors.yaml)
- **packages/ventilation/**
  - [packages/ventilation/fan.yaml](packages/ventilation/fan.yaml)

<!-- AUTO:PACKAGE_INVENTORY_END -->

---

## Appendix: “How to understand the system quickly” (suggested reading order)

## Diagram (main flows)

The diagram below is intentionally high-level. It shows the *core state* (`input_select.home_status`) and how it drives the biggest subsystems.

```mermaid
flowchart TD
  %% Core inputs
  P1[group.track_for_home_devices]
  P2[group.persons]
  M1[binary_sensor.kok_narvaro]

  %% Core mode
  HS[input_select.home_status\n(Hemma / Sover / Borta)]

  %% Presence automation
  AHA[packages/presence/home_away.yaml\nAutomation: Hem borta status styrning]

  %% Lighting state machine
  LI[input_select.light_inside\n(Scene selector)]
  ALI[packages/lights/inside.yaml\nState machine automation]
  SLI[Scripts\n(morning/day/evening/night/away/window)]
  LGT[Lights & groups\n(standard + seasonal)]
  XMAS[input_boolean.christmas_light]

  %% Doorbell
  DB[packages/notifications/doorbell.yaml\nDoorbell automation]
  CAM[Cameras\n(snapshot to /media)]
  PUSH[Mobile notifications\nnotify.mobile_app_*]

  %% Ventilation
  VFTX[packages/ventilation_system.yaml\nFTX control automations]
  FAN[packages/ventilation/fan.yaml\nScripts: normal/forced]
  RELAY[switch.shelly1_c45bbe77099d]

  %% Alerts
  TALT[packages/alerts/temperature.yaml\nTemperature alarms]
  TSENS[Temp/Humidity sensors\n(MQTT, Zigbee, etc.)]

  %% Media
  HARM[packages/harmony_hub.yaml\nHarmony scripts + automations]
  REMOTE[remote.harmony_hub]

  %% Relationships
  P1 --> AHA
  P2 --> AHA
  M1 --> AHA
  AHA --> HS

  HS -->|drives| LI
  LI --> ALI
  ALI --> SLI
  SLI --> LGT
  XMAS -->|selects| LGT

  HS -->|affects behavior| DB
  DB --> CAM
  DB --> PUSH

  TSENS --> VFTX
  VFTX --> FAN
  FAN --> RELAY

  TSENS --> TALT
  TALT --> PUSH

  HARM --> REMOTE
  HS -->|turn off when leaving| HARM
```

If someone is new to the repo, this order usually makes it click:

1. `configuration.yaml` (how things are included)
2. `automations.md` (rules and conventions)
3. `packages/presence/home_away.yaml` (what “home/away” means)
4. `packages/lights/inside.yaml` (the indoor state machine approach)
5. `packages/alerts/temperature.yaml` (how alerts are built)
6. `packages/ventilation_system.yaml` (largest non-light automation)
7. `packages/notifications/doorbell.yaml` (end-to-end event → snapshot → push)
8. `extra/README.md` (tooling, audits)

---

If you want, I can also generate a **diagram** (Mermaid) of the main flows (presence → home_status → lighting/media/doorbell) and embed it here.
