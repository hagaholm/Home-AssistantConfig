"""
Utility sensor: counts how many lights are currently on.
Sets sensor.lights_on with a simple integer value.
Safe to run as a Home Assistant python_script.
"""

on = 0
for entity_id in hass.states.entity_ids('light'):
    state = hass.states.get(entity_id)
    if state.state == 'on':
        on = on + 1

hass.states.set('sensor.lights_on', on, {
    'unit_of_measurement': 'lights',
    'friendly_name': 'Lights On'
})