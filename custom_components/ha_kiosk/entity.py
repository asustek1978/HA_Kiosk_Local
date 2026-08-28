"""Base entity for HA Kiosk Local."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HAKioskCoordinator


class HAKioskEntity(CoordinatorEntity[HAKioskCoordinator]):
    """Base HA Kiosk Local entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HAKioskCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self.entity_key = key
        device_id = str(coordinator.data.get("device_id", "unknown"))
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=str(coordinator.data.get("device_name", "HA Kiosk Local")),
            manufacturer=str(coordinator.data.get("manufacturer", "Android")),
            model=str(coordinator.data.get("model", "Tablet")),
            sw_version=f"HA Kiosk Local {coordinator.data.get('app_version', '')}".strip(),
            hw_version=f"Android {coordinator.data.get('android_version', '')}".strip(),
        )
