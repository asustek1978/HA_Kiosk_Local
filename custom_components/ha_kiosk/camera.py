"""Camera entities for HA Kiosk Local.

The primary camera path in v0.3.4.1.4 intentionally follows the same transport
model as Home Assistant's Fully Kiosk Browser camera:

    tablet MJPEG (LAN only) -> Home Assistant camera proxy -> browser

The browser connects only to Home Assistant, so the primary camera works both
locally and remotely without exposing the tablet API or camera ports to the
Internet. RTSP/H.264/AAC and direct WebRTC are retained as disabled-by-default
secondary entities for diagnostics and optional local use.
"""

from __future__ import annotations

import asyncio
import base64
from urllib.parse import quote

from aiohttp import web
from webrtc_models import RTCIceCandidateInit

from homeassistant.components.camera import (
    Camera,
    CameraEntityFeature,
    StreamType,
    WebRTCAnswer,
    WebRTCSendMessage,
)
from homeassistant.components.web_rtc import async_get_ice_servers
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_aiohttp_proxy_stream, async_get_clientsession
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import HAKioskApiError
from .const import DOMAIN
from .coordinator import HAKioskCoordinator
from .entity import HAKioskEntity

_PLACEHOLDER = base64.b64decode(
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////2wBDAf//////////////////////////////////////////////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIQAxAAAAH/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAEFAqf/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAEDAQE/AYf/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAECAQE/AYf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAY/Aqf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAE/IV//2gAMAwEAAgADAAAAEP/EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQMBAT8QH//EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQIBAT8QH//EABQQAQAAAAAAAAAAAAAAAAAAABD/2gAIAQEAAT8QH//Z"
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: HAKioskCoordinator = hass.data[DOMAIN][entry.entry_id]
    capabilities = coordinator.data.get("api_capabilities", []) or []

    if "camera_rtsp" in capabilities:
        # The primary camera intentionally does not advertise STREAM. Home Assistant
        # therefore serves it through its authenticated MJPEG camera proxy, matching
        # the Fully Kiosk Browser transport model.
        #
        # Android v0.3.4.1.x already exposes /api/camera/mjpeg even though its newer
        # capability list primarily advertises camera_rtsp.
        #
        # RTSP and direct WebRTC remain disabled-by-default secondary entities so
        # they cannot change the transport selected for the primary camera.
        async_add_entities(
            [
                HAKioskRelayCamera(coordinator),
                HAKioskRtspCamera(coordinator, secondary=True),
                HAKioskDirectCamera(coordinator, secondary=True),
            ]
        )
    elif "camera_mjpeg_relay" in capabilities:
        async_add_entities(
            [
                HAKioskRelayCamera(coordinator),
                HAKioskDirectCamera(coordinator, secondary=True),
            ]
        )
    else:
        async_add_entities([HAKioskDirectCamera(coordinator)])


class HAKioskCameraBase(HAKioskEntity, Camera):
    """Common HA Kiosk Local camera behavior."""

    _attr_name = "Камера планшета"
    _attr_icon = "mdi:tablet-cellphone"
    _attr_supported_features = CameraEntityFeature.STREAM | CameraEntityFeature.ON_OFF

    def __init__(
        self,
        coordinator: HAKioskCoordinator,
        *,
        entity_key: str = "camera",
        entity_name: str = "Камера планшета",
    ) -> None:
        Camera.__init__(self)
        HAKioskEntity.__init__(self, coordinator, entity_key)
        self._attr_name = entity_name

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("camera_enabled", True))

    @property
    def is_streaming(self) -> bool:
        return bool(self.coordinator.data.get("camera_streaming", False))

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        # Do not claim the camera hardware for periodic dashboard thumbnails.
        return _PLACEHOLDER

    async def async_turn_on(self) -> None:
        await self.coordinator.client.async_command("camera_on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        await self.coordinator.client.async_command("camera_off")
        await self.coordinator.async_request_refresh()


class HAKioskRtspCamera(HAKioskCameraBase):
    """Optional H.264/AAC camera ingested by Home Assistant over the LAN."""

    _attr_frontend_stream_type = StreamType.HLS

    def __init__(self, coordinator: HAKioskCoordinator, *, secondary: bool = False) -> None:
        super().__init__(
            coordinator,
            entity_key="camera_rtsp" if secondary else "camera",
            entity_name="Камера планшета — RTSP" if secondary else "Камера планшета",
        )
        if secondary:
            self._attr_entity_registry_enabled_default = False

    async def stream_source(self) -> str | None:
        if not self.is_on:
            return None

        try:
            # go2rtc can keep its RTSP producer connected after the frontend viewer
            # has already been closed. On some Android/MediaCodec combinations that
            # long-lived producer eventually stops yielding usable video even though
            # both sides still report the connection as alive.
            #
            # Recreate only the tablet RTSP producer whenever a new stream source is
            # requested. This avoids requiring a full kiosk-app restart.
            try:
                await self.coordinator.client.async_command("camera_rtsp_stop")
            except HAKioskApiError:
                pass

            await asyncio.sleep(0.30)

            result = await self.coordinator.client.async_command("camera_rtsp_start")
            if not result.get("ok", False):
                return None

            await asyncio.sleep(0.45)
            status = await self.coordinator.client.async_status()
        except HAKioskApiError as err:
            raise HomeAssistantError(f"HA Kiosk Local RTSP: {err}") from err

        port = int(status.get("camera_rtsp_port") or 8554)
        return f"rtsp://{self.coordinator.client.host}:{port}/"

    async def async_turn_off(self) -> None:
        try:
            await self.coordinator.client.async_command("camera_rtsp_stop")
        except HAKioskApiError:
            pass
        await super().async_turn_off()


class HAKioskRelayCamera(HAKioskCameraBase):
    """Primary HA-proxied MJPEG camera.

    This intentionally mirrors the transport model used by Home Assistant's
    Fully Kiosk Browser camera: the entity does not advertise STREAM, so the
    frontend falls back to the authenticated Home Assistant MJPEG proxy.
    The browser never needs to reach the tablet directly.
    """

    _attr_supported_features = CameraEntityFeature.ON_OFF

    def _mjpeg_url(self) -> str:
        client = self.coordinator.client
        api_key = quote(client.api_key, safe="")
        return f"http://{client.host}:{client.port}/api/camera/mjpeg?key={api_key}"

    async def stream_source(self) -> str | None:
        return self._mjpeg_url() if self.is_on else None

    async def handle_async_mjpeg_stream(
        self, request: web.Request
    ) -> web.StreamResponse | None:
        if not self.is_on:
            return None

        session = async_get_clientsession(self.hass)
        response = await session.get(
            self._mjpeg_url(),
            headers=self.coordinator.client.headers,
            timeout=None,
        )
        if response.status != 200:
            response.close()
            return None

        content_type = response.headers.get(
            "Content-Type", "multipart/x-mixed-replace; boundary=ha-kiosk-frame"
        )
        try:
            return await async_aiohttp_proxy_stream(
                self.hass,
                request,
                response.content,
                content_type,
            )
        finally:
            response.close()


class HAKioskDirectCamera(HAKioskCameraBase):
    """Direct browser-to-tablet WebRTC fallback for local low-latency viewing."""

    def __init__(self, coordinator: HAKioskCoordinator, *, secondary: bool = False) -> None:
        super().__init__(
            coordinator,
            entity_key="camera_direct" if secondary else "camera",
            entity_name="Камера планшета — Direct WebRTC" if secondary else "Камера планшета",
        )
        if secondary:
            self._attr_entity_registry_enabled_default = False

    async def async_handle_async_webrtc_offer(
        self,
        offer_sdp: str,
        session_id: str,
        send_message: WebRTCSendMessage,
    ) -> None:
        try:
            ice_servers = [server.to_dict() for server in async_get_ice_servers(self.hass)]
            answer_sdp = await self.coordinator.client.async_webrtc_offer(
                session_id, offer_sdp, ice_servers
            )
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
