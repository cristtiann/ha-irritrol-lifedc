"""Direct BLE controller for Irritrol LifeDC."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from collections.abc import Callable

from bleak import BleakClient
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ACK_DELAY,
    CONF_ACK_PAYLOAD,
    CONF_ENTITY_PREFIX,
    CONF_STOP_PAYLOAD,
    CONF_WRITE_UUID,
    CONF_ZONE_1_PAYLOAD,
    CONF_ZONE_2_PAYLOAD,
    CONF_ZONE_3_PAYLOAD,
    CONF_ZONE_4_PAYLOAD,
    DEFAULT_ACK_DELAY,
    DEFAULT_ACK_PAYLOAD,
    DEFAULT_ENTITY_PREFIX,
    DEFAULT_STOP_PAYLOAD,
    DEFAULT_ZONE_PAYLOADS,
    LIFEDC_WRITE_UUID,
)

_LOGGER = logging.getLogger(__name__)


class IrritrolLifeDCBleController:
    """Manage Irritrol LifeDC commands and runtime state over direct BLE."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.address: str = entry.data[CONF_ADDRESS]
        self.name: str = entry.data.get(CONF_NAME, "Irritrol LifeDC")
        self.entity_prefix: str = entry.data.get(CONF_ENTITY_PREFIX, DEFAULT_ENTITY_PREFIX)

        self.ble_device_name: str | None = self.name
        self.rssi: int | None = None
        self.last_seen: datetime | None = None
        self.ble_source: str | None = None

        self.connected: bool = False
        self.last_error: str | None = None
        self.status: str = "Idle"
        self.active_zone: int = 0

        self.zone_minutes: dict[int, float] = {1: 0, 2: 0, 3: 0, 4: 0}
        self.zone_seconds: dict[int, float] = {1: 10, 2: 10, 3: 10, 4: 10}
        self.inter_zone_delay: float = 10

        self.zone_progress: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}
        self.zone_remaining: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}
        self.cycle_progress: int = 0
        self.cycle_remaining: int = 0

        self._listeners: set[Callable[[], None]] = set()
        self._task: asyncio.Task | None = None
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self._stop_event = asyncio.Event()
        self._next_event = asyncio.Event()
        self._metadata_remove_callbacks: list[Callable[[], None]] = []


    async def async_start(self) -> None:
        """Start metadata polling."""
        await self.async_refresh_ble_metadata()
        self._metadata_remove_callbacks.append(
            async_track_time_interval(
                self.hass,
                self._async_metadata_poll,
                timedelta(seconds=30),
            )
        )

    @callback
    def _async_metadata_poll(self, now) -> None:
        """Schedule BLE metadata refresh."""
        self.hass.async_create_task(self.async_refresh_ble_metadata())

    async def async_refresh_ble_metadata(self) -> None:
        """Refresh BLE advertisement metadata from Home Assistant's Bluetooth stack."""
        info = bluetooth.async_last_service_info(
            self.hass,
            self.address,
            connectable=True,
        )
        if info is None:
            return

        self.ble_device_name = info.name or self.ble_device_name or self.name
        self.rssi = getattr(info, "rssi", None)
        self.last_seen = dt_util.utcnow()
        self.ble_source = getattr(info, "source", None)
        self._notify()

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Add state listener."""
        self._listeners.add(listener)

        @callback
        def remove_listener() -> None:
            self._listeners.discard(listener)

        return remove_listener

    @callback
    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    def zone_duration(self, zone: int) -> int:
        """Return configured zone duration in seconds."""
        return int(self.zone_minutes[zone] * 60 + self.zone_seconds[zone])

    async def async_shutdown(self) -> None:
        """Stop active tasks and metadata polling."""
        for remove in self._metadata_remove_callbacks:
            remove()
        self._metadata_remove_callbacks.clear()
        await self.async_stop()

    async def _ble_device(self):
        await self.async_refresh_ble_metadata()
        return bluetooth.async_ble_device_from_address(
            self.hass,
            self.address,
            connectable=True,
        )

    def _parse_payload(self, value: str) -> list[int]:
        """Parse a payload string such as '31 05 12 01 00 00 B4'."""
        bytes_out: list[int] = []
        for token in value.replace(",", " ").split():
            token = token[2:] if token.lower().startswith("0x") else token
            bytes_out.append(int(token, 16))
        return bytes_out

    def _option(self, key: str, default):
        """Read a runtime protocol option."""
        return self.entry.options.get(key, default)

    @property
    def write_uuid(self) -> str:
        """BLE write characteristic UUID."""
        return self._option(CONF_WRITE_UUID, LIFEDC_WRITE_UUID)

    @property
    def ack_payload(self) -> list[int]:
        """ACK payload sent after command payloads."""
        return self._parse_payload(self._option(CONF_ACK_PAYLOAD, DEFAULT_ACK_PAYLOAD))

    @property
    def stop_payload(self) -> list[int]:
        """Valve off payload."""
        return self._parse_payload(self._option(CONF_STOP_PAYLOAD, DEFAULT_STOP_PAYLOAD))

    @property
    def ack_delay(self) -> float:
        """Delay between command and ACK write."""
        return float(self._option(CONF_ACK_DELAY, DEFAULT_ACK_DELAY))

    def zone_payload(self, zone: int) -> list[int]:
        """Return configured zone-on payload."""
        key_map = {
            1: CONF_ZONE_1_PAYLOAD,
            2: CONF_ZONE_2_PAYLOAD,
            3: CONF_ZONE_3_PAYLOAD,
            4: CONF_ZONE_4_PAYLOAD,
        }
        return self._parse_payload(self._option(key_map[zone], DEFAULT_ZONE_PAYLOADS[zone]))

    async def _write_payload(self, payload: list[int], *, send_ack: bool = True) -> None:
        """Connect, write a payload, optionally write ACK, then disconnect."""
        ble_device = await self._ble_device()
        if ble_device is None:
            self.connected = False
            self.last_error = f"BLE device {self.address} not found. Check Bluetooth adapter/proxy range."
            self._notify()
            raise RuntimeError(self.last_error)

        client: BleakClient | None = None
        try:
            client = await establish_connection(
                BleakClientWithServiceCache,
                ble_device,
                self.name,
                ble_device_callback=self._ble_device,
                max_attempts=3,
            )
            self.connected = True
            self.last_error = None
            await client.write_gatt_char(self.write_uuid, bytes(payload), response=False)

            if send_ack:
                await asyncio.sleep(self.ack_delay)
                await client.write_gatt_char(self.write_uuid, bytes(self.ack_payload), response=False)

        except Exception as err:
            self.connected = False
            self.last_error = str(err)
            _LOGGER.exception("LifeDC BLE command failed")
            raise

        finally:
            if client is not None and client.is_connected:
                await client.disconnect()
            self._notify()

    async def async_zone_on(self, zone: int) -> None:
        """Turn a zone on."""
        self.status = f"Running zone {zone}"
        self.active_zone = zone
        self._notify()
        await self._write_payload(self.zone_payload(zone))

    async def async_valve_off(self) -> None:
        """Turn current valve off."""
        await self._write_payload(self.stop_payload)

    async def async_stop(self) -> None:
        """Stop all irrigation activity."""
        self._stop_event.set()

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        try:
            await self.async_valve_off()
        except Exception:
            _LOGGER.warning("Failed to send valve off command", exc_info=True)

        self.status = "Idle"
        self.active_zone = 0
        self.cycle_progress = 0
        self.cycle_remaining = 0
        for zone in range(1, 5):
            self.zone_progress[zone] = 0
            self.zone_remaining[zone] = 0

        self._pause_event.set()
        self._stop_event.clear()
        self._next_event.clear()
        self._notify()

    async def async_pause(self) -> None:
        """Pause the software timer."""
        self._pause_event.clear()
        self.status = "Paused"
        self._notify()

    async def async_resume(self) -> None:
        """Resume the software timer."""
        self._pause_event.set()
        if self.active_zone:
            self.status = f"Running zone {self.active_zone}"
        self._notify()

    async def async_next_zone(self) -> None:
        """Skip to next zone."""
        self._next_event.set()
        self._notify()

    async def async_run_zone(self, zone: int) -> None:
        """Run one zone using configured duration."""
        await self._start_task(self._run_zone_task(zone, part_of_cycle=False))

    async def async_start_cycle(self, reverse: bool = False, repeat: int = 1) -> None:
        """Run a full cycle."""
        zones = [4, 3, 2, 1] if reverse else [1, 2, 3, 4]
        await self._start_task(self._cycle_task(zones, repeat))

#    async def _start_task(self, coro) -> None:
#        await self.async_stop()
#        self._stop_event.clear()
#        self._next_event.clear()
#        self._task = self.hass.async_create_task(coro)

    async def _start_task(self, coro) -> None:
        """Start a new irrigation task without sending valve off if already idle."""
        if self._task and not self._task.done():
            self._stop_event.set()
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

            try:
                await self.async_valve_off()
                await asyncio.sleep(2)
            except Exception:
                _LOGGER.warning("Failed to send valve off before new task", exc_info=True)

        self._stop_event.clear()
        self._next_event.clear()
        self._pause_event.set()
        self._task = self.hass.async_create_task(coro)

    async def _run_zone_task(self, zone: int, *, part_of_cycle: bool = False) -> None:
        duration = self.zone_duration(zone)
        if duration <= 0:
            self.status = f"Zone {zone} duration is 0"
            self._notify()
            return

        self.zone_progress[zone] = 0
        self.zone_remaining[zone] = duration

        try:
            await self.async_zone_on(zone)
        except Exception as err:
            self.status = "BLE command failed"
            self.last_error = str(err)
            self.active_zone = 0
            self._notify()
            return

        elapsed = 0
        try:
            while elapsed < duration and not self._stop_event.is_set() and not self._next_event.is_set():
                await self._pause_event.wait()
                await asyncio.sleep(1)
                elapsed += 1
                remaining = max(duration - elapsed, 0)
                self.zone_remaining[zone] = remaining
                self.zone_progress[zone] = round((elapsed * 100) / duration)
                self._notify()

        finally:
            await self.async_valve_off()
            self.zone_remaining[zone] = 0
            if not self._stop_event.is_set() and not self._next_event.is_set():
                self.zone_progress[zone] = 100
            self.active_zone = 0
            if not part_of_cycle:
                self.status = "Idle"
            self._notify()

    async def _cycle_task(self, zones: list[int], repeat: int) -> None:
        total = sum(self.zone_duration(zone) for zone in zones) * repeat
        if total <= 0:
            self.status = "Idle"
            self._notify()
            return

        self.cycle_progress = 0
        self.cycle_remaining = total
        elapsed_total = 0

        for _ in range(repeat):
            for zone in zones:
                if self._stop_event.is_set():
                    break

                self._next_event.clear()
                duration = self.zone_duration(zone)
                if duration <= 0:
                    continue

                await self.async_zone_on(zone)
                elapsed_zone = 0

                while elapsed_zone < duration and not self._stop_event.is_set() and not self._next_event.is_set():
                    await self._pause_event.wait()
                    await asyncio.sleep(1)
                    elapsed_zone += 1
                    elapsed_total += 1

                    self.zone_remaining[zone] = max(duration - elapsed_zone, 0)
                    self.zone_progress[zone] = round((elapsed_zone * 100) / duration)
                    self.cycle_remaining = max(total - elapsed_total, 0)
                    self.cycle_progress = round((elapsed_total * 100) / total)
                    self._notify()

                await self.async_valve_off()
                self.zone_remaining[zone] = 0
                self.zone_progress[zone] = 100 if not self._next_event.is_set() else self.zone_progress[zone]
                self.active_zone = 0
                self._notify()

                if self._stop_event.is_set():
                    break

                if zone != zones[-1] and self.inter_zone_delay > 0:
                    self.status = "Zone change delay"
                    self._notify()
                    await asyncio.sleep(self.inter_zone_delay)

        self.status = "Idle"
        self.active_zone = 0
        self.cycle_remaining = 0
        if not self._stop_event.is_set():
            self.cycle_progress = 100
        self._notify()
