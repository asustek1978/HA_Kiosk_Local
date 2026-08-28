"""Constants for HA Kiosk."""

from homeassistant.const import Platform

DOMAIN = "ha_kiosk"
PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.BUTTON,
    Platform.TEXT,
    Platform.CAMERA,
    Platform.SELECT,
]

CONF_API_KEY = "api_key"
DEFAULT_PORT = 2323
DEFAULT_SCAN_INTERVAL = 10
