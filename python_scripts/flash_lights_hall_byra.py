entity_id = 'light.hall_byra'
light = hass.states.get(entity_id)

original_state = light.state
if original_state is 'on':
    brightness = light.attributes.get('brightness') or 0

if original_state is 'off':
    hass.services.call('light', 'turn_on', {'entity_id': entity_id, 'brightness': '255'})
    time.sleep(1)

hass.services.call('light', 'turn_off', {'entity_id': entity_id})
time.sleep(2)
hass.services.call('light', 'turn_on', {'entity_id': entity_id, 'brightness': '255'})
time.sleep(1)

hass.services.call('light', 'turn_off', {'entity_id': entity_id})

if original_state is 'on':
    time.sleep(2)
    hass.services.call('light', 'turn_on', {'entity_id': entity_id, 'brightness': brightness})
