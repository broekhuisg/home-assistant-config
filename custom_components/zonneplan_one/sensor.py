"""Zonneplan Sensor"""
from typing import Optional, Any
from voluptuous.validators import Number
from datetime import datetime
from pytz import timezone


from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
import logging
from homeassistant.core import ( 
    callback, 
    HomeAssistant
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)

import homeassistant.util.dt as dt_util

from .coordinator import ZonneplanUpdateCoordinator
from .const import (
    DOMAIN,
    P1_INSTALL,
    PV_INSTALL,
    NONE_IS_ZERO,
    NONE_USE_PREVIOUS,
    SENSOR_TYPES,
    SUMMARY,
    CHARGE_POINT,
    BATTERY,
    ZonneplanSensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    coordinator: ZonneplanUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]

    entities = []
    for uuid, connection in coordinator.connections.items():
        pv_installations = coordinator.getConnectionValue(uuid, PV_INSTALL)
        p1_installations = coordinator.getConnectionValue(uuid, P1_INSTALL)
        summary = coordinator.getConnectionValue(uuid, SUMMARY)
        charge_point = coordinator.getConnectionValue(uuid, CHARGE_POINT)
        battery = coordinator.getConnectionValue(uuid, BATTERY)

        _LOGGER.debug("Setup sensors for connnection %s", uuid)

        if summary:
            for sensor_key in SENSOR_TYPES[SUMMARY]:
                entities.append(
                    ZonneplanSensor(
                        uuid,
                        sensor_key,
                        coordinator,
                        None,
                        SENSOR_TYPES[SUMMARY][sensor_key],
                    )
                )

        if pv_installations:
            for sensor_key in SENSOR_TYPES[PV_INSTALL]["totals"]:
                entities.append(
                    ZonneplanPvSensor(
                        uuid,
                        sensor_key,
                        coordinator,
                        -1,
                        SENSOR_TYPES[PV_INSTALL]["totals"][sensor_key],
                    )
                )
            for install_index in range(len(pv_installations)):
                for sensor_key in SENSOR_TYPES[PV_INSTALL]["install"]:
                    entities.append(
                        ZonneplanPvSensor(
                            uuid,
                            sensor_key,
                            coordinator,
                            install_index,
                            SENSOR_TYPES[PV_INSTALL]["install"][sensor_key],
                        )
                    )

        if p1_installations:
            for sensor_key in SENSOR_TYPES[P1_INSTALL]["totals"]:
                entities.append(
                    ZonneplanP1Sensor(
                        uuid,
                        sensor_key,
                        coordinator,
                        -1,
                        SENSOR_TYPES[P1_INSTALL]["totals"][sensor_key],
                    )
                )
            for install_index in range(len(p1_installations)):
                for sensor_key in SENSOR_TYPES[P1_INSTALL]["install"]:
                    entities.append(
                        ZonneplanP1Sensor(
                            uuid,
                            sensor_key,
                            coordinator,
                            install_index,
                            SENSOR_TYPES[P1_INSTALL]["install"][sensor_key],
                        )
                    )

        if charge_point:
            for install_index in range(len(charge_point)):
                for sensor_key in SENSOR_TYPES[CHARGE_POINT]:
                    entities.append(
                        ZonneplanChargePointSensor(
                            uuid,
                            sensor_key,
                            coordinator,
                            install_index,
                            SENSOR_TYPES[CHARGE_POINT][sensor_key],
                        )
                    )

        if battery:
            for install_index in range(len(battery)):
                for sensor_key in SENSOR_TYPES[BATTERY]:
                    entities.append(
                        ZonneplanBatterySensor(
                            uuid,
                            sensor_key,
                            coordinator,
                            install_index,
                            SENSOR_TYPES[BATTERY][sensor_key],
                        )
                    )

    async_add_entities(entities)


