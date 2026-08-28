"""Binary sensors for HA Kiosk."""
from __future__ import annotations
from dataclasses import dataclass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
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
    icon: str | None = None
    device_class: BinarySensorDeviceClass | None = None

BINARY_SENSORS = (
    D(key="charging", name="Зарядка", icon="mdi:battery-charging", device_class=BinarySensorDeviceClass.BATTERY_CHARGING),
    D(key="screen_on", name="Экран включён", icon="mdi:monitor"),
    D(key="kiosk_home", name="HA Kiosk — главный экран", icon="mdi:home-lock"),
    D(key="device_admin", name="Управление экраном разрешено", icon="mdi:shield-lock"),
    D(key="device_owner", name="Device Owner", icon="mdi:shield-crown"),
    D(key="camera_permission", name="Разрешение камеры", icon="mdi:camera-lock-open"),
    D(key="microphone_permission", name="Разрешение микрофона", icon="mdi:microphone-settings"),
    D(key="camera_streaming", name="Камера передаёт видео", icon="mdi:video-wireless"),
    D(key="presence_monitor_running", name="Монитор присутствия", icon="mdi:motion-sensor"),
    D(key="presence_paused_for_webrtc", name="Монитор приостановлен для WebRTC", icon="mdi:pause-circle"),
    D(key="motion_detected", name="Обнаружено движение", icon="mdi:motion-sensor"),
    D(key="sound_detected", name="Обнаружен звук", icon="mdi:waveform"),
    D(key="presence_active", name="Есть активность", icon="mdi:account-check"),
    D(key="light_sensor_available", name="Датчик освещённости доступен", icon="mdi:brightness-auto"),
    D(key="ambient_dark", name="Темно", icon="mdi:weather-night"),
    D(key="memory_low", name="Android сообщает о нехватке памяти", icon="mdi:memory-arrow-down"),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator: HAKioskCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(HAKioskBinarySensor(coordinator, description) for description in BINARY_SENSORS)

class HAKioskBinarySensor(HAKioskEntity, BinarySensorEntity):
    def __init__(self, coordinator: HAKioskCoordinator, description: D) -> None:
        super().__init__(coordinator, description.key)
        self.description = description
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_device_class = description.device_class
    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self.description.key)
        return bool(value) if value is not None else None
