"""Buttons for HA Kiosk Local."""
from __future__ import annotations
from dataclasses import dataclass
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from .const import DOMAIN
from .coordinator import HAKioskCoordinator
from .entity import HAKioskEntity

@dataclass(frozen=True, kw_only=True)
class D:
    key: str
    name: str
    command: str
    icon: str

BUTTONS = (
    D(key="reload", name="Перезагрузить страницу", command="reload", icon="mdi:reload"),
    D(key="home", name="Открыть домашнюю страницу", command="home", icon="mdi:home"),
    D(key="restart", name="Перезапустить HA Kiosk Local", command="restart", icon="mdi:restart"),
    D(key="reboot_device", name="Перезагрузить планшет / телефон", command="reboot_device", icon="mdi:restart-alert"),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator: HAKioskCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(HAKioskButton(coordinator, description) for description in BUTTONS)

class HAKioskButton(HAKioskEntity, ButtonEntity):
    def __init__(self, coordinator: HAKioskCoordinator, description: D) -> None:
        super().__init__(coordinator, description.key)
        self.description = description
        self._attr_name = description.name
        self._attr_icon = description.icon
    @property
    def available(self) -> bool:
        base = super().available
        if self.description.command == "reboot_device":
            return base and bool(self.coordinator.data.get("device_owner"))
        return base
    async def async_press(self) -> None:
        await self.coordinator.client.async_command(self.description.command)
        if self.description.command not in ("restart", "reboot_device"):
            await self.coordinator.async_request_refresh()