class ZonneplanSensor(CoordinatorEntity, RestoreEntity, SensorEntity):
    """Abstract class for a zonneplan sensor."""

    coordinator: ZonneplanUpdateCoordinator

    def __init__(
        self,
        connection_uuid,
        sensor_key: str,
        coordinator: ZonneplanUpdateCoordinator,
        install_index: Number,
        description: ZonneplanSensorEntityDescription,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._connection_uuid = connection_uuid
        self._sensor_key = sensor_key
        self._install_index = install_index
        self.entity_description = description

        self._attr_native_value = self._value_from_coordinator()

    @property
    def install_uuid(self) -> str:
        """Return install ID."""
        return self._connection_uuid

    @property
    def unique_id(self) -> Optional[str]:
        """Return a unique ID."""
        return self.install_uuid + "_" + self._sensor_key

    @property
    def device_info(self):
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._connection_uuid)},
            "manufacturer": "Zonneplan",
            "name": "Zonneplan",
        }

    @property
    def last_reset(self) -> datetime | None:

        if not self.entity_description.last_reset_key:
            return None

        value = self.coordinator.getConnectionValue(
            self._connection_uuid,
            self.entity_description.last_reset_key.format(install_index=self._install_index),
        )

        if value:
            value = dt_util.parse_datetime(value)

        _LOGGER.debug(f"Last update {self.name}: {value}")

        return value

    @callback
    def _handle_coordinator_update(self) -> None:
        value = self._value_from_coordinator()

        if (
            value is None
            and self.entity_description.none_value_behaviour == NONE_USE_PREVIOUS
        ):
            return

        if self.skip_update_based_on_daily_update_hour():
            _LOGGER.info(
                f"Skip update {self.name} until {self.entity_description.daily_update_hour}h"
            )
            return

        _LOGGER.debug(f"Update {self.name}: {value}")

        self._attr_native_value = value
        self.async_write_ha_state()

    def skip_update_based_on_daily_update_hour(self) -> bool:
        if self.entity_description.daily_update_hour is None:
            return False

        # No state? then we update
        if not (state := self.hass.states.get(self.entity_id)):
            return False

        # No last update value? then we update
        if not state.last_updated:
            return False

        update_today = dt_util.now().replace(
            hour=self.entity_description.daily_update_hour,
            minute=0,
            second=0,
            microsecond=0,
        )

        # Is it time already to update the value today? No then we skip
        if update_today > dt_util.now():
            _LOGGER.debug(
                f"Skipped update {self.name}: {update_today} (update today) > {dt_util.now()} (now)"
            )
            return True

        # Already updated today after daily_update_hour? Then skip
        if dt_util.as_local(state.last_updated) >= update_today:
            _LOGGER.debug(
                f"Skipped update {self.name}: {dt_util.as_local(state.last_updated)} (last update) >= {update_today} (update today)"
            )
            return True

        return False

    @property
    def extra_state_attributes(self):
        if not self.entity_description.attributes:
            return

        attrs = {}
        for attribute in self.entity_description.attributes:
            value = self.coordinator.getConnectionValue(
                self._connection_uuid,
                attribute.key.format(install_index=self._install_index),
            )
            _LOGGER.debug(f"Update {self.name}.attribute[{attribute.label}]: {value}")
            attrs[attribute.label] = value

        return attrs

    def _value_from_coordinator(self):
        raw_value = value = self.coordinator.getConnectionValue(
            self._connection_uuid,
            self.entity_description.key.format(install_index=self._install_index),
        )

        if (
            value is None
            and self.entity_description.none_value_behaviour == NONE_IS_ZERO
        ):
            value = 0

        # Converting value is only needed when value isn't None or 0
        if value:
            if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
                if isinstance(value, str):
                    value = dt_util.parse_datetime(value)
                elif value > 100000000000000:
                    value = datetime.fromtimestamp(value/1000000, timezone('Europe/Amsterdam'))
                else:
                    value = datetime.fromtimestamp(value/1000, timezone('Europe/Amsterdam'))

            if self.entity_description.value_factor:
                value = value * self.entity_description.value_factor

        _LOGGER.debug(f"Value {self.name}: {value} [{raw_value}]")

        return value


class ZonneplanPvSensor(ZonneplanSensor):
    @property
    def install_uuid(self) -> str:
        """Return install ID."""
        if self._install_index < 0:
            return self._connection_uuid
        else:
            return self.coordinator.getConnectionValue(
                self._connection_uuid,
                "pv_installation.{install_index}.uuid".format(
                    install_index=self._install_index
                ),
            )

    @property
    def device_info(self):
        """Return the device information."""
        device_info = {
            "identifiers": {(DOMAIN, self._connection_uuid)},
            "manufacturer": "Zonneplan",
            "name": "Zonneplan",
        }

        if self._install_index >= 0:
            device_info["identifiers"] = {(DOMAIN, self.install_uuid)}
            device_info["via_device"] = (DOMAIN, self._connection_uuid)
            device_info["name"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "pv_installation.{install_index}.meta.name".format(
                    install_index=self._install_index
                ),
            ) + (f" ({self._install_index + 1})" if self._install_index and self._install_index > 0 else "")

            device_info["model"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "pv_installation.{install_index}.meta.name".format(
                    install_index=self._install_index
                ),
            ) + " " + str(self.coordinator.getConnectionValue(
                self._connection_uuid,
                "pv_installation.{install_index}.meta.panel_count".format(
                    install_index=self._install_index
                ),
            )) + " panels"

            device_info["serial_number"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "pv_installation.{install_index}.meta.sgn_serial_number".format(
                    install_index=self._install_index
                ),
            )
            device_info["sw_version"] = str(
                    self.coordinator.getConnectionValue(
                        self._connection_uuid,
                        "pv_installation.{install_index}.meta.module_firmware_version".format(
                            install_index=self._install_index
                        ),
                    )
                    or "unknown"
                )
            device_info["hw_version"] = str(
                    self.coordinator.getConnectionValue(
                        self._connection_uuid,
                        "pv_installation.{install_index}.meta.inverter_firmware_version".format(
                            install_index=self._install_index
                        ),
                    )
                    or "unknown"
                )

        return device_info


