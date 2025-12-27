import time

entity_id = 'light.kok_lilla_fonstret'
light = hass.states.get(entity_id)

if not light:
    return

original_state = light.state

if original_state == 'off':
    hass.services.call('light', 'turn_on', {'entity_id': entity_id})
    time.sleep(1)
    hass.services.call('light', 'turn_off', {'entity_id': entity_id})
    time.sleep(1)
    hass.services.call('light', 'turn_on', {'entity_id': entity_id})
    time.sleep(1)
    hass.services.call('light', 'turn_off', {'entity_id': entity_id})

if original_state == 'on':
    hass.services.call('light', 'turn_off', {'entity_id': entity_id})
    time.sleep(1)
    hass.services.call('light', 'turn_on', {'entity_id': entity_id})
    time.sleep(1)
    hass.services.call('light', 'turn_off', {'entity_id': entity_id})
    time.sleep(1)
    hass.services.call('light', 'turn_on', {'entity_id': entity_id})