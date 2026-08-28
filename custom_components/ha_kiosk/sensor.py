"""Sensors for HA Kiosk Local."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, SIGNAL_STRENGTH_DECIBELS_MILLIWATT, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import HAKioskCoordinator
from .entity import HAKioskEntity


@dataclass(frozen=True, kw_only=True)
class HAKioskSensorDescription:
    key: str
    name: str
    icon: str | None = None
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    precision: int | None = None


M = SensorStateClass.MEASUREMENT
SENSORS = (
    HAKioskSensorDescription(key="battery_level", name="Уровень батареи", icon="mdi:battery", unit=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=M),
    HAKioskSensorDescription(key="battery_voltage_v", name="Напряжение аккумулятора", icon="mdi:sine-wave", unit="V", state_class=M, precision=3),
    HAKioskSensorDescription(key="battery_current_ma", name="Ток аккумулятора", icon="mdi:current-dc", unit="mA", state_class=M, precision=0),
    HAKioskSensorDescription(key="battery_current_average_ma", name="Средний ток аккумулятора", icon="mdi:current-dc", unit="mA", state_class=M, precision=0),
    HAKioskSensorDescription(key="battery_power_w", name="Мощность аккумулятора", icon="mdi:flash", unit="W", state_class=M, precision=2),
    HAKioskSensorDescription(key="battery_load_w", name="Нагрузка аккумулятора", icon="mdi:gauge", unit="W", state_class=M, precision=2),
    HAKioskSensorDescription(key="battery_temperature_c", name="Температура аккумулятора", icon="mdi:thermometer", unit="°C", state_class=M, precision=1),
    HAKioskSensorDescription(key="battery_charge_counter_mah", name="Остаток заряда аккумулятора", icon="mdi:battery-clock", unit="mAh", state_class=M, precision=0),
    HAKioskSensorDescription(key="battery_energy_remaining_wh", name="Остаток энергии аккумулятора", icon="mdi:battery-heart-variant", unit="Wh", state_class=M, precision=2),
    HAKioskSensorDescription(key="battery_status", name="Состояние аккумулятора", icon="mdi:battery-sync"),
    HAKioskSensorDescription(key="battery_health", name="Состояние здоровья аккумулятора", icon="mdi:battery-heart"),
    HAKioskSensorDescription(key="charge_source", name="Источник зарядки", icon="mdi:power-plug"),
    HAKioskSensorDescription(key="battery_rate_percent_per_hour", name="Скорость заряда/разряда", icon="mdi:chart-timeline-variant", unit="%/ч", state_class=M, precision=2),
    HAKioskSensorDescription(key="battery_estimated_hours", name="Оценка времени аккумулятора", icon="mdi:timer-sand", unit="h", state_class=M, precision=1),

    HAKioskSensorDescription(key="wifi_rssi", name="Wi-Fi сигнал", icon="mdi:wifi", unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT, state_class=M),
    HAKioskSensorDescription(key="ip_address", name="IP-адрес", icon="mdi:ip-network"),
    HAKioskSensorDescription(key="current_url", name="Текущий URL", icon="mdi:web"),
    HAKioskSensorDescription(key="android_version", name="Android", icon="mdi:android"),
    HAKioskSensorDescription(key="app_version", name="Версия HA Kiosk Local", icon="mdi:information-outline"),
    HAKioskSensorDescription(key="uptime_seconds", name="Время работы планшета", icon="mdi:timer-outline", unit=UnitOfTime.SECONDS, device_class=SensorDeviceClass.DURATION, state_class=M),

    HAKioskSensorDescription(key="ram_total_mb", name="RAM всего", icon="mdi:memory", unit="MB", state_class=M, precision=0),
    HAKioskSensorDescription(key="ram_available_mb", name="RAM доступно", icon="mdi:memory", unit="MB", state_class=M, precision=0),
    HAKioskSensorDescription(key="ram_used_mb", name="RAM занято", icon="mdi:memory", unit="MB", state_class=M, precision=0),
    HAKioskSensorDescription(key="ram_used_percent", name="Использование RAM", icon="mdi:memory", unit=PERCENTAGE, state_class=M, precision=1),
    HAKioskSensorDescription(key="app_memory_pss_mb", name="Память HA Kiosk Local", icon="mdi:application-braces", unit="MB", state_class=M, precision=1),
    HAKioskSensorDescription(key="swap_total_mb", name="Swap / zRAM всего", icon="mdi:swap-horizontal", unit="MB", state_class=M, precision=0),
    HAKioskSensorDescription(key="swap_used_mb", name="Swap / zRAM занято", icon="mdi:swap-horizontal-bold", unit="MB", state_class=M, precision=0),
    HAKioskSensorDescription(key="swap_used_percent", name="Использование Swap / zRAM", icon="mdi:swap-horizontal", unit=PERCENTAGE, state_class=M, precision=1),
    HAKioskSensorDescription(key="virtual_memory_total_mb", name="Виртуальная память всего", icon="mdi:database-cog", unit="MB", state_class=M, precision=0),
    HAKioskSensorDescription(key="virtual_memory_used_mb", name="Виртуальная память занято", icon="mdi:database", unit="MB", state_class=M, precision=0),
    HAKioskSensorDescription(key="virtual_memory_used_percent", name="Использование виртуальной памяти", icon="mdi:database-eye", unit=PERCENTAGE, state_class=M, precision=1),
    HAKioskSensorDescription(key="zram_size_mb", name="Размер zRAM", icon="mdi:archive-cog", unit="MB", state_class=M, precision=0),
    HAKioskSensorDescription(key="cpu_usage_percent", name="Загрузка CPU", icon="mdi:cpu-64-bit", unit=PERCENTAGE, state_class=M, precision=1),
    HAKioskSensorDescription(key="cpu_temperature_c", name="Температура CPU", icon="mdi:thermometer", unit="°C", state_class=M, precision=1),

    HAKioskSensorDescription(key="camera_facing", name="Выбранная камера", icon="mdi:camera-switch"),
    HAKioskSensorDescription(key="webrtc_sessions", name="WebRTC подключения", icon="mdi:video-wireless-outline", state_class=M),
    HAKioskSensorDescription(key="camera_last_error", name="Последняя ошибка камеры", icon="mdi:alert-circle-outline"),
    HAKioskSensorDescription(key="motion_score", name="Уровень движения", icon="mdi:motion-sensor", unit=PERCENTAGE, state_class=M, precision=1),
    HAKioskSensorDescription(key="sound_level_db", name="Уровень звука", icon="mdi:waveform", unit="dB", state_class=M, precision=1),
    HAKioskSensorDescription(key="ambient_light_lux", name="Освещённость", icon="mdi:brightness-5", unit="lx", device_class=SensorDeviceClass.ILLUMINANCE, state_class=M, precision=1),
    HAKioskSensorDescription(key="camera_light_percent", name="Уровень света по камере", icon="mdi:camera-metering-matrix", unit=PERCENTAGE, state_class=M, precision=1),
    HAKioskSensorDescription(key="light_source_active", name="Активный источник освещённости", icon="mdi:brightness-auto"),
    HAKioskSensorDescription(key="last_presence_source", name="Последняя активность", icon="mdi:account-clock"),
    HAKioskSensorDescription(key="presence_seconds_ago", name="С последней активности", icon="mdi:timer-sand", unit=UnitOfTime.SECONDS, device_class=SensorDeviceClass.DURATION, state_class=M, precision=0),
    HAKioskSensorDescription(key="swipe_direction", name="Направление свайпа Reload", icon="mdi:gesture-swipe-horizontal"),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator: HAKioskCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(HAKioskSensor(coordinator, description) for description in SENSORS)


class HAKioskSensor(HAKioskEntity, SensorEntity):
    def __init__(self, coordinator: HAKioskCoordinator, description: HAKioskSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.description = description
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_suggested_display_precision = description.precision

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get(self.description.key)