class ZonneplanP1Sensor(ZonneplanSensor):
    @property
    def install_uuid(self) -> str:
        """Return install ID."""
        if self._install_index < 0:
            return self._connection_uuid
        else:
            return self.coordinator.getConnectionValue(
                self._connection_uuid,
                "p1_installation.{install_index}.uuid".format(
                    install_index=self._install_index
                ),
            )

    @property
    def device_info(self):
        """Return the device information."""
        device_info = {
            "identifiers": {(DOMAIN, self._connection_uuid)},
            "manufacturer": "Zonneplan",
            "name": "Zonneplan",
        }

        if self._install_index >= 0:
            device_info["identifiers"] = {(DOMAIN, self.install_uuid)}
            device_info["via_device"] = (DOMAIN, self._connection_uuid)
            device_info["name"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "p1_installation.{install_index}.label".format(
                    install_index=self._install_index
                ),
            ) + (f" ({self._install_index + 1})" if self._install_index and self._install_index > 0 else "")
            device_info["model"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "p1_installation.{install_index}.label".format(
                    install_index=self._install_index
                ),
            )
            device_info["serial_number"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "p1_installation.{install_index}.meta.sgn_serial_number".format(
                    install_index=self._install_index
                ),
            )
            device_info["sw_version"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "p1_installation.{install_index}.meta.sgn_firmware".format(
                    install_index=self._install_index
                ),
            )

        return device_info


class ZonneplanChargePointSensor(ZonneplanSensor):
    @property
    def install_uuid(self) -> str:
        """Return install ID."""
        if self._install_index < 0:
            return self._connection_uuid
        else:
            return self.coordinator.getConnectionValue(
                self._connection_uuid,
                "charge_point_installation.{install_index}.uuid".format(
                    install_index=self._install_index
                ),
            )

    @property
    def device_info(self):
        """Return the device information."""
        device_info = {
            "identifiers": {(DOMAIN, self._connection_uuid)},
            "manufacturer": "Zonneplan",
            "name": "Zonneplan",
        }

        if self._install_index >= 0:
            device_info["identifiers"] = {(DOMAIN, self.install_uuid)}
            device_info["via_device"] = (DOMAIN, self._connection_uuid)
            device_info["name"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "charge_point_installation.{install_index}.label".format(
                    install_index=self._install_index
                ),
            ) + (f" ({self._install_index + 1})" if self._install_index and self._install_index > 0 else "")
            device_info["model"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "charge_point_installation.{install_index}.label".format(
                    install_index=self._install_index
                ),
            )
            device_info["serial_number"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "charge_point_installation.{install_index}.meta.serial_number".format(
                    install_index=self._install_index
                ),
            )

        return device_info


class ZonneplanBatterySensor(ZonneplanSensor):
    @property
    def install_uuid(self) -> str:
        """Return install ID."""
        if self._install_index < 0:
            return self._connection_uuid
        else:
            return self.coordinator.getConnectionValue(
                self._connection_uuid,
                "home_battery_installation.{install_index}.uuid".format(
                    install_index=self._install_index
                ),
            )

    @property
    def device_info(self):
        """Return the device information."""
        device_info = {
            "identifiers": {(DOMAIN, self._connection_uuid)},
            "manufacturer": "Zonneplan",
            "name": "Zonneplan",
        }

        if self._install_index >= 0:
            device_info["identifiers"] = {(DOMAIN, self.install_uuid)}
            device_info["via_device"] = (DOMAIN, self._connection_uuid)
            device_info["name"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "home_battery_installation.{install_index}.label".format(
                    install_index=self._install_index
                ),
            ) + (f" ({self._install_index + 1})" if self._install_index and self._install_index > 0 else "")
            device_info["model"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "home_battery_installation.{install_index}.label".format(
                    install_index=self._install_index
                ),
            )
            device_info["serial_number"] = self.coordinator.getConnectionValue(
                self._connection_uuid,
                "home_battery_installation.{install_index}.meta.identifier".format(
                    install_index=self._install_index
                ),
            )

        return device_info
