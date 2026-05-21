"""Diagnostics for Irritrol LifeDC."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get

from .const import CONF_ENTITY_PREFIX, DOMAIN


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    """Return diagnostics for a config entry."""
    prefix = entry.data.get(CONF_ENTITY_PREFIX)
    registry = async_get(hass)
    entities = [entity.entity_id for entity in registry.entities.values() if entity.config_entry_id == entry.entry_id]
    return {
        "domain": DOMAIN,
        "version": 1,
        "entity_prefix": prefix,
        "managed_entities": entities,
    }
