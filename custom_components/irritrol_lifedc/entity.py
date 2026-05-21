"""Base entities for Irritrol LifeDC."""
from __future__ import annotations

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, MANUFACTURER, MODEL


class IrritrolEntity(Entity):
    """Base Irritrol entity."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, key: str, name: str) -> None:
        self._entry = entry
        self._key = key
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }
