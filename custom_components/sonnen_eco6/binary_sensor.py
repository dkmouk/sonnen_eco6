from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SonnenEco6Coordinator

POWER_THRESHOLD_W = 10.0


@dataclass(frozen=True)
class SonnenBinary:
    key: str
    name: str
    metric_id: str
    icon: str


BINARIES = [
    SonnenBinary(key="charging", name="Lädt", metric_id="M35", icon="mdi:battery-charging"),
    SonnenBinary(key="discharging", name="Entlädt", metric_id="M34", icon="mdi:battery-minus"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    store = hass.data[DOMAIN][entry.entry_id]
    coordinator: SonnenEco6Coordinator = store["coordinator"]
    device_info = store.get("device_info")

    async_add_entities(
        [SonnenEco6BinarySensor(coordinator, entry, device_info, desc) for desc in BINARIES],
        update_before_add=False,
    )


class SonnenEco6BinarySensor(CoordinatorEntity[SonnenEco6Coordinator], BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SonnenEco6Coordinator,
        entry: ConfigEntry,
        device_info,
        desc: SonnenBinary,
    ) -> None:
        super().__init__(coordinator)
        self._desc = desc
        self._attr_name = desc.name
        self._attr_unique_id = f"{entry.entry_id}_bin_{desc.key}"
        self._attr_icon = desc.icon

        if device_info is not None:
            self._attr_device_info = device_info

    @property
    def is_on(self) -> bool:
        raw = self.coordinator.data.get(self._desc.metric_id)
        try:
            val = float(raw)
        except Exception:
            return False
        return val >= POWER_THRESHOLD_W
