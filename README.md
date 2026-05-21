# Irritrol LifeDC for Home Assistant

A HACS-ready Home Assistant custom integration for Irritrol LifeDC BLE irrigation controllers.

---

# Architecture

```text
Irritrol LifeDC Controller
        ↓ BLE
ESP32 + ESPHome bridge
        ↓ Home Assistant entities
Irritrol LifeDC Integration
        ↓
Dashboard / Scheduler / Automations
```

---

# Phase 2A architecture

This integration is a professional Home Assistant companion integration for the ESPHome BLE bridge built in Phase 1.

```text
Home Assistant integration
        ↓
ESPHome entities/buttons/numbers
        ↓
ESP32 BLE bridge
        ↓
Irritrol LifeDC controller
```

The ESP32 remains responsible for the BLE connection and command timing. This integration provides a cleaner Home Assistant layer with grouped entities, service helpers, diagnostics, dashboard examples and a path toward a future native BLE implementation.

---

# Important Notice

This integration currently depends on the ESPHome BLE bridge described in the Phase 1 project:

https://github.com/cristtiann/ha-Irritrol-LifeDC-BLE-Controller

Phase 1 contains:
- ESPHome firmware
- BLE reverse engineering
- BLE command handling
- timing logic
- ESP32 bridge configuration
- initial dashboard examples

This repository (Phase 2A) adds the polished Home Assistant integration layer.

---

# Required Hardware

- Irritrol LifeDC BLE irrigation controller
- ESP32 development board
- Home Assistant
- ESPHome integration
- Bluetooth capability (ESP32 BLE bridge)

Tested hardware:
- ESP32 DevKit v1
- ESP32-WROOM-32

---

# Requirements

- Home Assistant
- HACS (recommended)
- ESPHome device from Phase 1 already installed and working
- Irritrol LifeDC BLE controller

---

# Installation Flow

## Step 1 — ESPHome BLE Bridge

Install and configure the ESPHome bridge from:

https://github.com/cristtiann/ha-Irritrol-LifeDC-BLE-Controller

Make sure:
- ESP32 firmware is installed
- BLE communication is working
- ESPHome entities are visible in Home Assistant

---

## Step 2 — Install Irritrol LifeDC Integration

### Installation with HACS

1. In HACS, open **Integrations**
2. Click the three-dot menu
3. Choose **Custom repositories**
4. Add this repository URL:

```text
https://github.com/cristtiann/ha-irritrol-lifedc
```

5. Category: **Integration**
6. Install **Irritrol LifeDC**
7. Restart Home Assistant
8. Go to:

```text
Settings → Devices & Services → Add Integration
```

9. Search for:

```text
Irritrol LifeDC
```

10. Enter the ESPHome entity prefix

---

# Entity Prefix

The integration mirrors existing ESPHome entities.

Default ESPHome prefix from Phase 1 is usually:

```text
irritrol_irrigation
```

Example ESPHome entity:

```text
button.irritrol_irrigation_irritrol_start_cycle_1_2_3_4
```

The integration then creates cleaner companion entities such as:

```text
button.irritrol_lifedc_start_cycle_1_2_3_4
sensor.irritrol_lifedc_cycle_progress
switch.irritrol_lifedc_zone_1
```

---

# What this integration does

- Creates clean Home Assistant companion entities
- Calls the existing ESPHome buttons, switches and numbers
- Mirrors ESPHome sensor/binary_sensor states
- Provides integration-level services
- Adds diagnostics support
- Adds dashboard examples
- Keeps the BLE-critical logic on ESP32 for stability

---

# Integration services

```yaml
service: irritrol_lifedc.start_cycle
service: irritrol_lifedc.stop
service: irritrol_lifedc.next_zone
service: irritrol_lifedc.pause
service: irritrol_lifedc.resume
service: irritrol_lifedc.run_zone
```

---

# Dashboard Examples

Dashboard examples are included under:

```text
examples/
```

These dashboards use:
- Bubble Card
- Fold Entity Row
- Vertical Stack In Card

Recommended dashboard mode:
- Sections layout
- Dark theme

---

# Branding and dashboard assets

Brand assets are included under:

```text
custom_components/irritrol_lifedc/brand/
```

Files:
- `icon.png`
- `logo.png`

Project screenshots and additional branding assets are included under:

```text
images/
```

The original Bubble Card dashboard is included as:

```text
examples/legacy_dashboard_bubble_cards.yaml
```

---

# Future Phase 2B

Phase 2B will be an experimental native BLE mode using Home Assistant's Bluetooth stack.

It may communicate through:
- local Bluetooth adapters
- ESPHome Bluetooth Proxy

Architecture:

```text
Home Assistant integration
        ↓
Bluetooth stack / Bluetooth Proxy
        ↓
Irritrol LifeDC controller
```

That mode is intentionally not included here yet.

Phase 2A is currently the stable and recommended implementation.

---

# License

MIT

