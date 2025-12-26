from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, METRICS
from .coordinator import SonnenEco6Coordinator

_DEVICE_CLASS_MAP: dict[str, SensorDeviceClass] = {
    "power": SensorDeviceClass.POWER,
    "battery": SensorDeviceClass.BATTERY,
}


@dataclass(frozen=True)
class SonnenMetric:
    metric_id: str
    name: str
    unit: str | None
    device_class: str | None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    store = hass.data[DOMAIN][entry.entry_id]
    coordinator: SonnenEco6Coordinator = store["coordinator"]

    metrics: list[SonnenMetric] = [
        SonnenMetric(
            metric_id=mid,
            name=cfg["name"],
            unit=cfg.get("unit"),
            device_class=cfg.get("device_class"),
        )
        for mid, cfg in METRICS.items()
    ]

    device_info = store.get("device_info")
    async_add_entities(
        [SonnenEco6Sensor(coordinator, entry, device_info, metric) for metric in metrics],
        update_before_add=False,
    )


class SonnenEco6Sensor(CoordinatorEntity[SonnenEco6Coordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SonnenEco6Coordinator,
        entry: ConfigEntry,
        device_info: Any,
        metric: SonnenMetric,
    ) -> None:
        super().__init__(coordinator)
        self._metric = metric

        if device_info is not None:
            self._attr_device_info = device_info

        if metric.metric_id in ("M06", "M10", "M11", "M12"):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

        self._attr_name = metric.name
        self._attr_unique_id = f"{entry.entry_id}_{metric.metric_id}"
        self._attr_native_unit_of_measurement = metric.unit
        self._attr_device_class = _DEVICE_CLASS_MAP.get(metric.device_class)

        if metric.device_class == "power":
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif metric.metric_id == "M05":
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        val = self.coordinator.data.get(self._metric.metric_id)

        if isinstance(val, str):
            s = val.strip()
            try:
                if "." in s:
                    return float(s)
                return int(s)
            except Exception:
                return s

        return val
