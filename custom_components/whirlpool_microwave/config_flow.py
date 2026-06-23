"""Config flow for the Whirlpool Microwave integration (stub; full implementation is a later task)."""
from __future__ import annotations

from homeassistant.config_entries import ConfigFlow

from .const import DOMAIN


class WhirlpoolMicrowaveConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whirlpool Microwave."""

    VERSION = 1
