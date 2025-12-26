from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .const import DOMAIN

TO_REDACT = {"host"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    store = hass.data[DOMAIN].get(entry.entry_id, {})
    coordinator = store.get("coordinator")

    diag = {
        "entry": {
            "title": entry.title,
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "runtime": {
            "device_num": store.get("device_num"),
            "last_update_success": getattr(coordinator, "last_update_success", None),
            "last_exception": str(getattr(coordinator, "last_exception", "")) if getattr(coordinator, "last_exception", None) else None,
        },
        "coordinator_data": getattr(coordinator, "data", None),
    }

    return async_redact_data(diag, TO_REDACT)
