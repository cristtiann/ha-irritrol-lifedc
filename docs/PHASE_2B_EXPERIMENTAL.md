# Phase 2B - Experimental Direct BLE Mode

Planned architecture:

```text
Home Assistant Irritrol LifeDC integration
        ↓
Home Assistant Bluetooth stack
        ↓
Local Bluetooth adapter or ESPHome Bluetooth Proxy
        ↓
Irritrol LifeDC BLE controller
```

This would remove the need for the dedicated ESPHome LifeDC YAML bridge. An ESP32 may still be used as a generic Bluetooth Proxy.

Known BLE details from Phase 1:

- Service UUID: `aa1c0001-eb88-44d3-8e21-6d83f5e221af`
- Write characteristic: `aa1c0002-eb88-44d3-8e21-6d83f5e221af`
- Notify characteristic: `aa1c0003-eb88-44d3-8e21-6d83f5e221af`
- ACK payload: `[0x3B, 0x00]`

This mode is not implemented in Phase 2A.
