"""Number platform for Irritrol LifeDC."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import IrritrolLifeDCBleEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for zone in range(1, 5):
        entities.append(IrritrolDurationNumber(controller, zone, "minutes"))
        entities.append(IrritrolDurationNumber(controller, zone, "seconds"))

    entities.append(IrritrolDelayNumber(controller))

    async_add_entities(entities)


class IrritrolDurationNumber(IrritrolLifeDCBleEntity, NumberEntity):
    _attr_mode = NumberMode.BOX
    _attr_native_step = 1
    _attr_native_min_value = 0

    def __init__(self, controller, zone: int, unit: str) -> None:
        self.zone = zone
        self.unit = unit
        key = f"zone_{zone}_{unit}"
        name = f"Zone {zone} {unit}"
        super().__init__(controller, "number", key, name)
        self._attr_native_unit_of_measurement = "min" if unit == "minutes" else "s"
        self._attr_native_max_value = 25 if unit == "minutes" else 59

    @property
    def native_value(self) -> float:
        if self.unit == "minutes":
            return self.controller.zone_minutes[self.zone]
        return self.controller.zone_seconds[self.zone]

    async def async_set_native_value(self, value: float) -> None:
        if self.unit == "minutes":
            self.controller.zone_minutes[self.zone] = value
        else:
            self.controller.zone_seconds[self.zone] = value
        self.controller._notify()


class IrritrolDelayNumber(IrritrolLifeDCBleEntity, NumberEntity):
    _attr_mode = NumberMode.BOX
    _attr_native_step = 1
    _attr_native_min_value = 0
    _attr_native_max_value = 30
    _attr_native_unit_of_measurement = "s"

    def __init__(self, controller) -> None:
        super().__init__(controller, "number", "inter_zone_delay", "Inter-zone delay")

    @property
    def native_value(self) -> float:
        return self.controller.inter_zone_delay

    async def async_set_native_value(self, value: float) -> None:
        self.controller.inter_zone_delay = value
        self.controller._notify()
