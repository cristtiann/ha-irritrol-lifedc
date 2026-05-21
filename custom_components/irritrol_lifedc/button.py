"""Button platform for Irritrol LifeDC."""
from __future__ import annotations

from dataclasses import dataclass
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ENTITY_PREFIX, DOMAIN
from .entity import IrritrolEntity


@dataclass(frozen=True)
class ButtonDescription:
    key: str
    name: str
    source_suffix: str


BUTTONS = [
    ButtonDescription("start_cycle_forward", "Start cycle 1-2-3-4", "irritrol_start_cycle_1_2_3_4"),
    ButtonDescription("start_cycle_reverse", "Start cycle 4-3-2-1", "irritrol_start_cycle_4_3_2_1"),
    ButtonDescription("repeat_cycle_2", "Repeat cycle 2 times", "irritrol_repeat_cycle_2_times"),
    ButtonDescription("repeat_cycle_3", "Repeat cycle 3 times", "irritrol_repeat_cycle_3_times"),
    ButtonDescription("stop", "Stop", "irritrol_stop"),
    ButtonDescription("pause", "Pause", "irritrol_pause"),
    ButtonDescription("resume", "Resume", "irritrol_resume"),
    ButtonDescription("next", "Next zone", "irritrol_next"),
    ButtonDescription("run_zone_1", "Run zone 1", "irritrol_run_zone_1_timed"),
    ButtonDescription("run_zone_2", "Run zone 2", "irritrol_run_zone_2_timed"),
    ButtonDescription("run_zone_3", "Run zone 3", "irritrol_run_zone_3_timed"),
    ButtonDescription("run_zone_4", "Run zone 4", "irritrol_run_zone_4_timed"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    prefix = hass.data[DOMAIN][entry.entry_id][CONF_ENTITY_PREFIX]
    async_add_entities([IrritrolButton(entry, prefix, description) for description in BUTTONS])


class IrritrolButton(IrritrolEntity, ButtonEntity):
    def __init__(self, entry: ConfigEntry, prefix: str, description: ButtonDescription) -> None:
        super().__init__(entry, description.key, description.name)
        self._source_entity_id = f"button.{prefix}_{description.source_suffix}"

    async def async_press(self) -> None:
        await self.hass.services.async_call("button", "press", {"entity_id": self._source_entity_id}, blocking=True)
