"""Sensor platform for Irritrol LifeDC."""
from __future__ import annotations

from dataclasses import dataclass
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_ENTITY_PREFIX, DOMAIN
from .entity import IrritrolEntity


@dataclass(frozen=True)
class SensorDescription:
    key: str
    name: str
    source_suffix: str
    native_unit_of_measurement: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None


SENSORS = [
    SensorDescription("status", "Status", "irrigation_status"),
    SensorDescription("lifedc_rssi", "LifeDC RSSI", "lifedc_rssi", "dBm", SensorDeviceClass.SIGNAL_STRENGTH,SensorStateClass.MEASUREMENT,),
    SensorDescription("cycle_progress", "Cycle progress", "cycle_progress", "%",SensorStateClass.MEASUREMENT,),
    SensorDescription("cycle_time_remaining", "Cycle time remaining", "cycle_time_remaining", "s", SensorDeviceClass.DURATION,SensorStateClass.MEASUREMENT,),
]

for zone in range(1, 5):
    SENSORS.append(SensorDescription(f"zone_{zone}_progress", f"Zone {zone} progress", f"zone_{zone}_progress", "%"))
    SENSORS.append(SensorDescription(f"zone_{zone}_time_remaining", f"Zone {zone} time remaining", f"zone_{zone}_time_remaining", "s", SensorDeviceClass.DURATION))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_ENTITY_PREFIX]
    async_add_entities([IrritrolSensor(entry, prefix, description) for description in SENSORS])


class IrritrolSensor(IrritrolEntity, SensorEntity):
    def __init__(self, entry: ConfigEntry, prefix: str, description: SensorDescription) -> None:
        super().__init__(entry, description.key, description.name)
        self._source_entity_id = f"sensor.{prefix}_{description.source_suffix}"
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class

        if description.native_unit_of_measurement == "%":
            self._attr_suggested_display_precision = 0

        self._attr_available = False
        self._attr_native_value = None

    async def async_added_to_hass(self) -> None:
        @callback
        def _state_changed(event):
            self._update_from_state()
            self.async_write_ha_state()

        self.async_on_remove(async_track_state_change_event(self.hass, [self._source_entity_id], _state_changed))
        self._update_from_state()

    def _update_from_state(self) -> None:
        state = self.hass.states.get(self._source_entity_id)
        self._attr_available = state is not None and state.state not in ("unavailable", "unknown")

        if state is None or not self._attr_available:
            self._attr_native_value = None
            return

        if self._attr_native_unit_of_measurement in ("%", "s", "dBm"):
            try:
                value = float(state.state)

                if self._attr_native_unit_of_measurement in ("%", "s"):
                    self._attr_native_value = round(value)
                else:
                    self._attr_native_value = value

            except (TypeError, ValueError):
                self._attr_native_value = None

            return

        self._attr_native_value = state.state
