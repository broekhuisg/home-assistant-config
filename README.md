# My Home Assistant Configuration


## Home Assistant
[Home Assistant][hassurl]
My config for Home Assistant

## Based on Frenck's config and Patatman's config
See: [Frencks Github][frencksgithub]
See: [Patatmans Github][patatmangithub]

[frencksgithub]: https://github.com/frenck/home-assistant-config
[patatmangithub]: https://github.com/patatman/patatman-homeassistant-config
[hassurl]: https://www.home-assistant.io/

## Hardware
TODO: Fill in hardware

## Software
TODO: Fill in software

#### Entity file naming:
`<entity_type>/<platform>.<name>.yaml` e.g. `light/mqtt.color_light.yaml`

#### Customization file naming:
`<entity_name>.yaml` e.g. `binary_sensor.motion_sensor_4.yaml`

#### Automation naming:
If room specific, lighting for example.
`<room>_<type>_<trigger>.yaml` e.g. `kitchen_light_motion-on.yaml` or `livingroom_light_button-1.yaml`

If it's a virtual automation, like alarm:
`<type>_<trigger>_<action>.yaml` e.g. `alarm_pending_notification.yaml` or `telegram_windows-open_notification.yaml`