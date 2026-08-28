"""Number entities for HA Kiosk."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
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
    command: str
    minimum: float
    maximum: float
    step: float
    unit: str | None = None

NUMBERS = (
    D(key="brightness", name="Яркость", icon="mdi:brightness-6", state_key="screen_brightness", command="brightness", minimum=0, maximum=100, step=1, unit=PERCENTAGE),
    D(key="motion_sensitivity", name="Чувствительность движения", icon="mdi:motion-sensor", state_key="motion_sensitivity", command="motion_sensitivity", minimum=0, maximum=100, step=1, unit=PERCENTAGE),
    D(key="sound_sensitivity", name="Чувствительность звука", icon="mdi:waveform", state_key="sound_sensitivity", command="sound_sensitivity", minimum=0, maximum=100, step=1, unit=PERCENTAGE),
    D(key="inactivity_timeout", name="Таймер выключения экрана", icon="mdi:timer-outline", state_key="inactivity_timeout_seconds", command="inactivity_timeout", minimum=30, maximum=7200, step=30, unit=UnitOfTime.SECONDS),
    D(key="light_threshold", name="Порог темноты — lux", icon="mdi:brightness-5", state_key="light_threshold_lux", command="light_threshold", minimum=0, maximum=1000, step=1, unit="lx"),
    D(key="camera_light_threshold", name="Порог темноты — камера", icon="mdi:camera-metering-matrix", state_key="camera_light_threshold_percent", command="camera_light_threshold", minimum=0, maximum=100, step=1, unit=PERCENTAGE),
    D(key="light_off_delay", name="Задержка выключения в темноте", icon="mdi:timer-outline", state_key="light_off_delay_seconds", command="light_off_delay", minimum=5, maximum=600, step=5, unit=UnitOfTime.SECONDS),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator: HAKioskCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(HAKioskNumber(coordinator, description) for description in NUMBERS)

class HAKioskNumber(HAKioskEntity, NumberEntity):
    _attr_mode = NumberMode.SLIDER
    def __init__(self, coordinator: HAKioskCoordinator, description: D) -> None:
        super().__init__(coordinator, description.key)
        self.description = description
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_native_min_value = description.minimum
        self._attr_native_max_value = description.maximum
        self._attr_native_step = description.step
        self._attr_native_unit_of_measurement = description.unit
    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get(self.description.state_key)
        return float(value) if value is not None else None
    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.async_command(self.description.command, round(value))
        await asyncio.sleep(0.2)
        await self.coordinator.async_request_refresh()
