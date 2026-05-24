"""Base entities for Irritrol LifeDC."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, MANUFACTURER, MODEL



class IrritrolLifeDCBleEntity(Entity):
    """Base Irritrol LifeDC entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        controller,
        platform: str,
        key: str,
        name: str | None = None,
    ) -> None:
        self.controller = controller

        safe_address = controller.address.replace(":", "").lower()

        self._attr_unique_id = f"{controller.entity_prefix}_{safe_address}_{key}"

        self._attr_translation_key = key

        self.entity_id = f"{platform}.{controller.entity_prefix}_{key}"

        if name is not None:
            self._attr_name = name

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.controller.address)},
            connections={(dr.CONNECTION_BLUETOOTH, self.controller.address)},
            name=self.controller.name,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self.controller.async_add_listener(self.async_write_ha_state)
        )