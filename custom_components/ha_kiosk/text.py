"""Text entity for opening a URL in HA Kiosk Local."""

from __future__ import annotations

import asyncio

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import HAKioskCoordinator
from .entity import HAKioskEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: HAKioskCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HAKioskUrlText(coordinator)])


class HAKioskUrlText(HAKioskEntity, TextEntity):
    """Current URL and remote URL loader."""

    _attr_name = "Открыть URL"
    _attr_icon = "mdi:web"
    _attr_mode = TextMode.TEXT
    _attr_native_min = 1
    _attr_native_max = 1024

    def __init__(self, coordinator: HAKioskCoordinator) -> None:
        super().__init__(coordinator, "open_url")

    @property
    def native_value(self) -> str | None:
        value = self.coordinator.data.get("current_url")
        return str(value) if value else None

    async def async_set_value(self, value: str) -> None:
        await self.coordinator.client.async_command("load_url", value)
        await asyncio.sleep(0.3)
        await self.coordinator.async_request_refresh()
