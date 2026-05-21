"""Number platform for Irritrol LifeDC."""
from __future__ import annotations

from dataclasses import dataclass
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_ENTITY_PREFIX, DOMAIN
from .entity import IrritrolEntity


@dataclass(frozen=True)
class NumberDescription:
    key: str
    name: str
    source_suffix: str
    native_min_value: float
    native_max_value: float
    native_step: float
    native_unit_of_measurement: str | None = None


NUMBERS = []
for zone in range(1, 5):
    NUMBERS.append(NumberDescription(f"zone_{zone}_minutes", f"Zone {zone} minutes", f"zone_{zone}_minutes", 0, 25, 1, "min"))
    NUMBERS.append(NumberDescription(f"zone_{zone}_seconds", f"Zone {zone} seconds", f"zone_{zone}_seconds", 0, 59, 1, "s"))
NUMBERS.append(NumberDescription("inter_zone_delay", "Inter-zone delay", "inter_zone_delay", 0, 30, 1, "s"))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_ENTITY_PREFIX]
    async_add_entities([IrritrolNumber(entry, prefix, description) for description in NUMBERS])


class IrritrolNumber(IrritrolEntity, NumberEntity):
    def __init__(self, entry: ConfigEntry, prefix: str, description: NumberDescription) -> None:
        super().__init__(entry, description.key, description.name)
        self._source_entity_id = f"number.{prefix}_{description.source_suffix}"
        self._attr_native_min_value = description.native_min_value
        self._attr_native_max_value = description.native_max_value
        self._attr_native_step = description.native_step
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        # Display number entities as editable input boxes instead of sliders,
        # matching the ESPHome UI behavior and making exact durations easier to enter.
        self._attr_mode = NumberMode.BOX
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
        if self._attr_available:
            try:
                self._attr_native_value = float(state.state)
            except (TypeError, ValueError):
                self._attr_native_value = None

    async def async_set_native_value(self, value: float) -> None:
        await self.hass.services.async_call("number", "set_value", {"entity_id": self._source_entity_id, "value": value}, blocking=True)
