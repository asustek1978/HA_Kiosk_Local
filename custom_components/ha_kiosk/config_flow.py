"""Config flow for HA Kiosk Local."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HAKioskApi, HAKioskAuthError, HAKioskConnectionError
from .const import CONF_API_KEY, DEFAULT_PORT, DOMAIN


class HAKioskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Kiosk Local."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input[CONF_PORT])
            api_key = str(user_input[CONF_API_KEY]).strip()
            client = HAKioskApi(async_get_clientsession(self.hass), host, port, api_key)

            try:
                status = await client.async_status()
            except HAKioskAuthError:
                errors["base"] = "invalid_auth"
            except HAKioskConnectionError:
                errors["base"] = "cannot_connect"
            else:
                device_id = str(status.get("device_id") or f"{host}:{port}")
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=str(status.get("device_name") or "HA Kiosk Local"),
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_API_KEY: api_key,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(int), vol.Range(min=1024, max=65535)),
                vol.Required(CONF_API_KEY): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
