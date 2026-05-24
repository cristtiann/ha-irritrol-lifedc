"""Diagnostics for Irritrol LifeDC."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry):
    controller = hass.data[DOMAIN][entry.entry_id]
    return {
        "address": controller.address,
        "configured_name": controller.name,
        "ble_device_name": controller.ble_device_name,
        "rssi": controller.rssi,
        "last_seen": controller.last_seen.isoformat() if controller.last_seen else None,
        "bluetooth_source": controller.ble_source,
        "status": controller.status,
        "active_zone": controller.active_zone,
        "connected": controller.connected,
        "last_error": controller.last_error,
        "protocol_options": dict(entry.options),
    }
