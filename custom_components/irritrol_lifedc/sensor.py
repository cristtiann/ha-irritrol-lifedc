"""Sensor platform for Irritrol LifeDC."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import IrritrolLifeDCBleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Irritrol LifeDC BLE sensors."""
    controller = hass.data[DOMAIN][entry.entry_id]

    entities = [
        IrritrolStatusSensor(controller),
        IrritrolDeviceNameSensor(controller),
        IrritrolBleAddressSensor(controller),
        IrritrolBleRssiSensor(controller),
        IrritrolBleLastSeenSensor(controller),
        IrritrolBleSourceSensor(controller),
        IrritrolActiveZoneSensor(controller),
        IrritrolCycleProgressSensor(controller),
        IrritrolCycleRemainingSensor(controller),
        IrritrolLastErrorSensor(controller),
    ]

    for zone in range(1, 5):
        entities.append(IrritrolZoneProgressSensor(controller, zone))
        entities.append(IrritrolZoneRemainingSensor(controller, zone))

    async_add_entities(entities)


class IrritrolStatusSensor(IrritrolLifeDCBleEntity, SensorEntity):
    def __init__(self, controller) -> None:
        super().__init__(controller, "sensor", "status", "Status")

    @property
    def native_value(self):
        return self.controller.status


class IrritrolDeviceNameSensor(IrritrolLifeDCBleEntity, SensorEntity):
    def __init__(self, controller) -> None:
        super().__init__(controller, "sensor", "device_name", "Device Name")

    @property
    def native_value(self):
        return self.controller.ble_device_name


class IrritrolBleAddressSensor(IrritrolLifeDCBleEntity, SensorEntity):
    def __init__(self, controller) -> None:
        super().__init__(controller, "sensor", "ble_address", "BLE MAC Address")

    @property
    def native_value(self):
        return self.controller.address


class IrritrolBleRssiSensor(IrritrolLifeDCBleEntity, SensorEntity):
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, controller) -> None:
        super().__init__(controller, "sensor", "ble_rssi", "BLE RSSI")

    @property
    def native_value(self):
        if self.controller.rssi is None:
            return None
        return int(self.controller.rssi)


class IrritrolBleLastSeenSensor(IrritrolLifeDCBleEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, controller) -> None:
        super().__init__(controller, "sensor", "ble_last_seen", "BLE Last Seen")

    @property
    def native_value(self):
        return self.controller.last_seen


class IrritrolBleSourceSensor(IrritrolLifeDCBleEntity, SensorEntity):
    def __init__(self, controller) -> None:
        super().__init__(controller, "sensor", "ble_source", "Bluetooth Source")

    @property
    def native_value(self):
        return self.controller.ble_source


class IrritrolActiveZoneSensor(IrritrolLifeDCBleEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, controller) -> None:
        super().__init__(controller, "sensor", "active_zone", "Active Zone")

    @property
    def native_value(self):
        return self.controller.active_zone


class IrritrolCycleProgressSensor(IrritrolLifeDCBleEntity, SensorEntity):
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, controller) -> None:
        super().__init__(controller, "sensor", "cycle_progress", "Cycle Progress")

    @property
    def native_value(self):
        return self.controller.cycle_progress


class IrritrolCycleRemainingSensor(IrritrolLifeDCBleEntity, SensorEntity):
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, controller) -> None:
        super().__init__(
            controller,
            "sensor",
            "cycle_time_remaining",
            "Cycle Time Remaining",
        )

    @property
    def native_value(self):
        return self.controller.cycle_remaining


class IrritrolZoneProgressSensor(IrritrolLifeDCBleEntity, SensorEntity):
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, controller, zone: int) -> None:
        self.zone = zone
        super().__init__(
            controller,
            "sensor",
            f"zone_{zone}_progress",
            f"Zone {zone} Progress",
        )

    @property
    def native_value(self):
        return self.controller.zone_progress.get(self.zone)


class IrritrolZoneRemainingSensor(IrritrolLifeDCBleEntity, SensorEntity):
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, controller, zone: int) -> None:
        self.zone = zone
        super().__init__(
            controller,
            "sensor",
            f"zone_{zone}_time_remaining",
            f"Zone {zone} Time Remaining",
        )

    @property
    def native_value(self):
        return self.controller.zone_remaining.get(self.zone)


class IrritrolLastErrorSensor(IrritrolLifeDCBleEntity, SensorEntity):
    def __init__(self, controller) -> None:
        super().__init__(controller, "sensor", "last_error", "Last Error")

    @property
    def native_value(self):
        return self.controller.last_error