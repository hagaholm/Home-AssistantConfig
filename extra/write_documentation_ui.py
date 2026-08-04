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

            ## Summary

            This is a package-based Home Assistant setup that manages everyday comfort and house automation in a structured way.
            It covers lighting, climate, presence, notifications, media, and camera-based awareness.

            ## Detailed description

            The system is organized around a central configuration entrypoint in configuration.yaml.
            The real behavior lives in separate package files that group automations, helpers, scripts, sensors, and templates by topic.
            This structure keeps the logic modular, so changes can be made in one area without rewriting the entire house behavior.
            In practice, the system is built as a network of smaller subsystems that all use the same shared state model: presence, home mode, time, and sensor values are reused across lighting, climate, notifications, media, and camera logic.
            That makes the installation easier to maintain, easier to troubleshoot, and easier to expand with new features later.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Översikt över Home Assistant-systemet
          content: |
            # Översikt över Home Assistant-systemet

            ## Sammanfattning

            Detta är en paketbaserad Home Assistant-uppsättning som sköter vardagskomfort och husautomation på ett strukturerat sätt.
            Den täcker belysning, klimat, närvaro, notiser, media och kamerabaserad uppfattning.

            ## Detaljerad beskrivning

            Systemet är organiserat kring en central konfigurationsingång i configuration.yaml.
            Det verkliga beteendet finns i separata paketfiler som grupperar automatiseringar, hjälpare, skript, sensorer och mallar efter ämne.
            Den här strukturen gör logiken modulär, så att ändringar kan göras i ett område utan att hela husets beteende behöver skrivas om.
            I praktiken byggs systemet upp som ett nätverk av mindre delsystem som alla använder samma delade tillståndsmodell: närvaro, hemmaläge, tid och sensordata återanvänds i belysning, klimat, notiser, media och kameralogik.
            Det gör installationen lättare att underhålla, felsöka och utöka med nya funktioner längre fram.

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

            ## Summary

            The lighting system controls indoor and outdoor lights, seasonal behavior, and scene-based changes across the home.
            It reacts to time of day, presence, and home mode so the lighting feels natural and adaptive.

            ## Detailed description

            The logic is organized around scenes, state transitions, and grouped light entities.
            Files such as packages/lights/inside.yaml, facade.yaml, garden.yaml, hall.yaml, kitchen.yaml, and scenes.yaml define the behavior for morning, day, evening, night, away, and window modes.
            The deeper functionality is that multiple automations work together: time-based triggers decide when a mode should change, presence data decides whether someone is at home, and home-mode conditions decide how the house should behave in each situation.
            In practice, this means the system can apply a general evening rule for the whole house while still allowing room-specific overrides for kitchens, hallways, or outdoor areas.
            The result is a layered lighting model where global rules set the baseline and local logic adds the finer adjustments.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Belysning
          content: |
            # Belysning

            ## Sammanfattning

            Belysningssystemet styr inomhus- och utomhusljus, säsongsbeteende och scenbaserade förändringar i huset.
            Det reagerar på tid på dygnet, närvaro och hemmaläge så att belysningen känns naturlig och anpassningsbar.

            ## Detaljerad beskrivning

            Logiken är organiserad kring scener, tillståndsövergångar och grupperade ljusentiteter.
            Filer som packages/lights/inside.yaml, facade.yaml, garden.yaml, hall.yaml, kitchen.yaml och scenes.yaml definierar beteendet för morgon-, dag-, kväll-, natt-, borta- och fönstermode.
            Den djupare funktionen är att flera automatiseringar arbetar tillsammans: tidsbaserade triggar avgör när ett läge ska ändras, närvarodata avgör om någon är hemma, och hemmalägesvillkor avgör hur huset ska bete sig i varje situation.
            I praktiken innebär det att systemet kan tillämpa en generell kvällsregel för hela huset samtidigt som det fortfarande tillåter rumsspecifika undantag för kök, hallar eller utomhusområden.
            Resultatet är en lagerindelad belysningsmodell där globala regler sätter grunden och lokal logik gör de finare justeringarna.

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

            ## Summary

            This part monitors temperature and humidity in important areas and raises alerts when values become abnormal.
            It is designed to protect sensitive spaces without creating noisy alerts from short temporary fluctuations.

            ## Detailed description

            The logic uses thresholds, delays, and notification routing to decide when an alarm should be raised.
            Files such as packages/alerts/temperature.yaml, packages/climate/friggebod.yaml, packages/climate/garage.yaml, and packages/climate/ute.yaml define the conditions and the response path.
            The deeper design is to distinguish real problems from temporary spikes so the system gives reliable warnings while staying calm and predictable.
            This is usually done by combining sensor values with time-based filters, so a short peak or a brief sensor glitch does not create a false alarm, while a sustained issue still triggers a clear action.
            The same pattern is useful for protecting spaces such as a garage, a shed, or a cold-storage area where the consequences of a missed alert can be significant.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Klimat och larm
          content: |
            # Klimat och larm

            ## Sammanfattning

            Den här delen övervakar temperatur och fuktighet i viktiga områden och skapar larm när värden blir onormala.
            Den är utformad för att skydda känsliga utrymmen utan att skapa brusiga larm från korta tillfälliga fluktuationer.

            ## Detaljerad beskrivning

            Logiken använder trösklar, fördröjningar och notisrouting för att avgöra när ett larm ska utlösas.
            Filer som packages/alerts/temperature.yaml, packages/climate/friggebod.yaml, packages/climate/garage.yaml och packages/climate/ute.yaml definierar villkoren och svarsvägen.
            Den djupare designen är att skilja verkliga problem från tillfälliga toppar så att systemet ger pålitliga varningar samtidigt som det förblir lugnt och förutsägbart.
            Detta görs vanligtvis genom att kombinera sensordata med tidsbaserade filter, så att en kort topp eller en kort sensorstörning inte skapar ett falskt larm, medan ett ihållande problem fortfarande utlöser en tydlig åtgärd.
            Samma mönster är särskilt användbart för att skydda områden som garage, friggebod eller kallförråd, där konsekvenserna av ett missat larm kan bli betydande.

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

            ## Summary

            The ventilation part keeps the indoor environment comfortable by controlling air flow and fan speed.
            It reacts to humidity, temperature, and timing so the system can adjust smoothly rather than just switching on and off.

            ## Detailed description

            Ventilation is implemented as a control loop with thresholds and safety logic.
            Files such as packages/ventilation/ventilation_system.yaml, packages/ventilation/fan.yaml, and packages/sensors/template_sensors/template_ventilation_system.yaml define the fan modes and the conditions that force higher speed.
            The detailed behavior includes mode transitions, timers, and fallback logic so the system avoids unstable or overly aggressive behavior.
            In real use, the ventilation can be driven by humidity and temperature sensors, but it can also be influenced by occupancy, schedules, or manual overrides, which makes it useful both for comfort and for preventing stale air.
            The important point is that the system is not just a simple on/off fan; it is tuned to ramp smoothly and stay predictable under changing conditions.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Ventilation
          content: |
            # Ventilation

            ## Sammanfattning

            Ventilationsdelen håller inomhusmiljön bekväm genom att styra luftflöde och fläkthastighet.
            Den reagerar på fuktighet, temperatur och tid så att systemet kan justeras mjukt istället för att bara slås på och av.

            ## Detaljerad beskrivning

            Ventilation implementeras som en styrloop med trösklar och säkerhetslogik.
            Filer som packages/ventilation/ventilation_system.yaml, packages/ventilation/fan.yaml och packages/sensors/template_sensors/template_ventilation_system.yaml definierar fläktlägen och villkoren som tvingar högre hastighet.
            Det detaljerade beteendet inkluderar lägesövergångar, timers och reservlogik så att systemet undviker instabilt eller för aggressivt beteende.
            I verklig användning kan ventilationen drivas av fukt- och temperatursensorer, men den kan också påverkas av närvaro, scheman eller manuella överskridanden, vilket gör den användbar både för komfort och för att förhindra dålig luft.
            Den viktiga poängen är att systemet inte bara är en enkel på/av-fläkt; det är finjusterat för att öka gradvis och förbli förutsägbart under förändrade förhållanden.

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

            ## Summary

            This part answers whether someone is home, away, or asleep, and that information is reused across the house.
            It acts as a shared state layer for many other automations.

            ## Detailed description

            Presence is treated as a shared state layer that influences many other subsystems.
            Files such as packages/presence/home_away.yaml, packages/presence/person.yaml, and packages/presence/working_at_home.yaml define how the home mode changes and how people are represented.
            The real value is that one consistent presence model keeps the rest of the automations simpler, because they can depend on a stable state instead of guessing from many individual inputs.
            This is especially important because many automations are not driven by a single sensor; they are driven by the combined interpretation of presence, time, and manual choices such as working from home or sleeping.
            In other words, this layer provides a stable “house context” that the rest of the system can trust.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Närvaro och lägen
          content: |
            # Närvaro och lägen

            ## Sammanfattning

            Den här delen svarar på om någon är hemma, borta eller sover, och den informationen används igen över hela huset.
            Den fungerar som ett gemensamt tillståndslager för många andra automatiseringar.

            ## Detaljerad beskrivning

            Närvaro behandlas som ett gemensamt tillståndslager som påverkar många andra delsystem.
            Filer som packages/presence/home_away.yaml, packages/presence/person.yaml och packages/presence/working_at_home.yaml definierar hur hemmaläget ändras och hur personer representeras.
            Det verkliga värdet är att en konsekvent närvaromodell gör resten av automatiseringarna enklare, eftersom de kan lita på ett stabilt tillstånd istället för att gissa från många individuella ingångar.
            Detta är särskilt viktigt eftersom många automatiseringar inte drivs av en enda sensor; de drivs av en kombinerad tolkning av närvaro, tid och manuella val som att arbeta hemifrån eller sova.
            Med andra ord ger detta lager ett stabilt ”huskontext” som resten av systemet kan lita på.

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

            ## Summary

            This part handles ring events, snapshots, and phone notifications so the house can respond to visitors in a useful and visible way.
            It connects a physical trigger to visual and mobile feedback.

            ## Detailed description

            The flow is usually triggered by a hardware event and passed through one or more automations.
            The logic in packages/notifications/doorbell.yaml connects the trigger, the camera snapshot, and the notification action into a reliable event chain.
            The deeper functionality is that the system can decide not only whether to notify, but also how to notify based on current house state, camera availability, and the context of the event.
            In practice, this means the event chain is not just a single action; it can include a light signal, a snapshot, a delay, and a mobile notification, with each step being conditional on the current house state.
            That gives a much more robust experience than simply sending a push message immediately.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Notiser och ringklocka
          content: |
            # Notiser och ringklocka

            ## Sammanfattning

            Den här delen hanterar ringhändelser, ögonblicksbilder och telefonnotiser så att huset kan reagera på besökare på ett användbart och synligt sätt.
            Den kopplar en fysisk utlösare till visuell och mobil feedback.

            ## Detaljerad beskrivning

            Flödet startas vanligtvis av en hårdvaruhändelse och skickas vidare genom en eller flera automatiseringar.
            Logiken i packages/notifications/doorbell.yaml kopplar ihop utlösare, kamerasnapshot och notifieringsåtgärd till en pålitlig händelsekedja.
            Den djupare funktionen är att systemet inte bara kan bestämma om det ska notifiera, utan också hur det ska notifiera baserat på husets aktuella tillstånd, kameratillgänglighet och händelsens sammanhang.
            I praktiken betyder detta att händelsekedjan inte bara är en enda åtgärd; den kan inkludera en ljussignal, en snapshot, en fördröjning och en mobilnotis, där varje steg är villkorat av husets aktuella tillstånd.
            Det ger en mycket mer robust upplevelse än att bara skicka en push-notis direkt.

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

            ## Summary

            This part controls media devices such as TV, radio, Chromecast, and Spotify in a consistent way.
            It makes media feel like part of the house rather than an isolated feature.

            ## Detailed description

            Media behavior is linked to device state, power handling, and activity management.
            Files such as packages/media/harmony_hub.yaml and packages/integrations/media_player.yaml define how media devices behave when the house changes mode or when a user starts a routine.
            The deeper design is to treat media as part of the overall house state so that power, activity, and user intent are handled together.
            This is useful because a media action should not just turn on a device; it should also consider whether the house is in a quiet mode, whether another device is already active, and whether the user is trying to start a focused activity or a general entertainment session.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Media och Harmony
          content: |
            # Media och Harmony

            ## Sammanfattning

            Den här delen styr medieenheter som TV, radio, Chromecast och Spotify på ett konsekvent sätt.
            Den gör media till en del av huset snarare än en isolerad funktion.

            ## Detaljerad beskrivning

            Mediebeteendet är kopplat till enhetsstatus, strömhantering och aktivitetsstyrning.
            Filer som packages/media/harmony_hub.yaml och packages/integrations/media_player.yaml definierar hur medieenheter beter sig när huset ändrar läge eller när en användare startar en rutin.
            Den djupare designen är att behandla media som en del av husets övergripande tillstånd så att ström, aktivitet och användaravsikt hanteras tillsammans.
            Detta är användbart eftersom en medieåtgärd inte bara ska slå på en enhet; den ska också ta hänsyn till om huset befinner sig i ett tyst läge, om en annan enhet redan är aktiv, och om användaren försöker starta en fokuserad aktivitet eller en generell underhållningssession.

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

            ## Summary

            Frigate watches the cameras, notices movement, and turns raw video into useful event information for Home Assistant.
            It can react to people, animals, faces, and other events in a structured way.

            ## Detailed description

            Frigate acts as the camera analysis layer that feeds Home Assistant with event-based information.
            The logic in packages/frigate/frigate_person_detected.yaml, frigate_animal_detected.yaml, frigate_intruder_alarm.yaml, frigate_face_detection.yaml, frigate_sensors.yaml, and frigate_media.yaml turns those detections into automations, summary sensors, and cleanup routines.
            The deeper design is to separate useful signals from noise so the system can react quickly without becoming noisy, overly chatty, or storage-heavy.
            In practical terms, this means the system can record and expose only meaningful events such as a person seen near the entrance or an animal detected in the yard, while keeping the overall event stream concise and useful for automations and dashboards.
            The same pipeline can also feed notifications, snapshots, and longer-term summaries so that camera data becomes part of the house intelligence instead of just raw video.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Frigate-dokumentation
          content: |
            # Frigate

            ## Sammanfattning

            Frigate bevakar kamerorna, märker rörelse och förvandlar rå video till användbar händelseinformation för Home Assistant.
            Den kan reagera på människor, djur, ansikten och andra händelser på ett strukturerat sätt.

            ## Detaljerad beskrivning

            Frigate fungerar som lagret för kameraanalys som matar Home Assistant med händelsebaserad information.
            Logiken i packages/frigate/frigate_person_detected.yaml, frigate_animal_detected.yaml, frigate_intruder_alarm.yaml, frigate_face_detection.yaml, frigate_sensors.yaml och frigate_media.yaml omvandlar dessa detektioner till automatiseringar, sammanfattningssensorer och rensningsrutiner.
            Den djupare designen är att skilja användbara signaler från brus så att systemet kan reagera snabbt utan att bli störigt, överdrivet pratigt eller lagringsintensivt.
            I praktiken innebär det att systemet kan spela in och exponera endast meningsfulla händelser, till exempel en person som ses vid ingången eller ett djur som upptäcks på gården, samtidigt som händelseflödet hålls kortfattat och användbart för automatiseringar och dashboards.
            Samma pipeline kan också mata notiser, snapshots och långsiktiga sammanfattningar så att kameradata blir en del av husets intelligens istället för bara rå video.
'''

Path(r'c:/Users/micke/Documents/GitHub/Home-AssistantConfig/documentation.ui').write_text(content, encoding='utf-8')
