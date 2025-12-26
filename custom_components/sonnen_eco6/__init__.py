from __future__ import annotations

import json
import logging
from typing import Any

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT_DATA,
    CONF_PORT_CTRL,
    CONF_SCAN_INTERVAL,
    CONF_DEVICE_NUM,
)
from .coordinator import SonnenEco6Coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "select", "binary_sensor"]


def _find_device_num(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None

    devices = payload.get("devices")
    if not isinstance(devices, list):
        return None

    def score(dev: dict) -> int:
        s = 0
        name = str(dev.get("name", "")).lower()
        dtype = str(dev.get("device_type", "")).lower()
        did = dev.get("id")

        if "battery" in name:
            s += 5
        if "battery" in dtype:
            s += 5
        if "psi-storage" in dtype:
            s += 3
        if isinstance(did, int):
            s += 2
        return s

    best = None
    best_score = 0
    for dev in devices:
        if not isinstance(dev, dict):
            continue
        sc = score(dev)
        if sc > best_score:
            best_score = sc
            best = dev

    if best and isinstance(best.get("id"), int) and best_score >= 7:
        return best["id"]

    return None


async def _auto_detect_device_num(hass: HomeAssistant, host: str, port_ctrl: int) -> int | None:
    session = async_get_clientsession(hass)
    urls = [
        f"http://{host}:{port_ctrl}/data_request?id=lu_sdata",
        f"http://{host}:{port_ctrl}/data_request?id=user_data",
    ]

    for url in urls:
        try:
            async with async_timeout.timeout(8):
                resp = await session.get(url)
                resp.raise_for_status()
                text = await resp.text()

            payload = json.loads(text)
            found = _find_device_num(payload)
            if found is not None:
                _LOGGER.info("Auto-detected Sonnen DeviceNum=%s via %s", found, url)
                return found
        except Exception as err:
            _LOGGER.debug("DeviceNum auto-detect failed via %s: %s", url, err)

    return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = entry.data
    options = entry.options

    host: str = data[CONF_HOST]
    port_data: int = data[CONF_PORT_DATA]
    port_ctrl: int = data[CONF_PORT_CTRL]
    scan_interval: int = options.get(CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, 10))

    coordinator = SonnenEco6Coordinator(
        hass=hass,
        host=host,
        port_data=port_data,
        scan_interval=scan_interval,
    )
    await coordinator.async_config_entry_first_refresh()

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="SonnenBatterie eco 6.0",
        manufacturer="sonnen",
        model="eco 6.0",
        configuration_url=f"http://{host}:{port_ctrl}",
    )

    configured_device_num = data.get(CONF_DEVICE_NUM)
    if isinstance(configured_device_num, int) and configured_device_num != 10:
        device_num = configured_device_num
    else:
        detected = await _auto_detect_device_num(hass, host, port_ctrl)
        device_num = detected if detected is not None else 10

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "host": host,
        "port_ctrl": port_ctrl,
        "device_num": device_num,
        "device_info": device_info,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
