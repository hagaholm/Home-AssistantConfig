# Home Assistant Configuration

Home automation configuration for a Swedish home with extensive lighting control, temperature monitoring, and smart home integrations.

## 📁 Structure

### Core Configuration
- **configuration.yaml** - Main config file (minimal, mostly includes)
- **customize.yaml** - Entity customizations and friendly names
- **secrets.yaml** - Sensitive data (not in version control)

### Packages
Organized by function for better maintainability:

#### `/packages/integrations/`
- **mqtt.yaml** - MQTT sensors (light sensors, 1-Wire temperature sensors)
- **tellstick.yaml** - Tellstick platform (switches and covers)
- **tts.yaml** - Google Translate text-to-speech
- **media_player.yaml** - Yamaha AV receiver

#### `/packages/lights/`
- **light_entities.yaml** - 14 switch-based light definitions
- **light_groups_standard.yaml** - 18 standard light groups (daily use)
- **light_groups_seasonal.yaml** - 9 Christmas variant light groups

#### `/packages/helpers/`
- **input_booleans.yaml** - Toggle helpers (Christmas mode)
- **input_selects.yaml** - Lighting scene and status selectors

#### `/packages/sensors/`
- **command_line_sensors.yaml** - System temperature monitoring

#### `/packages/` (other configs)
- Various template sensors, automations triggers, and integrations
- See individual files for documentation

### Automations & Scripts
Automations and scripts are now primarily managed via `packages/`.

The legacy include folders `automations/` and `script/` are intentionally kept minimal to avoid duplicate loading.

### Standards
- See `automations.md` for the repo’s automation/package documentation standard.
- Full template reference: `extra/AUTOMATION_TEMPLATE.md`
- Helper tools index: `extra/README.md`

## 🧭 Contributing

- Repo contribution guidelines: `CONTRIBUTING.md`

### Sensors
`/sensor/` - Additional sensor configurations

### Groups
`/group/` - Entity groupings for UI

### Logging
`/logging/` - Database and log configurations:
- **recorder.yaml** - Database config (7 day retention)
- **logger.yaml** - Log level settings
- **logbook.yaml** - Event history config

## 🎄 Seasonal Lighting System

The system supports automatic switching between standard and Christmas lighting:

1. **Toggle:** `input_boolean.christmas_light` (UI: "Använd julbelysning")
2. **Standard mode:** Uses `light_groups_standard.yaml` groups
3. **Christmas mode:** Uses `light_groups_seasonal.yaml` groups
4. **Scripts:** Automatically detect mode via templates in `/scripts/light_*.yaml`

### Light Groups
- **Dagbelysning** - Daytime lighting
- **Morgonbelysning** - Morning lighting  
- **Nattbelysning** - Night lighting
- **Bortabelysning** - Away mode lighting
- **Fasadbelysning** - Facade lighting
- **Utebelysning** - Outdoor lighting
- Room-specific: Kök, Vardagsrum, Hall, Sovrum, Badrum, Uterum, etc.

## 🌡️ Temperature Monitoring

### MQTT Sensors (via Raspberry Pi)
- **Outdoor:** Ute, Uteluft
- **Indoor:** Sovrum, Uterum, På vinden
- **Ventilation:** Avluft, Tilluft, Frånluft

### System Sensors
- CPU temperatures (Acpitz 0, 1, CPU)

### Alarms
Automated alerts for temperature thresholds in various zones.

## 💡 Light Control

### Input Selects (Scene Control)
- `light_inside` - Indoor scenes (9 options)
- `light_kitchen` - Kitchen brightness (4 levels)
- `light_bathroom` - Bathroom scenes with presence detection
- `light_outside` - Outdoor lighting
- `facade_lights` - Facade lighting modes
- `light_garden` - Garden lighting
- `light_uterum` - Outdoor room lighting

### Switch-as-Light Entities
14 lights defined as switch platforms (decorative/window lights)

### Native Light Entities
- Tellstick-controlled lights
- IKEA Trådfri bulbs
- Zigbee lights (hall ceiling - 13 bulbs)

## 🏠 Integrations

- **Tellstick** - RF433 switches and sensors
- **MQTT** - Sensor data from Raspberry Pi
- **Frigate** - Camera AI detection (separate config)
- **ESPHome** - ESP32 devices
- **Yamaha** - AV receiver control
- **Google TTS** - Text-to-speech

## 📊 Performance Settings

- **Database retention:** 7 days
- **Excluded from recorder:** camera, media_player, sun, calendar, update domain
- **Sensor scan intervals:** 60 seconds for command line sensors
- **MQTT broker:** Integrated (Mosquitto addon)

## 🔒 Security Notes

- All sensitive data in `secrets.yaml` (not committed)
- Archive files excluded from git
- API keys and passwords properly secured

## 🚀 Quick Start

1. Copy `secrets.yaml.example` to `secrets.yaml` and fill in values
2. Check configuration: `ha core check`
3. Restart: `ha core restart`

## 📝 Maintenance

- **Purge old data:** Automatic (7 days)
- **Backup:** Use HA built-in backup system
- **Updates:** Check for integration updates regularly

## 🐛 Known Issues

- Some entity naming inconsistencies (Swedish/English mix)
- Light entity names contain numbered variants (_2, etc.)

## 📚 Documentation Links

- System overview (architecture, flows, and file map): `SYSTEM_OVERVIEW.md`

- [Home Assistant Docs](https://www.home-assistant.io/docs/)
- [Package Documentation](https://www.home-assistant.io/docs/configuration/packages/)
- [Template Syntax](https://www.home-assistant.io/docs/configuration/templating/)
