"""Polling coordinator for the Whirlpool Microwave."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .microwave import Microwave

_LOGGER = logging.getLogger(__name__)


class WhirlpoolMicrowaveCoordinator(DataUpdateCoordinator[None]):
    """Refreshes the microwave's attribute payload on an interval."""

    def __init__(self, hass: HomeAssistant, microwave: Microwave, model: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.microwave = microwave
        self.model = model

    async def _async_update_data(self) -> None:
        try:
            ok = await self.microwave.fetch_data()
        except Exception as err:  # noqa: BLE001 - surface any client error as UpdateFailed
            raise UpdateFailed(f"error fetching microwave data: {err}") from err
        if not ok:
            raise UpdateFailed("microwave fetch_data returned False")
