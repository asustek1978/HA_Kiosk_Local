"""Select entities for HA Kiosk Local."""
from __future__ import annotations
import asyncio
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from .const import DOMAIN
from .coordinator import HAKioskCoordinator
from .entity import HAKioskEntity

SWIPE_OPTIONS = ["В обе стороны", "Слева направо", "Справа налево"]
SWIPE_TO_VALUE = {"В обе стороны": "both", "Слева направо": "left_to_right", "Справа налево": "right_to_left"}
SWIPE_FROM_VALUE = {value: label for label, value in SWIPE_TO_VALUE.items()}

LIGHT_OPTIONS = ["Авто: lux → камера", "Только датчик lux", "Только камера"]
LIGHT_TO_VALUE = {"Авто: lux → камера": "auto", "Только датчик lux": "lux", "Только камера": "camera"}
LIGHT_FROM_VALUE = {value: label for label, value in LIGHT_TO_VALUE.items()}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator: HAKioskCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [HAKioskSwipeDirection(coordinator)]
    capabilities = coordinator.data.get("api_capabilities", []) or []
    if "light_source" in capabilities:
        entities.append(HAKioskLightSource(coordinator))
    async_add_entities(entities)

class HAKioskSwipeDirection(HAKioskEntity, SelectEntity):
    _attr_name = "Направление свайпа Reload"
    _attr_icon = "mdi:gesture-swipe-horizontal"
    _attr_options = SWIPE_OPTIONS
    def __init__(self, coordinator: HAKioskCoordinator) -> None:
        super().__init__(coordinator, "swipe_direction_select")
    @property
    def current_option(self) -> str | None:
        return SWIPE_FROM_VALUE.get(str(self.coordinator.data.get("swipe_direction", "both")), "В обе стороны")
    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.async_command("swipe_direction", SWIPE_TO_VALUE[option])
        await asyncio.sleep(0.2)
        await self.coordinator.async_request_refresh()

class HAKioskLightSource(HAKioskEntity, SelectEntity):
    _attr_name = "Источник освещённости"
    _attr_icon = "mdi:brightness-auto"
    _attr_options = LIGHT_OPTIONS
    def __init__(self, coordinator: HAKioskCoordinator) -> None:
        super().__init__(coordinator, "light_source_select")
    @property
    def current_option(self) -> str | None:
        return LIGHT_FROM_VALUE.get(str(self.coordinator.data.get("light_source_configured", "auto")), "Авто: lux → камера")
    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.async_command("light_source", LIGHT_TO_VALUE[option])
        await asyncio.sleep(0.4)
        await self.coordinator.async_request_refresh()
