# Phase 2A - ESPHome Companion Integration

This is the stable professional integration path.

The LifeDC BLE connection remains on ESP32/ESPHome because it is close to the controller and can handle BLE write timing reliably.

The Home Assistant custom integration provides a clean UI layer and service abstraction above the ESPHome entities.

## Why not direct BLE first?

Direct BLE is possible, but it depends on Home Assistant's Bluetooth stack, adapter/proxy availability, reconnect handling and active GATT connection stability.

Phase 2A gives users a reliable integration now. Phase 2B can later implement direct BLE experimentally.
