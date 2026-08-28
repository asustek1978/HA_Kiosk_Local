"""Native WebRTC camera for HA Kiosk Local."""

from __future__ import annotations

import base64
import logging

from webrtc_models import RTCIceCandidateInit

from homeassistant.components.camera import (
    Camera,
    CameraEntityFeature,
    WebRTCAnswer,
    WebRTCSendMessage,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import HAKioskApiError
from .const import DOMAIN
from .coordinator import HAKioskCoordinator
from .entity import HAKioskEntity

_LOGGER = logging.getLogger(__name__)

_PLACEHOLDER = base64.b64decode(
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////2wBDAf//////////////////////////////////////////////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIQAxAAAAH/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAEFAqf/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAEDAQE/AYf/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAECAQE/AYf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAY/Aqf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAE/IV//2gAMAwEAAgADAAAAEP/EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQMBAT8QH//EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQIBAT8QH//EABQQAQAAAAAAAAAAAAAAAAAAABD/2gAIAQEAAT8QH//Z"
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: HAKioskCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HAKioskCamera(coordinator)])


class HAKioskCamera(HAKioskEntity, Camera):
    """Tablet camera streamed directly to the HA frontend with WebRTC."""

    _attr_name = "Камера планшета"
    _attr_icon = "mdi:tablet-cellphone"
    _attr_supported_features = CameraEntityFeature.STREAM | CameraEntityFeature.ON_OFF

    def __init__(self, coordinator: HAKioskCoordinator) -> None:
        Camera.__init__(self)
        HAKioskEntity.__init__(self, coordinator, "camera")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("camera_enabled", True))

    @property
    def is_streaming(self) -> bool:
        return bool(self.coordinator.data.get("camera_streaming", False))

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        return _PLACEHOLDER

    async def async_turn_on(self) -> None:
        await self.coordinator.client.async_command("camera_on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        await self.coordinator.client.async_command("camera_off")
        await self.coordinator.async_request_refresh()

    async def async_handle_async_webrtc_offer(
        self,
        offer_sdp: str,
        session_id: str,
        send_message: WebRTCSendMessage,
    ) -> None:
        try:
            answer_sdp = await self.coordinator.client.async_webrtc_offer(session_id, offer_sdp)
        except HAKioskApiError as err:
            raise HomeAssistantError(f"HA Kiosk Local WebRTC: {err}") from err
        send_message(WebRTCAnswer(answer_sdp))

    async def async_on_webrtc_candidate(
        self,
        session_id: str,
        candidate: RTCIceCandidateInit,
    ) -> None:
        await self.coordinator.client.async_webrtc_candidate(
            session_id,
            candidate.candidate,
            candidate.sdp_mid,
            candidate.sdp_m_line_index,
        )

    @callback
    def close_webrtc_session(self, session_id: str) -> None:
        self.hass.async_create_task(self.coordinator.client.async_webrtc_close(session_id))
