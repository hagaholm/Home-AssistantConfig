from pathlib import Path

content = r'''title: Documentation
views:
  - path: system-overview
    title: Home Assistant system overview
    icon: mdi:home-assistant
    theme: default
    badges: []
    cards:
      - type: entities
        title: Language
        entities:
          - entity: input_boolean.documentation_language_swedish
            name: Show Swedish text
            icon: mdi:translate

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "off"
        card:
          type: markdown
          title: Home Assistant system overview
          content: |
            # Home Assistant system overview

            This setup is organized around comfort, safety, convenience, and automation.

            ## Easy version

            In simple words, this Home Assistant configuration is a connected system that helps the house behave in a smart way.
            It handles lighting, climate, presence, notifications, media, and camera intelligence.

            ## More advanced version

            The system is built as a package-based Home Assistant configuration.
            The main entrypoint is configuration.yaml, while the actual logic is split into packages by area such as lights, climate, ventilation, presence, notifications, media, and frigate.
            Helpers, templates, scripts, and automations work together so the house can react to state changes in a predictable way.
            The dashboard files and custom integrations extend the base system with a user-friendly interface and extra integrations.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Översikt över Home Assistant-systemet
          content: |
            # Översikt över Home Assistant-systemet

            Den här uppsättningen är organiserad kring komfort, säkerhet, bekvämlighet och automatisering.

            ## Enkel version

            I enkla ord är denna Home Assistant-konfiguration ett sammankopplat system som hjälper huset att agera på ett smart sätt.
            Den hanterar belysning, klimat, närvaro, notiser, media och kameraintelligens.

            ## Mer avancerad version

            Systemet är byggt som en paketbaserad Home Assistant-konfiguration.
            Huvudingången är configuration.yaml, medan den egentliga logiken är uppdelad i paket efter område som belysning, klimat, ventilation, närvaro, notiser, media och frigate.
            Hjälpare, mallar, skript och automatiseringar fungerar tillsammans så att huset kan reagera på tillståndsändringar på ett förutsägbart sätt.
            Dashboardfilerna och anpassade integrationer bygger ut systemet med ett användarvänligt gränssnitt och extra funktioner.

  - path: lighting-docs
    title: Lighting
    icon: mdi:lightbulb
    theme: default
    badges: []
    cards:
      - type: entities
        title: Language
        entities:
          - entity: input_boolean.documentation_language_swedish
            name: Show Swedish text
            icon: mdi:translate

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "off"
        card:
          type: markdown
          title: Lighting documentation
          content: |
            # Lighting

            ## Easy version

            Lighting is one of the biggest parts of the house automation.
            It controls indoor and outdoor lights, seasonal behavior, scenes, and the way light changes depending on time, presence, and home mode.

            ## More advanced version

            The lighting logic is organized around scenes, state transitions, and grouped light entities.
            The configuration uses files such as packages/lights/inside.yaml, facade.yaml, garden.yaml, hall.yaml, kitchen.yaml, and scenes.yaml to define how lights behave in different modes such as morning, day, evening, night, away, and window.
            In practice, the automations combine time-based triggers, presence data, and home-mode conditions so that lighting can be adjusted in a consistent and layered way.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Belysning
          content: |
            # Belysning

            ## Enkel version

            Belysning är en av de största delarna i husautomationen.
            Den styr inomhus- och utomhusljus, säsongsbeteende, scener och hur ljuset ändras beroende på tid, närvaro och hemmaläge.

            ## Mer avancerad version

            Belysningslogiken är organiserad kring scener, tillståndsövergångar och grupperade ljusentiteter.
            Konfigurationen använder filer som packages/lights/inside.yaml, facade.yaml, garden.yaml, hall.yaml, kitchen.yaml och scenes.yaml för att definiera hur lampor ska bete sig i olika lägen som morgon, dag, kväll, natt, borta och fönster.
            I praktiken kombinerar automatiseringarna tidsbaserade triggar, närvarodata och hemmalägesvillkor så att belysningen kan justeras på ett konsekvent och lagerindelat sätt.

  - path: climate-docs
    title: Climate & alarms
    icon: mdi:thermometer
    theme: default
    badges: []
    cards:
      - type: entities
        title: Language
        entities:
          - entity: input_boolean.documentation_language_swedish
            name: Show Swedish text
            icon: mdi:translate

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "off"
        card:
          type: markdown
          title: Climate and alarms
          content: |
            # Climate and alarms

            ## Easy version

            This part watches temperature and humidity in important rooms and outdoor spaces.
            It raises alerts if values move outside acceptable ranges and helps protect sensitive areas.

            ## More advanced version

            The climate and alarm logic is built around thresholds, delays, and notification routing.
            Files such as packages/alerts/temperature.yaml, packages/climate/friggebod.yaml, packages/climate/garage.yaml, and packages/climate/ute.yaml define the monitoring behavior and the conditions for raising alerts.
            The advanced pattern is to avoid reacting to short flickers, while still giving fast and reliable warnings when a real issue persists.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Klimat och larm
          content: |
            # Klimat och larm

            ## Enkel version

            Den här delen övervakar temperatur och fuktighet i viktiga rum och utomhusområden.
            Den skapar larm om värden går utanför acceptabla intervall och hjälper till att skydda känsliga områden.

            ## Mer avancerad version

            Klimat- och larmlogiken är byggd kring trösklar, fördröjningar och notisrouting.
            Filer som packages/alerts/temperature.yaml, packages/climate/friggebod.yaml, packages/climate/garage.yaml och packages/climate/ute.yaml definierar övervakningsbeteendet och villkoren för att skapa larm.
            Det avancerade mönstret är att undvika reaktion på korta fluktuationer, samtidigt som man ger snabba och pålitliga varningar när ett verkligt problem kvarstår.

  - path: ventilation-docs
    title: Ventilation
    icon: mdi:fan
    theme: default
    badges: []
    cards:
      - type: entities
        title: Language
        entities:
          - entity: input_boolean.documentation_language_swedish
            name: Show Swedish text
            icon: mdi:translate

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "off"
        card:
          type: markdown
          title: Ventilation
          content: |
            # Ventilation

            ## Easy version

            The ventilation part controls air flow and fan speed so the house stays comfortable and healthy.
            It reacts to humidity, temperature, and time-based conditions.

            ## More advanced version

            Ventilation is implemented as a control loop with thresholds and safety logic.
            Files such as packages/ventilation/ventilation_system.yaml, packages/ventilation/fan.yaml, and packages/sensors/template_sensors/template_ventilation_system.yaml define the fan modes and the conditions that force higher speed.
            The advanced behavior is not just on/off; it uses state transitions, timers, and fallback logic to avoid unstable or overly aggressive behavior.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Ventilation
          content: |
            # Ventilation

            ## Enkel version

            Ventilationsdelen styr luftflöde och fläkthastighet så att huset blir bekvämt och hälsosamt.
            Den reagerar på fuktighet, temperatur och tidsbaserade villkor.

            ## Mer avancerad version

            Ventilation implementeras som en styrloop med trösklar och säkerhetslogik.
            Filer som packages/ventilation/ventilation_system.yaml, packages/ventilation/fan.yaml och packages/sensors/template_sensors/template_ventilation_system.yaml definierar fläktlägen och villkoren som tvingar högre hastighet.
            Det avancerade beteendet handlar inte bara om på/av, utan använder tillståndsövergångar, timers och reservlogik för att undvika instabilt eller för aggressivt beteende.

  - path: presence-docs
    title: Presence & modes
    icon: mdi:account-multiple
    theme: default
    badges: []
    cards:
      - type: entities
        title: Language
        entities:
          - entity: input_boolean.documentation_language_swedish
            name: Show Swedish text
            icon: mdi:translate

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "off"
        card:
          type: markdown
          title: Presence and modes
          content: |
            # Presence and modes

            ## Easy version

            This part answers one simple question: is someone home, away, or asleep?
            That information is reused by many automations.

            ## More advanced version

            Presence is treated as a shared state layer that influences many other subsystems.
            Files such as packages/presence/home_away.yaml, packages/presence/person.yaml, and packages/presence/working_at_home.yaml define how the home mode changes and how people are represented.
            The deeper idea is that one consistent presence model keeps the rest of the automations simpler, because they can rely on a stable state instead of guessing from many individual inputs.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Närvaro och lägen
          content: |
            # Närvaro och lägen

            ## Enkel version

            Den här delen svarar på en enkel fråga: är någon hemma, borta eller sover?
            Den informationen används av många automatiseringar.

            ## Mer avancerad version

            Närvaro behandlas som ett gemensamt tillståndslager som påverkar många andra delsystem.
            Filer som packages/presence/home_away.yaml, packages/presence/person.yaml och packages/presence/working_at_home.yaml definierar hur hemmaläget ändras och hur personer representeras.
            Den djupare idén är att en konsekvent närvaromodell gör resten av automatiseringarna enklare, eftersom de kan lita på ett stabilt tillstånd istället för att gissa från många individuella ingångar.

  - path: notifications-docs
    title: Notifications
    icon: mdi:bell
    theme: default
    badges: []
    cards:
      - type: entities
        title: Language
        entities:
          - entity: input_boolean.documentation_language_swedish
            name: Show Swedish text
            icon: mdi:translate

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "off"
        card:
          type: markdown
          title: Notifications and doorbell
          content: |
            # Notifications and doorbell

            ## Easy version

            This area handles ring events, snapshots, and phone notifications.
            When the doorbell is pressed, the house can respond with lights, images, and alerts.

            ## More advanced version

            The flow is usually triggered by a hardware event and then passed through one or more automations.
            The logic in packages/notifications/doorbell.yaml connects the trigger, the camera snapshot, and the notification action into a reliable event chain.
            The advanced part is not only sending a message but doing so in a context-aware way, depending on the current state of the house and the camera system.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Notiser och ringklocka
          content: |
            # Notiser och ringklocka

            ## Enkel version

            Det här området hanterar ringhändelser, ögonblicksbilder och telefonnotiser.
            När ringklockan aktiveras kan huset reagera med ljus, bilder och varningar.

            ## Mer avancerad version

            Flödet startas vanligtvis av en hårdvaruhändelse och skickas sedan vidare genom en eller flera automatiseringar.
            Logiken i packages/notifications/doorbell.yaml kopplar ihop utlöser, kamerasnapshot och notifieringsåtgärd till en pålitlig händelsekedja.
            Den avancerade delen handlar inte bara om att skicka ett meddelande utan att göra det på ett kontextmedvetet sätt, beroende på husets aktuella tillstånd och kamerasystemet.

  - path: media-docs
    title: Media
    icon: mdi:play-box-multiple
    theme: default
    badges: []
    cards:
      - type: entities
        title: Language
        entities:
          - entity: input_boolean.documentation_language_swedish
            name: Show Swedish text
            icon: mdi:translate

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "off"
        card:
          type: markdown
          title: Media and Harmony
          content: |
            # Media and Harmony

            ## Easy version

            This part controls media devices such as TV, radio, Chromecast, and Spotify in a consistent way.
            It connects the media experience to the rest of the house.

            ## More advanced version

            Media behavior is linked to device state, power handling, and activity management.
            Files such as packages/media/harmony_hub.yaml and packages/integrations/media_player.yaml define how media devices behave when the house changes mode or when a user starts a routine.
            The advanced design is to treat media as part of the overall house state rather than as an isolated feature.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Media och Harmony
          content: |
            # Media och Harmony

            ## Enkel version

            Den här delen styr medieenheter som TV, radio, Chromecast och Spotify på ett konsekvent sätt.
            Den kopplar medieupplevelsen till resten av huset.

            ## Mer avancerad version

            Mediebeteendet är kopplat till enhetsstatus, strömhantering och aktivitetsstyrning.
            Filer som packages/media/harmony_hub.yaml och packages/integrations/media_player.yaml definierar hur medieenheter beter sig när huset ändrar läge eller när en användare startar en rutin.
            Den avancerade designen är att behandla media som en del av husets övergripande tillstånd snarare än som en isolerad funktion.

  - path: frigate-docs
    title: Frigate
    icon: mdi:cctv
    theme: default
    badges: []
    cards:
      - type: entities
        title: Language
        entities:
          - entity: input_boolean.documentation_language_swedish
            name: Show Swedish text
            icon: mdi:translate

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "off"
        card:
          type: markdown
          title: Frigate documentation
          content: |
            # Frigate

            ## Easy version

            Frigate watches the cameras, notices movement, and tries to understand what it sees.
            It can react to people, animals, faces, and other events.

            ## More advanced version

            Frigate is used as the camera analysis layer that feeds Home Assistant with event-based information.
            The logic in packages/frigate/frigate_person_detected.yaml, frigate_animal_detected.yaml, frigate_intruder_alarm.yaml, frigate_face_detection.yaml, frigate_sensors.yaml, and frigate_media.yaml turns those raw detections into useful automations.
            The deeper design includes summary sensors, MQTT event handling, state filtering, and cleanup routines so the system can react quickly without becoming noisy or storage-heavy.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Frigate-dokumentation
          content: |
            # Frigate

            ## Enkel version

            Frigate bevakar kamerorna, märker rörelse och försöker förstå vad den ser.
            Den kan reagera på människor, djur, ansikten och andra händelser.

            ## Mer avancerad version

            Frigate används som lagret för kameraanalys som matar Home Assistant med händelsebaserad information.
            Logiken i packages/frigate/frigate_person_detected.yaml, frigate_animal_detected.yaml, frigate_intruder_alarm.yaml, frigate_face_detection.yaml, frigate_sensors.yaml och frigate_media.yaml omvandlar dessa råa detektioner till användbara automatiseringar.
            Den djupare designen inkluderar sammanfattningssensorer, MQTT-händelsehantering, tillståndsfiltrering och rensningsrutiner så att systemet kan reagera snabbt utan att bli störigt eller lagringsintensivt.
'''

Path(r'c:/Users/micke/Documents/GitHub/Home-AssistantConfig/documentation.ui').write_text(content, encoding='utf-8')
