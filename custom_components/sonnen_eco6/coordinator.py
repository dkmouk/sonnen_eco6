from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any

import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, METRICS

_LOGGER = logging.getLogger(__name__)


def _extract_value(payload: Any) -> float | int | str | None:
    """Extract a usable scalar value from common JSON shapes."""
    if payload is None:
        return None
    if isinstance(payload, (int, float, str)):
        return payload
    if isinstance(payload, dict):
        for k in ("value", "Value", "data", "val", "result"):
            if k in payload:
                return payload[k]
        if len(payload) == 1:
            return next(iter(payload.values()))
    return None


class SonnenEco6Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, host: str, port_data: int, scan_interval: int):
        self.hass = hass
        self.host = host
        self.port_data = port_data
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _fetch_metric(self, metric_id: str) -> Any:
        url = f"http://{self.host}:{self.port_data}/rest/devices/battery/{metric_id}"
        try:
            async with async_timeout.timeout(8):
                resp = await self.session.get(url)
                resp.raise_for_status()
                text = await resp.text()

            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                payload = text.strip()

            return _extract_value(payload)
        except Exception as err:
            raise UpdateFailed(f"Error fetching {metric_id} from {url}: {err}") from err

    async def _async_update_data(self) -> dict[str, Any]:
        tasks = [self._fetch_metric(mid) for mid in METRICS.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        data: dict[str, Any] = {}
        errors = 0

        for mid, res in zip(METRICS.keys(), results, strict=True):
            if isinstance(res, Exception):
                errors += 1
                _LOGGER.debug("Fetch failed for %s: %s", mid, res)
                data[mid] = None
            else:
                data[mid] = res

        if errors == len(METRICS):
            raise UpdateFailed("All Sonnen eco6 metric fetches failed")

        return data
