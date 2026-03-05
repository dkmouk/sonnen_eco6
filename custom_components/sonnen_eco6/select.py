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

OPT_LAST_SET_MODE = "last_set_mode"


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

    def _label_for_mode_num(self, num: int) -> str | None:
        for label, val in OP_MODES.items():
            if val == num:
                return label
        return None

    @property
    def current_option(self) -> str | None:
        # 1) Try to interpret current "state" from M06
        m06 = self.coordinator.data.get("M06")
        try:
            state_num = int(float(m06))
        except Exception:
            state_num = None

        # 2) Read last explicitly set mode (persisted in config entry options)
        last_set = self.entry.options.get(OPT_LAST_SET_MODE)
        if isinstance(last_set, (int, float, str)):
            try:
                last_set = int(float(last_set))
            except Exception:
                last_set = None
        else:
            last_set = None

        # If M06 is one of our explicit modes (10/12/20/22/13), show it
        if state_num is not None:
            direct = self._label_for_mode_num(state_num)
            if direct is not None and state_num != 13:
                # For everything except 13, M06 can be shown directly
                return direct

        # Special handling for 13:
        # 13 can mean "charging state" under Auto OR the explicitly set mode "Angepasst Laden".
        if state_num == 13:
            if last_set == 13:
                return self._label_for_mode_num(13)  # "Angepasst Laden"
            # otherwise treat it as "Auto is charging"
            return self._label_for_mode_num(10)  # "Auto"

        # If we don't have M06 mapping, fall back to last_set
        if isinstance(last_set, int):
            return self._label_for_mode_num(last_set)

        return None

    async def async_select_option(self, option: str) -> None:
        store = self.hass.data[DOMAIN][self.entry.entry_id]
        host: str = store["host"]
        port_ctrl: int = store["port_ctrl"]
        device_num: int = store.get("device_num", 10)

        new_mode = int(OP_MODES[option])
        url = (
            f"http://{host}:{port_ctrl}/data_request?"
            f"id=action&output_format=xml&DeviceNum={device_num}"
            f"&serviceId=urn:psi-storage-com:serviceId:Battery1"
            f"&action=SetOperationMode&newOperationModeValue={new_mode}"
        )

        async with async_timeout.timeout(8):
            resp = await self._session.get(url)
            resp.raise_for_status()

        # Persist last set mode so it survives restarts
        new_opts = dict(self.entry.options)
        new_opts[OPT_LAST_SET_MODE] = new_mode
        self.hass.config_entries.async_update_entry(self.entry, options=new_opts)

        await self.coordinator.async_request_refresh()