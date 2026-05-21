"""Switch platform for Irritrol LifeDC."""
from __future__ import annotations

from dataclasses import dataclass
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_ENTITY_PREFIX, DOMAIN
from .entity import IrritrolEntity


@dataclass(frozen=True)
class SwitchDescription:
    key: str
    name: str
    source_suffix: str


SWITCHES = [
    SwitchDescription("zone_1", "Zone 1", "irritrol_zone_1"),
    SwitchDescription("zone_2", "Zone 2", "irritrol_zone_2"),
    SwitchDescription("zone_3", "Zone 3", "irritrol_zone_3"),
    SwitchDescription("zone_4", "Zone 4", "irritrol_zone_4"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_ENTITY_PREFIX]
    async_add_entities([IrritrolSwitch(entry, prefix, description) for description in SWITCHES])


class IrritrolSwitch(IrritrolEntity, SwitchEntity):
    def __init__(self, entry: ConfigEntry, prefix: str, description: SwitchDescription) -> None:
        super().__init__(entry, description.key, description.name)
        self._source_entity_id = f"switch.{prefix}_{description.source_suffix}"
        self._attr_available = False
        self._attr_is_on = False

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
        self._attr_is_on = state is not None and state.state == "on"

    async def async_turn_on(self, **kwargs) -> None:
        await self.hass.services.async_call("switch", "turn_on", {"entity_id": self._source_entity_id}, blocking=True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.hass.services.async_call("switch", "turn_off", {"entity_id": self._source_entity_id}, blocking=True)
