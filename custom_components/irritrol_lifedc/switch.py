"""Switch platform for Irritrol LifeDC."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import IrritrolLifeDCBleEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IrritrolZoneSwitch(controller, zone) for zone in range(1, 5)])


class IrritrolZoneSwitch(IrritrolLifeDCBleEntity, SwitchEntity):
    def __init__(self, controller, zone: int) -> None:
        self.zone = zone
        super().__init__(controller, "switch", f"zone_{zone}", f"Zone {zone}")

    @property
    def is_on(self) -> bool:
        return self.controller.active_zone == self.zone

    async def async_turn_on(self, **kwargs) -> None:
        await self.controller.async_zone_on(self.zone)

    async def async_turn_off(self, **kwargs) -> None:
        await self.controller.async_stop()
