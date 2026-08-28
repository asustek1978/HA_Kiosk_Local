"""Switch entities for HA Kiosk."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from homeassistant.components.switch import SwitchEntity
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
    icon: str
    state_key: str
    on_command: str
    off_command: str

SWITCHES = (
    D(key="screen", name="Экран", icon="mdi:monitor", state_key="screen_on", on_command="screen_on", off_command="screen_off"),
    D(key="camera", name="Камера WebRTC", icon="mdi:camera", state_key="camera_enabled", on_command="camera_on", off_command="camera_off"),
    D(key="camera_microphone", name="Микрофон камеры", icon="mdi:microphone", state_key="microphone_enabled", on_command="microphone_on", off_command="microphone_off"),
    D(key="motion_detection", name="Определение движения", icon="mdi:motion-sensor", state_key="motion_detection", on_command="motion_detection_on", off_command="motion_detection_off"),
    D(key="wake_on_motion", name="Экран по движению", icon="mdi:motion-sensor", state_key="wake_on_motion", on_command="wake_on_motion_on", off_command="wake_on_motion_off"),
    D(key="sound_detection", name="Определение звука", icon="mdi:waveform", state_key="sound_detection", on_command="sound_detection_on", off_command="sound_detection_off"),
    D(key="wake_on_sound", name="Экран по звуку", icon="mdi:volume-high", state_key="wake_on_sound", on_command="wake_on_sound_on", off_command="wake_on_sound_off"),
    D(key="auto_screen_off", name="Автовыключение экрана", icon="mdi:monitor-off", state_key="auto_screen_off", on_command="auto_screen_off_on", off_command="auto_screen_off_off"),
    D(key="light_screen_off", name="Выключать экран в темноте", icon="mdi:brightness-4", state_key="light_screen_off", on_command="light_screen_off_on", off_command="light_screen_off_off"),
    D(key="swipe_reload", name="Reload свайпом", icon="mdi:gesture-swipe-horizontal", state_key="swipe_reload", on_command="swipe_reload_on", off_command="swipe_reload_off"),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator: HAKioskCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(HAKioskSwitch(coordinator, description) for description in SWITCHES)

class HAKioskSwitch(HAKioskEntity, SwitchEntity):
    def __init__(self, coordinator: HAKioskCoordinator, description: D) -> None:
        super().__init__(coordinator, description.key)
        self.description = description
        self._attr_name = description.name
        self._attr_icon = description.icon
    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self.description.state_key)
        return bool(value) if value is not None else None
    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.client.async_command(self.description.on_command)
        await asyncio.sleep(0.2)
        await self.coordinator.async_request_refresh()
    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.async_command(self.description.off_command)
        await asyncio.sleep(0.2)
        await self.coordinator.async_request_refresh()
