"""Config flow for Irritrol LifeDC."""
from __future__ import annotations

import logging
import re

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_ACK_DELAY,
    CONF_ACK_PAYLOAD,
    CONF_DEVICE,
    CONF_ENTITY_PREFIX,
    CONF_NOTIFY_UUID,
    CONF_PROTOCOL_PROFILE,
    CONF_SERVICE_UUID,
    CONF_STOP_PAYLOAD,
    CONF_WRITE_UUID,
    CONF_ZONE_1_PAYLOAD,
    CONF_ZONE_2_PAYLOAD,
    CONF_ZONE_3_PAYLOAD,
    CONF_ZONE_4_PAYLOAD,
    DEFAULT_ACK_DELAY,
    DEFAULT_ACK_PAYLOAD,
    DEFAULT_ENTITY_PREFIX,
    DEFAULT_NAME,
    DEFAULT_STOP_PAYLOAD,
    DEFAULT_ZONE_PAYLOADS,
    DOMAIN,
    LIFEDC_NOTIFY_UUID,
    LIFEDC_SERVICE_UUID,
    LIFEDC_WRITE_UUID,
    MANUAL_ADDRESS_OPTION,
    PROFILE_CUSTOM,
    PROFILE_KNOWN_LIFEDC_4_ZONE,
)

_LOGGER = logging.getLogger(__name__)

_LIFEDC_NAME_RE = re.compile(r"life[-_ ]?dc", re.IGNORECASE)
_HEX_RE = re.compile(r"^[0-9a-fA-F ,xX]+$")


def _normalize_address(address: str) -> str:
    """Normalize a BLE MAC address string."""
    return address.strip().upper()


def _looks_like_lifedc(info: bluetooth.BluetoothServiceInfoBleak) -> bool:
    """Return True if a discovered BLE advertisement looks like LifeDC."""
    name = info.name or ""
    service_uuids = {uuid.lower() for uuid in info.service_uuids or []}
    return LIFEDC_SERVICE_UUID in service_uuids or bool(_LIFEDC_NAME_RE.search(name))


def _valid_hex_payload(value: str) -> bool:
    """Validate a human-readable hex payload string."""
    value = value.strip()
    if not value or not _HEX_RE.match(value):
        return False
    tokens = value.replace(",", " ").split()
    try:
        for token in tokens:
            token = token[2:] if token.lower().startswith("0x") else token
            if not 0 <= int(token, 16) <= 255:
                return False
    except ValueError:
        return False
    return True


class IrritrolLifeDCBleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Irritrol LifeDC."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered: dict[str, bluetooth.BluetoothServiceInfoBleak] = {}
        self._discovered_address: str | None = None
        self._discovered_name: str | None = None

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Return the options flow."""
        return IrritrolLifeDCBleOptionsFlow(config_entry)

    def _discover_lifedc_devices(self) -> dict[str, str]:
        """Build a dropdown list of currently visible LifeDC BLE devices."""
        self._discovered = {}
        options: dict[str, str] = {}

        for info in bluetooth.async_discovered_service_info(self.hass, connectable=True):
            if not _looks_like_lifedc(info):
                continue

            address = _normalize_address(info.address)
            name = info.name or "Irritrol LifeDC"
            rssi = getattr(info, "rssi", None)
            label = f"{name} ({address})"
            if rssi is not None:
                label = f"{label} - {rssi} dBm"

            self._discovered[address] = info
            options[address] = label

        options[MANUAL_ADDRESS_OPTION] = "Manual entry - BLE MAC address"
        return options

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle manual setup or discovered device selection."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected = user_input.get(CONF_DEVICE)

            if selected and selected != MANUAL_ADDRESS_OPTION:
                address = _normalize_address(selected)
                info = self._discovered.get(address)
                name = (info.name if info else None) or DEFAULT_NAME
            else:
                address = _normalize_address(user_input[CONF_ADDRESS])
                name = user_input.get(CONF_NAME, DEFAULT_NAME)

            entity_prefix = user_input.get(CONF_ENTITY_PREFIX, DEFAULT_ENTITY_PREFIX).strip() or DEFAULT_ENTITY_PREFIX

            if not address:
                errors[CONF_ADDRESS] = "address_required"
            else:
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_ADDRESS: address,
                        CONF_NAME: name,
                        CONF_ENTITY_PREFIX: entity_prefix,
                    },
                )

        options = self._discover_lifedc_devices()

        if len(options) > 1:
            schema = vol.Schema(
                {
                    vol.Required(CONF_DEVICE, default=next(iter(options))): vol.In(options),
                    vol.Optional(CONF_ADDRESS, default=self._discovered_address or ""): str,
                    vol.Optional(CONF_NAME, default=self._discovered_name or DEFAULT_NAME): str,
                    vol.Optional(CONF_ENTITY_PREFIX, default=DEFAULT_ENTITY_PREFIX): str,
                }
            )
        else:
            schema = vol.Schema(
                {
                    vol.Required(CONF_ADDRESS, default=self._discovered_address or ""): str,
                    vol.Optional(CONF_NAME, default=self._discovered_name or DEFAULT_NAME): str,
                    vol.Optional(CONF_ENTITY_PREFIX, default=DEFAULT_ENTITY_PREFIX): str,
                }
            )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_bluetooth(self, discovery_info: bluetooth.BluetoothServiceInfoBleak) -> FlowResult:
        """Handle Bluetooth discovery."""
        if not _looks_like_lifedc(discovery_info):
            return self.async_abort(reason="not_supported")

        name = discovery_info.name or DEFAULT_NAME
        address = _normalize_address(discovery_info.address)

        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        self._discovered_address = address
        self._discovered_name = name
        self._discovered[address] = discovery_info

        self.context["title_placeholders"] = {"name": name}
        return await self.async_step_user()


class IrritrolLifeDCBleOptionsFlow(config_entries.OptionsFlow):
    """Options flow for editable BLE protocol payloads."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    def _option(self, key: str, default):
        return self._config_entry.options.get(key, default)

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Configure BLE UUIDs and payloads."""
        errors: dict[str, str] = {}

        if user_input is not None:
            for key in (
                CONF_ACK_PAYLOAD,
                CONF_STOP_PAYLOAD,
                CONF_ZONE_1_PAYLOAD,
                CONF_ZONE_2_PAYLOAD,
                CONF_ZONE_3_PAYLOAD,
                CONF_ZONE_4_PAYLOAD,
            ):
                if not _valid_hex_payload(user_input[key]):
                    errors[key] = "invalid_hex_payload"

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_PROTOCOL_PROFILE,
                    default=self._option(CONF_PROTOCOL_PROFILE, PROFILE_KNOWN_LIFEDC_4_ZONE),
                ): vol.In(
                    {
                        PROFILE_KNOWN_LIFEDC_4_ZONE: "Known Irritrol LifeDC 4-zone profile",
                        PROFILE_CUSTOM: "Custom payloads / firmware variant",
                    }
                ),
                vol.Required(CONF_SERVICE_UUID, default=self._option(CONF_SERVICE_UUID, LIFEDC_SERVICE_UUID)): str,
                vol.Required(CONF_WRITE_UUID, default=self._option(CONF_WRITE_UUID, LIFEDC_WRITE_UUID)): str,
                vol.Required(CONF_NOTIFY_UUID, default=self._option(CONF_NOTIFY_UUID, LIFEDC_NOTIFY_UUID)): str,
                vol.Required(CONF_ACK_PAYLOAD, default=self._option(CONF_ACK_PAYLOAD, DEFAULT_ACK_PAYLOAD)): str,
                vol.Required(CONF_STOP_PAYLOAD, default=self._option(CONF_STOP_PAYLOAD, DEFAULT_STOP_PAYLOAD)): str,
                vol.Required(CONF_ZONE_1_PAYLOAD, default=self._option(CONF_ZONE_1_PAYLOAD, DEFAULT_ZONE_PAYLOADS[1])): str,
                vol.Required(CONF_ZONE_2_PAYLOAD, default=self._option(CONF_ZONE_2_PAYLOAD, DEFAULT_ZONE_PAYLOADS[2])): str,
                vol.Required(CONF_ZONE_3_PAYLOAD, default=self._option(CONF_ZONE_3_PAYLOAD, DEFAULT_ZONE_PAYLOADS[3])): str,
                vol.Required(CONF_ZONE_4_PAYLOAD, default=self._option(CONF_ZONE_4_PAYLOAD, DEFAULT_ZONE_PAYLOADS[4])): str,
                vol.Required(CONF_ACK_DELAY, default=self._option(CONF_ACK_DELAY, DEFAULT_ACK_DELAY)): vol.Coerce(float),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
