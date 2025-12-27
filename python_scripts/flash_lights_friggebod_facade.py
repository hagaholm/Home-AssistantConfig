hass.services.call('light', 'turn_off', {'entity_id': entity_id})
hass.services.call('light', 'turn_off', {'entity_id': entity_id})
import time

entity_id = 'light.friggebod_fasad'
light = hass.states.get(entity_id)

# Exit safely if entity is missing
if not light:
    return

original_state = light.state
brightness = (light.attributes.get('brightness') or 0) if original_state == 'on' else None

if original_state == 'off':
    hass.services.call('light', 'turn_on', {'entity_id': entity_id})
    time.sleep(1)

hass.services.call('light', 'turn_off', {'entity_id': entity_id})
time.sleep(1)
hass.services.call('light', 'turn_on', {'entity_id': entity_id})
time.sleep(1)

hass.services.call('light', 'turn_off', {'entity_id': entity_id})

if original_state == 'on':
    time.sleep(1)
    hass.services.call('light', 'turn_on', {
        'entity_id': entity_id,
        'brightness': brightness,
    })
