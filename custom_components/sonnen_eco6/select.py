from __future__ import annotations

import async_timeout

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, OP_MODES
from .coordinator import SonnenEco6Coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    store = hass.data[DOMAIN][entry.entry_id]
    coordinator: SonnenEco6Coordinator = store["coordinator"]
    device_info = store.get("device_info")

    async_add_entities(
        [SonnenEco6ModeSelect(hass, coordinator, entry, device_info)],
        update_before_add=False,
    )


class SonnenEco6ModeSelect(CoordinatorEntity[SonnenEco6Coordinator], SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Modus"
    _attr_icon = "mdi:battery-charging"
    _attr_options = list(OP_MODES.keys())

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: SonnenEco6Coordinator,
        entry: ConfigEntry,
        device_info,
    ) -> None:
        super().__init__(coordinator)
        self.hass = hass
        self.entry = entry
        self._session = async_get_clientsession(hass)

        if device_info is not None:
            self._attr_device_info = device_info

        self._attr_unique_id = f"{entry.entry_id}_mode_select"

    @property
    def current_option(self) -> str | None:
        m06 = self.coordinator.data.get("M06")
        try:
            mode_num = int(float(m06))
        except Exception:
            return None

        for label, num in OP_MODES.items():
            if num == mode_num:
                return label

        return None

    async def async_select_option(self, option: str) -> None:
        store = self.hass.data[DOMAIN][self.entry.entry_id]
        host: str = store["host"]
        port_ctrl: int = store["port_ctrl"]
        device_num: int = store.get("device_num", 10)

        new_mode = OP_MODES[option]
        url = (
            f"http://{host}:{port_ctrl}/data_request?"
            f"id=action&output_format=xml&DeviceNum={device_num}"
            f"&serviceId=urn:psi-storage-com:serviceId:Battery1"
            f"&action=SetOperationMode&newOperationModeValue={new_mode}"
        )

        async with async_timeout.timeout(8):
            resp = await self._session.get(url)
            resp.raise_for_status()

        await self.coordinator.async_request_refresh()
