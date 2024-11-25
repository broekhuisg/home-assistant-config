# Home Assistant Configuration
![GitHub Last Commit][last-commit-shield]
![GitHub Activity][commits-shield]
![HA Version][ha-version-shield]

## Home Assistant
[Home Assistant][hassurl]
My config for Home Assistant

## Based on Frenck's config and Patatman's config
See: [Frencks Github][frencksgithub]
See: [Patatmans Github][patatmangithub]

[frencksgithub]: https://github.com/frenck/home-assistant-config
[patatmangithub]: https://github.com/patatman/patatman-homeassistant-config
[hassurl]: https://www.home-assistant.io/

#### Entity file naming:
`<entity_type>/<platform>.<name>.yaml` e.g. `light/mqtt.color_light.yaml`

#### Customization file naming:
`<entity_name>.yaml` e.g. `binary_sensor.motion_sensor_4.yaml`

#### Automation naming:
If room specific, lighting for example.
`<room>/<type>_<trigger>.yaml` e.g. `kitchen/light_motion-on.yaml` or `livingroom/light_button-1.yaml`

If it's a virtual automation, like alarm:
`<type>_<trigger>_<action>.yaml` e.g. `alarm_pending_notification.yaml` or `telegram_windows-open_notification.yaml`

[last-commit-shield]: https://img.shields.io/github/last-commit/broekhuisg/home-assistant-config.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/broekhuisg/home-assistant-config.svg
[ha-version-shield]: https://img.shields.io/badge/Home%20Assistant-2024.11.3-blue.svg

<img align="right" src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Home_Assistant_Logo.svg/519px-Home_Assistant_Logo.svg.png?raw=true" height="160">
