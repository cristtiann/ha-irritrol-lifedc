"""Constants for Irritrol LifeDC."""
from __future__ import annotations

DOMAIN = "irritrol_lifedc"

CONF_ADDRESS = "address"
CONF_NAME = "name"
CONF_DEVICE = "device"
CONF_ENTITY_PREFIX = "entity_prefix"
MANUAL_ADDRESS_OPTION = "manual"

DEFAULT_ENTITY_PREFIX = "irritrol_lifedc"
DEFAULT_NAME = "Irritrol LifeDC"

MANUFACTURER = "Irritrol"
MODEL = "LifeDC"

# BLE UUIDs discovered from a tested Irritrol LifeDC 4-zone controller.
LIFEDC_SERVICE_UUID = "aa1c0001-eb88-44d3-8e21-6d83f5e221af"
LIFEDC_WRITE_UUID = "aa1c0002-eb88-44d3-8e21-6d83f5e221af"
LIFEDC_NOTIFY_UUID = "aa1c0003-eb88-44d3-8e21-6d83f5e221af"

# Options / protocol profile fields.
CONF_PROTOCOL_PROFILE = "protocol_profile"
CONF_SERVICE_UUID = "service_uuid"
CONF_WRITE_UUID = "write_uuid"
CONF_NOTIFY_UUID = "notify_uuid"
CONF_ACK_PAYLOAD = "ack_payload"
CONF_STOP_PAYLOAD = "stop_payload"
CONF_ZONE_1_PAYLOAD = "zone_1_payload"
CONF_ZONE_2_PAYLOAD = "zone_2_payload"
CONF_ZONE_3_PAYLOAD = "zone_3_payload"
CONF_ZONE_4_PAYLOAD = "zone_4_payload"
CONF_ACK_DELAY = "ack_delay"

PROFILE_KNOWN_LIFEDC_4_ZONE = "known_lifedc_4_zone"
PROFILE_CUSTOM = "custom"

DEFAULT_ACK_DELAY = 0.5

DEFAULT_ACK_PAYLOAD = "3B 00"
DEFAULT_STOP_PAYLOAD = "31 05 15 00 FF 00 00"
DEFAULT_ZONE_PAYLOADS = {
    1: "31 05 12 01 00 00 B4",
    2: "31 05 12 02 00 00 B4",
    3: "31 05 12 03 00 00 B4",
    4: "31 05 12 04 00 00 78",
}

PLATFORMS = ["button", "switch", "number", "sensor", "binary_sensor"]
