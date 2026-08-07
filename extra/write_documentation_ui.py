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

            ## Scope of the system

            This documentation covers the complete house automation stack, not only one feature area.
            The same control model is reused across lighting, ventilation, presence, notifications, media, and camera-based reactions so the house behaves like a coordinated system rather than a collection of unrelated automations.

            ## Architecture

            The system is organized as a package-based Home Assistant deployment where each domain is implemented in its own package and wired together through shared entities such as home status, timers, helpers, and trigger sensors.
            The main entrypoint is configuration.yaml, while the practical behavior lives in packages/ and is then referenced by automations, scripts, and UI views.

            ## Control model

            The house behaves like a layered state machine.
            Presence and home state are resolved first, then time and sensor values are evaluated, and finally domain-specific automations decide which actions to execute.
            That means the same condition, for example “someone is home” or “bathroom humidity is high”, can influence lighting, ventilation, notifications, media, and camera-based reactions at the same time.

            ## Runtime flow

            1. Person entities and device trackers produce presence information.
            2. The shared home-status entity becomes the single source of truth for the rest of the system.
            3. Domain automations consume that state together with lux, temperature, humidity, and time-based inputs.
            4. Scripts execute the real actions so the automations stay small and the behavior is easier to reason about.

            ## Main subsystems

            - Lighting: scenes, facade logic, indoor and outdoor groups, and seasonal behavior.
            - Ventilation: humidity/temperature-driven fan logic with forced mode, timers, and safety guards.
            - Presence: person tracking, home/away logic, and sleep/wake handling.
            - Notifications, media, and Frigate: event-driven reactions that build on the same shared state model.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Översikt över Home Assistant-systemet
          content: |
            # Översikt över Home Assistant-systemet

            ## Omfattning av systemet

            Den här dokumentationen täcker hela husautomationsstacken, inte bara ett enskilt funktionsområde.
            Samma styrmodell används över belysning, ventilation, närvaro, notiser, media och kamerabaserade reaktioner, så huset beter sig som ett samordnat system snarare än som en samling oberoende automatiseringar.

            ## Arkitektur

            Systemet är uppbyggt som en paketbaserad Home Assistant-installation där varje domän implementeras i sitt eget paket och kopplas samman via delade entiteter som hemmaläge, timers, hjälpare och triggningssensorer.
            Huvudingången är configuration.yaml, medan det verkliga beteendet finns i packages/ och sedan anropas genom automatiseringar, skript och UI-vyer.

            ## Styrmodell

            Huset fungerar som en lagerindelad tillståndsmaskin.
            Närvaro och hemmaläge löses först, därefter utvärderas tid och sensordata, och slutligen väljer domänspecifika automatiseringar vilka åtgärder som ska utföras.
            Det innebär att samma villkor, till exempel “någon är hemma” eller “luftfuktigheten i badrummet är hög”, kan påverka belysning, ventilation, notiser, media och kamerabaserade reaktioner samtidigt.

            ## Körningsflöde

            1. Personentiteter och device trackers skapar närvaroinformation.
            2. Den gemensamma hemmalägesentiteten blir en enda källa till sanning för resten av systemet.
            3. Domänautomatiseringar använder detta tillstånd tillsammans med lux, temperatur, fuktighet och tidsbaserade indata.
            4. Skript utför de faktiska åtgärderna så att automatiseringarna förblir små och lättare att förstå.

            ## Huvuddelar

            - Belysning: scener, fasadlogik, inomhus- och utomhusgrupper samt säsongsbeteende.
            - Ventilation: fukt-/temperaturstyrd fläktlogik med forcerat läge, timers och säkerhetsgrindar.
            - Närvaro: personspårning, hem/borta-logik och sömn/vaken-hantering.
            - Notiser, media och Frigate: händelsedrivna reaktioner som bygger på samma delade tillståndsmodell.

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

            ## Control architecture

            The lighting system is one of the core domains in the house automation stack.
            It is implemented as a set of package-based automations and scripts that all consume the same shared house context: home status, time, lux, presence, and manual overrides.
            In practice this means the lighting layer behaves like a state-driven control system rather than a simple timer-based switchboard.

            ## How the lighting flow works

            A typical lighting decision follows this sequence:

            1. The presence layer resolves whether the house is occupied, away, or in a sleep-like state.
            2. The time and lux layer decides which lighting mode is currently appropriate.
            3. The lighting package selects the right scene or facade mode.
            4. Scripts apply the actual light changes with brightness, transition timing, and room-specific behavior.

            This is why the system can keep lighting consistent across indoor and outdoor areas even when the house changes state rapidly.

            ## Main lighting packages

            The implementation is split into several packages:

            - inside.yaml for general indoor behavior
            - facade.yaml for the exterior state machine and facade light modes
            - garden.yaml and hall.yaml for room-specific lighting logic
            - kitchen.yaml for kitchen-specific behavior
            - scenes.yaml for reusable scene definitions and shared light states

            ## Facade lighting in detail

            The facade subsystem uses an explicit state machine with the entity input_select.facade_lights and the helper input_boolean.lights_auto_fasad.
            The resolver evaluates three kinds of inputs before it sets a new mode:

            - lux level from the outdoor light sensor
            - home status from input_select.home_status
            - camera-based occupancy from the exterior camera binary sensors

            The decision order is intentionally simple and deterministic:

            1. If the outdoor light is bright enough, the system selects the Off state.
            2. If a person is detected and the light is not already bright, it switches to Person detected, which is the maximum-brightness mode.
            3. If the house is in Sleep mode and the environment is dark enough, it uses the Night mode.
            4. If the environment is dark and none of the above conditions apply, it selects Morning/Evening mode.
            5. If none of those conditions apply, the current state is retained.

            This makes the facade lighting behave as a controlled fallback system rather than a purely time-based switch. The reason it escalates to maximum brightness is visibility and safety: a detected person near the entrance should always be visible even if the normal evening mode would be too dim.

            ## Script behavior

            Each facade mode is executed by a dedicated script:

            - Off turns the facade fixtures off with a short transition.
            - Morning/Evening turns the lights on at moderate brightness.
            - Night uses a reduced brightness profile for the more subtle nighttime look.
            - Person detected uses the highest brightness values, which is why it is the most visible mode.

            The scripts are intentionally restart-safe so that rapid state changes do not leave the lights half-updated.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Belysning
          content: |
            # Belysning

            ## Styrarkitektur

            Belysningssystemet är ett av de centrala delarna i husautomationsstacken.
            Det implementeras som en uppsättning paketbaserade automatiseringar och skript som alla konsumerar samma gemensamma huskontext: hemmaläge, tid, lux, närvaro och manuella åsidosättningar.
            I praktiken betyder det att ljuslagret beter sig som ett tillståndsstyrt styrsystem snarare än en enkel timerbaserad brytare.

            ## Hur ljusflödet fungerar

            Ett typiskt ljusbeslut följer denna sekvens:

            1. Närvarolagret löser om huset är upptaget, borta eller i ett sovliknande tillstånd.
            2. Tid- och luxlagret avgör vilket ljusläge som är aktuellt.
            3. Belysningspaketet väljer rätt scen eller fasadläge.
            4. Skript tillämpar de faktiska ljusändringarna med styrka, övergångstid och rumspecifikt beteende.

            Det är därför systemet kan hålla belysningen konsekvent över inomhus- och utomhusområden även när huset ändrar tillstånd snabbt.

            ## Huvudpaket för belysning

            Implementationen är uppdelad i flera paket:

            - inside.yaml för allmän inomhusbelysning
            - facade.yaml för det yttre tillstånds- och fasadljusläget
            - garden.yaml och hall.yaml för rumspecifik ljuslogik
            - kitchen.yaml för kökspecifik beteende
            - scenes.yaml för återanvändbara scener och delade ljuslägen

            ## Fasadbelysning i detalj

            Fasadsubsystemet använder en explicit tillståndsmaskin med entiteten input_select.facade_lights och hjälpen input_boolean.lights_auto_fasad.
            Resolvern utvärderar tre typer av indata innan den sätter ett nytt läge:

            - lux-nivå från utomhusljussensorn
            - hemmaläge från input_select.home_status
            - kamerabaserad närvaro från de externa kamerornas binära sensorer

            Beslutsordningen är avsiktligt enkel och deterministisk:

            1. Om det är tillräckligt ljust ute väljs avstängt läge.
            2. Om en person upptäcks och ljuset inte redan är starkt väljs läget Person upptäckt, vilket är maxljusläget.
            3. Om huset är i sovläge och miljön är tillräckligt mörk används nattläge.
            4. Om miljön är mörk och inget av ovanstående gäller väljs morgon-/kvällsläge.
            5. Om inget av dessa villkor gäller behålls det aktuella läget.

            Det gör att fasadbelysningen beter sig som ett kontrollerat fallback-system istället för en ren tidsbaserad brytare. Anledningen till att den höjs till maxljus är synlighet och säkerhet: en upptäckt person nära ingången ska alltid vara synlig även om normal kvällsinställning skulle vara för svag.

            ## Skriptbeteende

            Varje fasadläge exekveras av ett dedikerat skript:

            - Av stänger fasadarmaturerna av med en kort övergång.
            - Morgon/Kväll slår på ljuset med måttlig styrka.
            - Natt använder en reducerad ljusstyrka för ett mer subtilt nattutseende.
            - Person upptäckt använder de högsta ljusvärdena, vilket är varför det är det mest synliga läget.

            Skripten är avsiktligt säkra vid omstart så att snabba tillståndsändringar inte lämnar ljuset halvuppdaterat.

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

            ## Control philosophy

            The ventilation system is not a simple on/off switch. It is a closed-loop control system that uses humidity, temperature, timers, and safety conditions to decide whether the fan should run in normal mode or be forced into a higher-speed state.

            ## Fan states and transitions

            The system has three practical operating concepts:

            - Normal mode: the fan operates under the standard control logic and only changes state when the measured values cross configured thresholds.
            - Forced mode: the system actively drives the fan into a higher-speed state when humidity or temperature conditions indicate that the airflow needs to increase immediately.
            - Off/available recovery: if the actuator becomes unavailable, the automation can recover to normal mode when the device is available again and no forced timer is active.

            ## How forced mode is triggered

            Forced mode is activated when the system detects that bathroom humidity is high enough, or when temperature conditions indicate that the ventilation should run more aggressively.
            The logic uses configurable thresholds and compares current values against them so that short spikes do not immediately cause the fan to stay in forced mode forever.

            ## Why timers exist

            Two timers are central to the design:

            - A stability timer prevents rapid oscillation by requiring the humidity condition to remain valid for a period before a new state transition is accepted.
            - A maximum runtime timer prevents forced mode from continuing indefinitely. After the configured maximum runtime, the system returns to the normal control path.

            This design keeps the ventilation system predictable and avoids unstable behavior caused by a single transient condition.

            ## Practical behavior

            In normal operation the fan can be considered to be “idle” with the standard control loop. When the humidity or temperature signal becomes severe enough, the system enters forced mode and stays there until the conditions normalize or the timer expires. The actuator is treated as the physical output of the control loop, while the helper values and timers are the control layer.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Ventilation
          content: |
            # Ventilation

            ## Styrfilosofi

            Ventilationssystemet är inte en enkel på/av-brytare. Det är ett slutet styrsystem som använder fuktighet, temperatur, timers och säkerhetsvillkor för att avgöra om fläkten ska köra i normalt läge eller tvingas till ett högre hastighetsläge.

            ## Fläktlägen och övergångar

            Systemet har tre praktiska driftskoncept:

            - Normalt läge: fläkten arbetar under standardstyrlogiken och byter endast tillstånd när uppmätta värden passerar konfigurerade trösklar.
            - Forcerat läge: systemet driver aktivt fläkten till ett högre hastighetsläge när fuktighet eller temperatur indikerar att luftflödet behöver öka omedelbart.
            - Av/återhämtning: om ställdonet blir otillgängligt kan automationen återgå till normalt läge när enheten är tillgänglig igen och inget forceringstimer är aktivt.

            ## Hur forcerat läge aktiveras

            Forcerat läge aktiveras när systemet upptäcker att badrumsfuktigheten är tillräckligt hög, eller när temperaturförhållanden indikerar att ventilationen bör köras aggressivare.
            Logiken använder konfigurerbara trösklar och jämför aktuella värden med dem så att korta toppar inte gör att fläkten blir förcerad för alltid.

            ## Varför timers finns

            Två timers är centrala för designen:

            - En stabilitetstimer förhindrar snabb oscillation genom att kräva att fuktighetsvillkoret förblir giltigt under en viss period innan en ny tillståndsövergång accepteras.
            - En maxtidstimer förhindrar att forcerat läge fortsätter oändligt. När den konfigurerade maxtiden passerats går systemet tillbaka till den normala styrvägen.

            Den här designen gör ventilationssystemet förutsägbart och undviker instabilt beteende orsakad av en enda tillfällig händelse.

            ## Praktiskt beteende

            I normal drift kan fläkten betraktas som “vilande” under standardstyrloopen. När fuktighets- eller temperaturvärdet blir tillräckligt allvarligt går systemet in i forcerat läge och stannar där tills villkoren normaliseras eller timern löper ut. Ställdonet behandlas som det fysiska utfallet av styrloopen, medan hjälpvärdena och timerna är styrlagret.

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

            ## Role of the home-status state

            The home-status entity is the house-level abstraction that other subsystems consume.
            It is the single source of truth that the rest of the automation network uses to decide whether to behave as if the house is occupied, empty, or in a sleep-like state.

            ## How the state changes

            The presence automation evaluates two main input groups:

            - person entities and device trackers, which determine whether anyone is effectively at home
            - the kitchen motion sensor, which can wake the house from sleep mode during daytime

            The transition logic is simple:

            1. If at least one person or tracked device is home, the target state becomes Hemma.
            2. If nobody is home, the target state becomes Borta.
            3. If the current state is Sover and motion occurs during daytime, the system can switch back to Hemma.

            In other words, Hemma and Borta are the primary occupancy states, while Sover is a special state that acts as a sleep override and can be used to suppress normal daytime behavior until a wake event occurs.

            ## Why this matters

            This layer is important because it keeps lighting, race conditions, media behavior, and other automations consistent.
            Instead of each subsystem trying to infer occupancy from its own sensors, they all rely on the same shared state and therefore behave as part of a single coordinated system.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Närvaro och lägen
          content: |
            # Närvaro och lägen

            ## Hemmalägets roll

            Hemmalägesentiteten är den husnivåabstraktion som andra delsystem konsumerar.
            Det är den enda källan till sanning som resten av automationsnätverket använder för att avgöra om huset ska bete sig som om det är upptaget, tomt eller i ett sovliknande tillstånd.

            ## Hur tillståndet ändras

            Närvaroautomationen utvärderar två huvudsakliga ingångsgrupper:

            - personentiteter och device trackers, som avgör om någon faktiskt är hemma
            - köksrörelsesensorn, som kan väcka huset från sovläge under dagtid

            Övergångslogiken är enkel:

            1. Om minst en person eller spårad enhet är hemma blir måltillståndet Hemma.
            2. Om ingen är hemma blir måltillståndet Borta.
            3. Om det aktuella tillståndet är Sover och rörelse inträffar under dagtid kan systemet gå tillbaka till Hemma.

            Med andra ord är Hemma och Borta de primära närvarotillstånden, medan Sover är ett specialtillstånd som fungerar som en sömnöverskridning och kan användas för att dämpa normalt dagligt beteende tills ett väckningshändelse sker.

            ## Varför detta är viktigt

            Detta lager är viktigt eftersom det håller belysning, media, krockningar mellan automationsflöden och andra delsystem konsekventa.
            Istället för att varje subsystem försöker dra slutsatser om närvaro från egna sensorer, så litar de alla på samma delade tillstånd och agerar därför som en del av ett samordnat system.

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
