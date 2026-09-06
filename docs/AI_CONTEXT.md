# AI Context: Home Assistant

Kort startpunkt för AI-assistenter som arbetar med detta repo och Home Assistant.

## Läs först

1. `docs/SYSTEM_OVERVIEW.md` - arkitektur, laddning och större delsystem.
2. `docs/automations.md` - regler för nya och ändrade packages/automationer.
3. `docs/AI_CONTEXT.md` - denna fil, för routing och felsökningspolicy.

## Systemets form

- Home Assistant-konfigurationen är packages-first.
- `configuration.yaml` är huvudsakligen en entrypoint med includes.
- Den funktionella konfigurationen ligger främst under `packages/`.
- YAML-dashboarder ligger i `ui-*.yaml` och ska inte behandlas som storage-dashboarder.
- `automations/` och `script/` är legacy-includes och ska normalt inte fyllas på.
- `custom_components/` innehåller lokala integrationer; ändra dem bara när uppgiften gäller integrationens kod.
- `extra/` innehåller audit-, inventerings- och dokumentationsverktyg.

## Ändringsregler

- Läs närliggande package och relaterade helpers/scripts innan ändring.
- Följ topic-strukturen `packages/<domain>/<topic>.yaml`.
- Bevara befintliga automation-id:n och entity-id:n.
- Lägg ny funktion där motsvarande funktion redan bor; skapa inte parallella implementationer.
- Använd native Home Assistant triggers/conditions/actions när de räcker.
- Använd templates främst i data, meddelanden, event_data och variables.
- Ändra aldrig secrets eller `.storage` direkt.
- Validera med `py extra/ha_audit.py` och relevant smal kontroll efter ändring.
- Läs live-state, traces och registry via MCP när frågan gäller nuläget.

## Snabb routing

| Fråga | Börja här |
|---|---|
| Var ska en ny automation ligga? | `docs/automations.md`, sedan relevant `packages/<domain>/` |
| Varför körs inte en automation? | live state + automation trace via MCP, därefter package-filen |
| Vilka automationer finns? | MCP overview/search; repo-filerna är inte hela sanningen |
| Vilka entity IDs finns nu? | MCP overview/search; använd repo-inventering som komplement |
| Belysning | `docs/LIGHTS_PACKAGES_STRATEGY_REPORT.md`, `packages/lights/` |
| Ventilation | `packages/ventilation_system.yaml`, `packages/ventilation/` |
| Kameror/Frigate | `packages/frigate/`, `custom_components/frigate/`, `frigate/` |
| UI/dashboard | relevant `ui-*.yaml`; kontrollera YAML-mode först |
| Kvalitetskontroll | `extra/README.md`, `py extra/ha_audit.py` |

## Live kontra dokumenterat

Dokumentera här och i övriga docs sådant som är stabilt: arkitektur, avsikt, prioriteringar,
namngivning, kända begränsningar och felsökningsvägar. Hämta följande live via MCP i stället
för att kopiera stora listor till repo:t:

- antal och status för automationer, scripts och helpers
- aktuella entity states och unavailable-entiteter
- devices, areas och integration registry
- senaste automation traces och loggar
- versioner, uppdateringar och systemhälsa

## Säkerhets- och återställningspolicy

- Skriv aldrig tokens, lösenord, API-nycklar eller kamerauppgifter i dokumentationen.
- Ta backup före ändringar med större blast radius.
- Vid osäkerhet: läs konfiguration och trace först; gör sedan minsta möjliga ändring.
- En ändring ska kunna verifieras och återställas utan att andra funktioner påverkas.

## Underhåll

Den här filen ska hållas kort. Lägg detaljer i ämnesspecifika docs och länka hit endast när
informationen behövs för routing. Genererade inventeringar ska märkas som genererade och får
inte ersätta live-kontroll i Home Assistant.
