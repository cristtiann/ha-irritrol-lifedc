"""Config flow for Irritrol LifeDC."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import CONF_ENTITY_PREFIX, DEFAULT_ENTITY_PREFIX, DOMAIN


class IrritrolLifeDCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an Irritrol LifeDC config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            prefix = user_input[CONF_ENTITY_PREFIX].strip()
            await self.async_set_unique_id(prefix)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Irritrol LifeDC", data={CONF_ENTITY_PREFIX: prefix})

        schema = vol.Schema({vol.Required(CONF_ENTITY_PREFIX, default=DEFAULT_ENTITY_PREFIX): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
