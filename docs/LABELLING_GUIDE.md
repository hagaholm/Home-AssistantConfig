# Labeling Guide (Swedish)

## Purpose
Labels are flexible tags for organizing entities, devices, automations, scripts, and scenes across areas and functions. Use labels to enable multi-dimensional filtering (room, function, integration, type).

## Taxonomy
- Rum/Zoner: Kök, Hall, Vardagsrum, Sovrum, Louise rum, Andreas rum, Uterum, Friggebod, Förråd, Tvättstuga, Badrum, Garage, Ute/fasad (script emits Area: <namn> only)
- Belysning (funktion): Fönsterljus, Fasad, Vitrinskåp, Trädgård, Spabad, LED, Jul
- Integrationer: Shelly, Tellstick, Frigate, Reolink, MQTT, Volvo, Zwift, TTS, Harmony
- Sensortyp: Temperatur, Luftfuktighet, Ljusstyrka, Batteri, Tryck
- Domäner: Belysning, Strömbrytare, Sensor, Media, Fläkt, Helper, Automation, Script, Spårning, Knapp, Lås, Solskydd, Person
- Drift/Underhåll: Kritisk, Underhåll, Otillgänglig, Legacy

## Assignment Strategy
- Max 3–4 etiketter per entitet. Prioritera (Area: <Rum> + Funktion + Integration) eller (Area: <Rum> + Typ + Integration).
- Använd Jul endast på säsongsentiteter.
- Märk ventilationsrelaterade enheter med Ventilation + Shelly (vid användning av Shelly) + Area: <rum>.

## Workflow
1. Skapa etiketter: Inställningar → Etiketter → Ny etikett
2. Mass-assignera: Inställningar → Enheter/Entiteter → filtrera efter namn → Redigera → Etiketter
3. Generera CSV-förslag: kör extra/suggest_labels.ps1 (se kommandon nedan)

## Commands
```powershell
PowerShell -NoProfile -ExecutionPolicy Bypass -File ".\extra\suggest_labels.ps1"
# Output: .\docs\labels_mapping.csv
```

## Notes
- CSV visar EntityId, föreslagna Etiketter (Area: <rum>), Domän och referensfiler.
- Justera taxonomy och script-regler vid behov i extra/suggest_labels.ps1.
