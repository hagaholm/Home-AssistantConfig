# Home Assistant Automation Template

## Rekommenderad Standard (Förbättrad version av light_bathroom.yaml)

```yaml
#######################################################
#                                                     #
#              [AUTOMATION NAMN]                      #
#                                                     #
#######################################################
#
# METADATA:
# Skapad: YYYY-MM-DD
# Senast ändrad: YYYY-MM-DD
# Version: 1.0
# Författare: [Ditt namn]
#
# BESKRIVNING:
# [Kort beskrivning av vad automationen gör]
# [Förklara övergripande logik och syfte]
# [Max 3-4 rader]
#
# HÅRDVARA/ENTITETER:
# - Sensor 1: sensor.example_sensor
# - Switch 1: switch.example_switch
# - Input: input_select.example
# - Output: light.example_light
#
# TRIGGRAR:
# - [Lista alla triggers och när de aktiveras]
# - [Använd konkreta exempel]
#
# VILLKOR (om relevanta):
# - [Lista alla conditions]
# - [Förklara varför de behövs]
#
# TILLSTÅND (för state machines):
# - Tillstånd 1: Beskrivning och när det används
# - Tillstånd 2: Beskrivning och när det används
# - Tillstånd 3: Beskrivning och när det används
#
# LOGIK/ÖVERGÅNGAR:
# TÄND/ON:
# - Scenario 1: Villkor → Åtgärd
# - Scenario 2: Villkor → Åtgärd
#
# SLÄCK/OFF:
# - Scenario 1: Villkor → Åtgärd
# - Scenario 2: Villkor → Åtgärd
#
# SÄKERHET/GRÄNSVÄRDEN:
# - [Viktig information om säkerhet]
# - [Hysteresis, timeouts, fail-safes]
#
# INTEGRATION:
# - [Hur automationen integrerar med andra system]
# - [Beroenden på andra automationer/scripts]
# - [UI-integrationer]
#
# KÄNDA BEGRÄNSNINGAR:
# - [Eventuella begränsningar eller edge cases]
#
# ÄNDRINGSLOGG:
# v1.0 (YYYY-MM-DD): Initial version
# v1.1 (YYYY-MM-DD): Lade till X funktionalitet
#######################################################


#######################################################
#                                                     #
#              AUTOMATIONER FÖR [NAMN]                #
#                                                     #
#######################################################

- alias: Automation Namn
  id: 'unique_id_here'
  description: >
    Kort beskrivning som visas i UI
  mode: single  # single|restart|queued|parallel
  max: 10  # Max instanser (för queued/parallel)
  max_exceeded: silent  # silent|warning|error

  trigger:
    - platform: state
      entity_id: sensor.example
      # ... mer triggers

  condition:
    - condition: state
      entity_id: input_boolean.example
      state: 'on'
    # ... mer conditions

  action:
    - choose:
        # Scenario 1
        - alias: Beskrivande namn för scenario
          conditions:
            - condition: state
              entity_id: input_select.example
              state: 'värde'
          sequence:
            - service: light.turn_on
              target:
                entity_id: light.example
              data:
                brightness: 255

        # Scenario 2
        - alias: Beskrivande namn för scenario 2
          conditions:
            - condition: numeric_state
              entity_id: sensor.example
              above: 20
          sequence:
            - service: switch.turn_off
              entity_id: switch.example

      # Default action om inget scenario matchar
      default:
        - service: notify.mobile_app
          data:
            message: "Ingen matchning i automation"
```

---

## Alternativ: Minimal Standard (för enklare automationer)

```yaml
#######################################################
#              [AUTOMATION NAMN]                      #
#######################################################
#
# BESKRIVNING: [En rad förklaring]
# TRIGGER: [När den körs]
# ÅTGÄRD: [Vad den gör]
#
# Skapad: YYYY-MM-DD | Version: 1.0
#######################################################

- alias: Automation Namn
  id: 'unique_id'
  mode: single
  
  trigger:
    # ...
  
  action:
    # ...
```

---

## Bästa Praxis

### 1. **Mode-inställningar**
- `single`: Standard, en exekvering åt gången (rekommenderad för ljus/värme)
- `restart`: Avbryt pågående, starta ny (för positioneringautomationer)
- `queued`: Kö flera (för meddelanden, larm)
- `parallel`: Flera samtidigt (för oberoende åtgärder)

### 2. **Choose vs If-Then-Else**
- Använd `choose` för 3+ scenarios
- Använd `if` för enkla 1-2 villkor
- Alltid sätt `alias` på varje choose-scenario för debugging

### 3. **ID-hantering**
- Använd numeriska ID:n (genererade av HA): `'1234567890123'`
- Använd beskrivande ID:n för nya: `'kitchen_light_state_machine'`
- **Återanvänd befintliga ID:n vid konsolidering**

### 4. **Kommentarer**
- Header: Övergripande dokumentation
- Inline: Förklara VARFÖR, inte VAD (koden visar VAD)
- Alias: Använd svenska, beskrivande namn

### 5. **Struktur**
```yaml
# 1. Header med dokumentation
# 2. Triggers (alla logiska triggers)
# 3. Conditions (globala villkor)
# 4. Actions med choose-block (för olika scenarios)
# 5. Default action (fallback)
```

### 6. **Namngivning**
- File: `light_bathroom.yaml` (svensk beskrivning)
- Alias: `Badrumsbelysning` (visas i UI, svenska)
- ID: `'bathroom_light_all_in_one'` (engelsk, snake_case)
- Entity: `automation.badrumsbelysning` (genereras av HA från alias)

### 7. **Versionering**
```yaml
# v1.0 (2025-12-27): Initial version
# v1.1 (2026-01-15): Lade till nattläge
# v2.0 (2026-03-01): Konsoliderade 3 automationer
```

---

## Checklista innan commit

- [ ] Header-dokumentation komplett
- [ ] Alla entiteter dokumenterade under HÅRDVARA
- [ ] Alla scenarios har `alias`
- [ ] `mode` är satt korrekt
- [ ] ID återanvänt från konsolidering (om relevant)
- [ ] Kommentarer förklarar VARFÖR, inte VAD
- [ ] YAML syntax validerad (no tabs, correct indentation)
- [ ] Testad i Home Assistant
- [ ] UI-referenser uppdaterade (om relevant)

---

## Exempel på Bra vs Dålig Kommentar

❌ **Dåligt:**
```yaml
# Tänder lampan
- service: light.turn_on
```

✅ **Bra:**
```yaml
# Nattläge för att undvika att väcka familjen
- service: light.turn_on
  data:
    brightness: 10
```

---

## Verktyg för Validering

```bash
# Validera YAML syntax
yamllint automations/

# Testa i Home Assistant
# Developer Tools → YAML → Check Configuration
```

---

## Template för Konsolidering

När du slår ihop flera automationer:

```yaml
# KONSOLIDERINGSHISTORIK:
# Denna automation ersätter följande tidigare automationer:
# - [Automation 1 namn] (ID: xxxx) - Skapad: YYYY-MM-DD
# - [Automation 2 namn] (ID: xxxx) - Skapad: YYYY-MM-DD  
# - [Automation 3 namn] (ID: xxxx) - Skapad: YYYY-MM-DD
# 
# Konsoliderad: YYYY-MM-DD
# Behållet ID: xxxx (från Automation 1)
# Anledning: Bättre underhåll, reducerad overhead, enklare logik
```
