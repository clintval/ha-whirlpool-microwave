"""Config flow for the Whirlpool Microwave integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from whirlpool.auth import Auth
from whirlpool.backendselector import BackendSelector, Brand, Region

from .const import CONF_BRAND, CONF_REGION, DEFAULT_BRAND, DEFAULT_REGION, DOMAIN

REGIONS = [region.name for region in Region]
BRANDS = [brand.name for brand in Brand]


class WhirlpoolMicrowaveConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single-step credential flow that locates the Cooking appliance."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            backend = BackendSelector(
                getattr(Brand, user_input[CONF_BRAND]),
                getattr(Region, user_input[CONF_REGION]),
            )
            auth = Auth(backend, user_input[CONF_EMAIL], user_input[CONF_PASSWORD], session)
            try:
                await auth.do_auth(store=False)
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                if not auth.is_access_token_valid():
                    errors["base"] = "invalid_auth"
                else:
                    appliance = await self._find_cooking(session, backend, auth)
                    if appliance is None:
                        errors["base"] = "no_appliance"
                    else:
                        await self.async_set_unique_id(appliance["SAID"])
                        self._abort_if_unique_id_configured()
                        return self.async_create_entry(
                            title=appliance["APPLIANCE_NAME"],
                            data={
                                CONF_EMAIL: user_input[CONF_EMAIL],
                                CONF_PASSWORD: user_input[CONF_PASSWORD],
                                CONF_REGION: user_input[CONF_REGION],
                                CONF_BRAND: user_input[CONF_BRAND],
                                "said": appliance["SAID"],
                                "name": appliance["APPLIANCE_NAME"],
                                "model": appliance.get("MODEL_NO", ""),
                                "data_model": appliance["DATA_MODEL_KEY"],
                            },
                        )

        schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_REGION, default=DEFAULT_REGION): vol.In(REGIONS),
                vol.Required(CONF_BRAND, default=DEFAULT_BRAND): vol.In(BRANDS),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def _find_cooking(self, session, backend, auth):
        """Find the first Cooking appliance on the account; returns None if not found."""
        account_id = await auth.get_account_id()
        if not account_id:
            return None
        url = backend.get_owned_appliances_url(account_id)
        async with session.get(url, headers=auth.create_headers()) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
        for location in data.get(str(account_id), {}).values():
            for appliance in location:
                if appliance.get("CATEGORY_NAME") == "Cooking":
                    return appliance
        return None
