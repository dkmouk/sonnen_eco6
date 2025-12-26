from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT_DATA,
    CONF_PORT_CTRL,
    CONF_SCAN_INTERVAL,
    CONF_DEVICE_NUM,
    DEFAULT_PORT_DATA,
    DEFAULT_PORT_CTRL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_DEVICE_NUM,
)


class SonnenEco6ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            schema = vol.Schema(
                {
                    vol.Required(CONF_HOST, default="192.168.2.76"): str,
                    vol.Required(CONF_PORT_DATA, default=DEFAULT_PORT_DATA): int,
                    vol.Required(CONF_PORT_CTRL, default=DEFAULT_PORT_CTRL): int,
                    # Optional manual override; if left as default, auto-detect may replace it at runtime.
                    vol.Optional(CONF_DEVICE_NUM, default=DEFAULT_DEVICE_NUM): int,
                    vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
                }
            )
            return self.async_show_form(step_id="user", data_schema=schema)

        await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT_DATA]}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title="SonnenBatterie eco 6.0", data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SonnenEco6OptionsFlowHandler(config_entry)


class SonnenEco6OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is None:
            d = self.config_entry.data
            o = self.config_entry.options
            schema = vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=o.get(CONF_SCAN_INTERVAL, d.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
                    ): int,
                }
            )
            return self.async_show_form(step_id="init", data_schema=schema)

        return self.async_create_entry(title="", data=user_input)
