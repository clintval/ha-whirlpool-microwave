"""Whirlpool Microwave custom integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from whirlpool.appliance import Appliance  # noqa: F401 - ensures library import is valid
from whirlpool.auth import Auth
from whirlpool.backendselector import BackendSelector, Brand, Region
from whirlpool.types import ApplianceInfo

from .const import CONF_BRAND, CONF_REGION
from .coordinator import WhirlpoolMicrowaveCoordinator
from .microwave import Microwave

_LOGGER = logging.getLogger(__name__)

# platform tasks (light, fan, switch, binary_sensor, sensor) append their Platform here as each is added
PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.FAN]

type WhirlpoolMicrowaveConfigEntry = ConfigEntry[WhirlpoolMicrowaveCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: WhirlpoolMicrowaveConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    backend = BackendSelector(
        getattr(Brand, entry.data[CONF_BRAND]),
        getattr(Region, entry.data[CONF_REGION]),
    )
    auth = Auth(backend, entry.data[CONF_EMAIL], entry.data[CONF_PASSWORD], session)
    try:
        await auth.do_auth(store=False)
    except Exception as err:  # noqa: BLE001
        raise ConfigEntryNotReady(f"could not reach Whirlpool cloud: {err}") from err
    if not auth.is_access_token_valid():
        raise ConfigEntryAuthFailed("invalid Whirlpool credentials")

    info = ApplianceInfo(
        said=entry.data["said"],
        name=entry.data["name"],
        data_model=entry.data["data_model"],
        category="Cooking",
        model_number=entry.data["model"],
        serial_number="",
    )
    microwave = Microwave(backend, auth, session, info)
    coordinator = WhirlpoolMicrowaveCoordinator(hass, microwave, entry.data["model"])
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: WhirlpoolMicrowaveConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
