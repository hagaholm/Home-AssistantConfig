from pathlib import Path

content = r'''title: Documentation
views:
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

            Frigate is the “camera brain” in this setup.
            It watches the video from your cameras and tries to understand what it sees.

            ## Easy version

            In simple words:
            - it notices movement
            - it tries to identify what it is
            - it tells Home Assistant what happened
            - Home Assistant can then decide what to do

            This is useful when you want the house to react to people, animals, or faces.

            ## How it works

            1. A camera sees movement.
            2. Frigate looks at the image.
            3. It tries to decide if it is a person, animal, or face.
            4. It sends that information to Home Assistant.
            5. Home Assistant checks the rules and decides what should happen.

            ## Person detection

            ### Easy version
            This part is for when Frigate sees a person.
            It can send you a warning and make the house react.

            ### More advanced version
            The person automations are triggered by the person activity summary sensor.
            They check whether you are asleep, away, or home and then decide whether to send an immediate notification or wait a few minutes.
            There is also a blinking-light automation for extra attention.

            ## Animal detection

            ### Easy version
            This part is for animals such as cats, dogs, or other wildlife.
            It helps the house react when something animal-like appears.

            ### More advanced version
            The animal automation listens to the animal activity summary sensor.
            If the detection is still active and the conditions are right, it turns on lights.
            If the detection disappears, it waits and then turns the lights off again.
            There is also a safety fallback that turns off the deck light after 10 minutes.

            ## Intruder alarm logic

            ### Easy version
            This is the stronger security part.
            If a person is detected in a sensitive zone, the house can make a stronger response.

            ### More advanced version
            The intruder alarm automation listens to MQTT Frigate event messages.
            It only acts if the event is new, comes from the right camera, is labeled as person, happens in the backyard zone, and the home mode is right.
            Then it turns on the siren briefly and sends a notification with event details.

            ## Face detection

            This part collects face-related information from Frigate and creates sensors for the face name, camera, score, and timestamp.

            ## Summary sensors and helpers

            These helpers make the system easier to use by turning many raw values into simple yes/no sensors.
            That lets the automations react to a simple signal instead of checking everything one by one.

            ## Media cleanup

            This part keeps Frigate storage from filling up by cleaning old clips and recordings.

            ## Main files

            - packages/frigate/frigate_person_detected.yaml
            - packages/frigate/frigate_animal_detected.yaml
            - packages/frigate/frigate_intruder_alarm.yaml
            - packages/frigate/frigate_face_detection.yaml
            - packages/frigate/frigate_sensors.yaml
            - packages/frigate/frigate_media.yaml

            ## Final summary

            Frigate watches the cameras, understands what it sees, and lets Home Assistant react in a smart way.

      - type: conditional
        conditions:
          - entity: input_boolean.documentation_language_swedish
            state: "on"
        card:
          type: markdown
          title: Frigate-dokumentation
          content: |
            # Frigate

            Frigate är “kamerahjärnan” i den här uppsättningen.
            Den följer videon från dina kameror och försöker förstå vad den ser.

            ## Enkel version

            I enkla ord:
            - den märker rörelse
            - den försöker identifiera vad det är
            - den berättar för Home Assistant vad som hände
            - Home Assistant kan sedan bestämma vad som ska göras

            Det här är användbart när du vill att huset ska reagera på människor, djur eller ansikten.

            ## Hur det fungerar

            1. En kamera ser rörelse.
            2. Frigate tittar på bilden.
            3. Den försöker avgöra om det är en person, ett djur eller ett ansikte.
            4. Den skickar information till Home Assistant.
            5. Home Assistant kontrollerar reglerna och bestämmer vad som ska hända.

            ## Persondetektering

            ### Enkel version
            Den här delen gäller när Frigate ser en person.
            Den kan skicka en varning och få huset att reagera.

            ### Mer avancerad version
            Personautomatiseringarna startar från en sammanfattningssensor för personaktivitet.
            De kontrollerar om du sover, är borta eller hemma och bestämmer sedan om det ska skickas en omedelbar varning eller vänta några minuter.
            Det finns också en blinkande-ljussautomation för extra uppmärksamhet.

            ## Djurdetektering

            ### Enkel version
            Den här delen gäller djur som katter, hundar eller annat vilt.
            Den hjälper huset att reagera när något djurlikt dyker upp.

            ### Mer avancerad version
            Djurautomationen lyssnar på en sammanfattningssensor för djuraktivitet.
            Om detekteringen fortfarande är aktiv och villkoren är rätt, tänds lampor.
            Om detekteringen försvinner väntar systemet en stund och stänger sedan av lamporna igen.
            Det finns också en säkerhetsåtgärd som stänger av trädäcksljuset efter 10 minuter.

            ## Intruder alarm logic

            ### Enkel version
            Det här är den starkare säkerhetsdelen.
            Om en person upptäcks i ett känsligt område kan huset göra en starkare reaktion.

            ### Mer avancerad version
            Intruder-alarmautomationen lyssnar på MQTT-meddelanden från Frigate.
            Den agerar bara om händelsen är ny, kommer från rätt kamera, är märkt som person, sker i bakgårdszonen och hemmets läge passar.
            Därefter tänds sirenen kort och en notis skickas med detaljer om händelsen.

            ## Ansiktsdetektering

            Den här delen samlar in ansiktsrelaterad information från Frigate och skapar sensorer för namn, kamera, poäng och tidsstämpel.

            ## Sammanfattningssensorer och hjälpare

            Dessa hjälpare gör systemet enklare att använda genom att omvandla många råa värden till enkla ja/nej-sensorer.
            Det gör att automatiseringarna kan reagera på ett enkelt signal istället för att kontrollera allt ett i taget.

            ## Media-rensning

            Den här delen håller Frigate-lagringen från att bli full genom att rensa gamla klipp och inspelningar.

            ## Huvudfiler

            - packages/frigate/frigate_person_detected.yaml
            - packages/frigate/frigate_animal_detected.yaml
            - packages/frigate/frigate_intruder_alarm.yaml
            - packages/frigate/frigate_face_detection.yaml
            - packages/frigate/frigate_sensors.yaml
            - packages/frigate/frigate_media.yaml

            ## Sammanfattning

            Frigate följer kamerorna, förstår vad den ser och låter Home Assistant reagera på ett smart sätt.
'''

Path(r'c:/Users/micke/Documents/GitHub/Home-AssistantConfig/documentation.ui').write_text(content, encoding='utf-8')
