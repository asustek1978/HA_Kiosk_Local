"""Data coordinator for HA Kiosk Local."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HAKioskApi, HAKioskApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class HAKioskCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate polling of one tablet."""

    def __init__(self, hass: HomeAssistant, client: HAKioskApi) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_status()
        except HAKioskApiError as err:
            raise UpdateFailed(f"HA Kiosk Local API error: {err}") from err
