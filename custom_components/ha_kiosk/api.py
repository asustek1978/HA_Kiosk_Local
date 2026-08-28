"""Local HTTP API client for HA Kiosk Local."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession


class HAKioskApiError(Exception):
    """Base HA Kiosk Local API error."""


class HAKioskAuthError(HAKioskApiError):
    """Invalid API key."""


class HAKioskConnectionError(HAKioskApiError):
    """Cannot connect to HA Kiosk Local."""


class HAKioskApi:
    """Client for one HA Kiosk Local tablet."""

    def __init__(self, session: ClientSession, host: str, port: int, api_key: str) -> None:
        self._session = session
        self.host = host.strip().strip("/")
        self.port = int(port)
        self.api_key = api_key.strip()

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def headers(self) -> dict[str, str]:
        return {"X-HA-Kiosk-Key": self.api_key}

    async def async_status(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(6):
                async with self._session.get(
                    f"{self.base_url}/api/status",
                    headers=self.headers,
                ) as response:
                    if response.status == 401:
                        raise HAKioskAuthError("Invalid API key")
                    response.raise_for_status()
                    data = await response.json(content_type=None)
                    if not data.get("ok"):
                        raise HAKioskApiError("Device returned not ok")
                    return data
        except HAKioskAuthError:
            raise
        except (TimeoutError, ClientError, ClientResponseError, ValueError) as err:
            raise HAKioskConnectionError(str(err)) from err

    async def async_command(self, command: str, value: str | int | None = None) -> dict[str, Any]:
        params: dict[str, str] = {"command": command}
        if value is not None:
            params["value"] = str(value)
        try:
            async with asyncio.timeout(6):
                async with self._session.post(
                    f"{self.base_url}/api/command",
                    headers=self.headers,
                    params=params,
                ) as response:
                    if response.status == 401:
                        raise HAKioskAuthError("Invalid API key")
                    data = await response.json(content_type=None)
                    if response.status >= 400 or not data.get("ok"):
                        raise HAKioskApiError(data.get("message") or f"HTTP {response.status}")
                    return data
        except (HAKioskAuthError, HAKioskApiError):
            raise
        except (TimeoutError, ClientError, ClientResponseError, ValueError) as err:
            raise HAKioskConnectionError(str(err)) from err

    async def async_webrtc_offer(self, session_id: str, sdp: str) -> str:
        payload = {"session_id": session_id, "sdp": sdp}
        try:
            async with asyncio.timeout(18):
                async with self._session.post(
                    f"{self.base_url}/api/webrtc/offer",
                    headers=self.headers,
                    json=payload,
                ) as response:
                    if response.status == 401:
                        raise HAKioskAuthError("Invalid API key")
                    data = await response.json(content_type=None)
                    if response.status >= 400 or not data.get("ok"):
                        raise HAKioskApiError(data.get("error") or f"HTTP {response.status}")
                    return str(data["sdp"])
        except (HAKioskAuthError, HAKioskApiError):
            raise
        except (TimeoutError, ClientError, ClientResponseError, ValueError, KeyError) as err:
            raise HAKioskConnectionError(str(err)) from err

    async def async_webrtc_candidate(
        self,
        session_id: str,
        candidate: str,
        sdp_mid: str | None,
        sdp_m_line_index: int | None,
    ) -> None:
        payload = {
            "session_id": session_id,
            "candidate": candidate,
            "sdp_mid": sdp_mid,
            "sdp_m_line_index": sdp_m_line_index if sdp_m_line_index is not None else 0,
        }
        try:
            async with asyncio.timeout(6):
                async with self._session.post(
                    f"{self.base_url}/api/webrtc/candidate",
                    headers=self.headers,
                    json=payload,
                ) as response:
                    if response.status == 401:
                        raise HAKioskAuthError("Invalid API key")
                    data = await response.json(content_type=None)
                    if response.status >= 400 or not data.get("ok"):
                        raise HAKioskApiError(data.get("error") or f"HTTP {response.status}")
        except (HAKioskAuthError, HAKioskApiError):
            raise
        except (TimeoutError, ClientError, ClientResponseError, ValueError) as err:
            raise HAKioskConnectionError(str(err)) from err

    async def async_webrtc_close(self, session_id: str) -> None:
        try:
            async with asyncio.timeout(4):
                async with self._session.post(
                    f"{self.base_url}/api/webrtc/close",
                    headers=self.headers,
                    json={"session_id": session_id},
                ):
                    return
        except (TimeoutError, ClientError):
            return
