"""Button platform for Irritrol LifeDC."""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Awaitable, Callable

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import IrritrolLifeDCBleEntity


@dataclass(frozen=True)
class ButtonDescription:
    key: str
    name: str
    press: Callable[[object], Awaitable[None]]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]

    descriptions = [
        ButtonDescription("start_cycle_1_2_3_4", "Start cycle 1-2-3-4", lambda c: c.async_start_cycle(False, 1)),
        ButtonDescription("start_cycle_4_3_2_1", "Start cycle 4-3-2-1", lambda c: c.async_start_cycle(True, 1)),
        ButtonDescription("repeat_cycle_2_times", "Repeat cycle 2 times", lambda c: c.async_start_cycle(False, 2)),
        ButtonDescription("repeat_cycle_3_times", "Repeat cycle 3 times", lambda c: c.async_start_cycle(False, 3)),
        ButtonDescription("run_zone_1", "Run zone 1", lambda c: c.async_run_zone(1)),
        ButtonDescription("run_zone_2", "Run zone 2", lambda c: c.async_run_zone(2)),
        ButtonDescription("run_zone_3", "Run zone 3", lambda c: c.async_run_zone(3)),
        ButtonDescription("run_zone_4", "Run zone 4", lambda c: c.async_run_zone(4)),
        ButtonDescription("next_zone", "Next zone", lambda c: c.async_next_zone()),
        ButtonDescription("pause", "Pause", lambda c: c.async_pause()),
        ButtonDescription("resume", "Resume", lambda c: c.async_resume()),
        ButtonDescription("stop", "Stop", lambda c: c.async_stop()),
    ]

    async_add_entities([IrritrolButton(controller, description) for description in descriptions])


class IrritrolButton(IrritrolLifeDCBleEntity, ButtonEntity):
    def __init__(self, controller, description: ButtonDescription) -> None:
        super().__init__(controller, "button", description.key, description.name)
        self.description = description

    async def async_press(self) -> None:
        await self.description.press(self.controller)
