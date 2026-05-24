"""Binary sensor platform for Irritrol LifeDC."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import IrritrolLifeDCBleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Irritrol LifeDC BLE binary sensors."""
    controller = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            IrritrolConnectedSensor(controller),
            IrritrolBleSeenSensor(controller),
        ]
    )


class IrritrolConnectedSensor(IrritrolLifeDCBleEntity, BinarySensorEntity):
    """Connection status sensor."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, controller) -> None:
        super().__init__(
            controller,
            "binary_sensor",
            "connected",
            "Connected",
        )

    @property
    def is_on(self) -> bool:
        return bool(self.controller.connected)


class IrritrolBleSeenSensor(IrritrolLifeDCBleEntity, BinarySensorEntity):
    """BLE seen status sensor."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, controller) -> None:
        super().__init__(
            controller,
            "binary_sensor",
            "ble_seen",
            "BLE Device Seen",
        )

    @property
    def is_on(self) -> bool:
        return self.controller.last_seen is not None