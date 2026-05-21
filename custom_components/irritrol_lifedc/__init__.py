"""Irritrol LifeDC companion integration for Home Assistant."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
import voluptuous as vol

from .const import (
    CONF_ENTITY_PREFIX,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    PLATFORMS,
    SERVICE_NEXT_ZONE,
    SERVICE_PAUSE,
    SERVICE_RESUME,
    SERVICE_RUN_ZONE,
    SERVICE_START_CYCLE,
    SERVICE_STOP,
)

_LOGGER = logging.getLogger(__name__)


def _eid(domain: str, prefix: str, suffix: str) -> str:
    return f"{domain}.{prefix}_{suffix}"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Irritrol LifeDC from a config entry."""
    prefix = entry.data[CONF_ENTITY_PREFIX]
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {CONF_ENTITY_PREFIX: prefix}

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer=MANUFACTURER,
        model=MODEL,
        name=entry.title,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def start_cycle(call: ServiceCall) -> None:
        direction = call.data.get("direction", "forward")
        repeat = int(call.data.get("repeat", 1))
        if repeat == 2:
            suffix = "irritrol_repeat_cycle_2_times"
        elif repeat == 3:
            suffix = "irritrol_repeat_cycle_3_times"
        elif direction == "reverse":
            suffix = "irritrol_start_cycle_4_3_2_1"
        else:
            suffix = "irritrol_start_cycle_1_2_3_4"
        await hass.services.async_call("button", "press", {"entity_id": _eid("button", prefix, suffix)}, blocking=True)

    async def stop(call: ServiceCall) -> None:
        await hass.services.async_call("button", "press", {"entity_id": _eid("button", prefix, "irritrol_stop")}, blocking=True)

    async def next_zone(call: ServiceCall) -> None:
        await hass.services.async_call("button", "press", {"entity_id": _eid("button", prefix, "irritrol_next")}, blocking=True)

    async def pause(call: ServiceCall) -> None:
        await hass.services.async_call("button", "press", {"entity_id": _eid("button", prefix, "irritrol_pause")}, blocking=True)

    async def resume(call: ServiceCall) -> None:
        await hass.services.async_call("button", "press", {"entity_id": _eid("button", prefix, "irritrol_resume")}, blocking=True)

    async def run_zone(call: ServiceCall) -> None:
        zone = int(call.data["zone"])
        if zone not in (1, 2, 3, 4):
            raise vol.Invalid("zone must be between 1 and 4")
        await hass.services.async_call(
            "button",
            "press",
            {"entity_id": _eid("button", prefix, f"irritrol_run_zone_{zone}_timed")},
            blocking=True,
        )

    hass.services.async_register(DOMAIN, SERVICE_START_CYCLE, start_cycle)
    hass.services.async_register(DOMAIN, SERVICE_STOP, stop)
    hass.services.async_register(DOMAIN, SERVICE_NEXT_ZONE, next_zone)
    hass.services.async_register(DOMAIN, SERVICE_PAUSE, pause)
    hass.services.async_register(DOMAIN, SERVICE_RESUME, resume)
    hass.services.async_register(
        DOMAIN,
        SERVICE_RUN_ZONE,
        run_zone,
        schema=vol.Schema({vol.Required("zone"): vol.Coerce(int)}),
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
