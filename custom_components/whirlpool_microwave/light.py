"""Hood surface light (Off / Low / High) modeled as a brightness light."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WhirlpoolMicrowaveConfigEntry
from .coordinator import WhirlpoolMicrowaveCoordinator
from .entity import WhirlpoolMicrowaveEntity

PARALLEL_UPDATES = 1

LEVEL_BRIGHTNESS = {"low": 128, "high": 255}
BRIGHTNESS_BOUNDARY = 191  # <= boundary -> low, above -> high


def level_to_brightness(level: str | None) -> int | None:
    return LEVEL_BRIGHTNESS.get(level or "")


def brightness_to_level(brightness: int) -> str:
    return "low" if brightness <= BRIGHTNESS_BOUNDARY else "high"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WhirlpoolMicrowaveConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([WhirlpoolMicrowaveLight(entry.runtime_data)])


class WhirlpoolMicrowaveLight(WhirlpoolMicrowaveEntity, LightEntity):
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_translation_key = "hood_light"

    def __init__(self, coordinator: WhirlpoolMicrowaveCoordinator) -> None:
        super().__init__(coordinator, key="light")
        self._last_on_level = "high"

    @property
    def is_on(self) -> bool | None:
        level = self.microwave.get_light_level()
        return None if level is None else level != "off"

    @property
    def brightness(self) -> int | None:
        return level_to_brightness(self.microwave.get_light_level())

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            level = brightness_to_level(kwargs[ATTR_BRIGHTNESS])
        else:
            level = self._last_on_level
        self._last_on_level = level
        if not await self.microwave.set_light_level(level):
            raise HomeAssistantError("failed to set hood light")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if not await self.microwave.set_light_level("off"):
            raise HomeAssistantError("failed to turn off hood light")
        await self.coordinator.async_request_refresh()
