"""Hood exhaust fan modeled as a 4-speed percentage fan."""
from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from . import WhirlpoolMicrowaveConfigEntry
from .const import FAN_ORDERED
from .entity import WhirlpoolMicrowaveEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WhirlpoolMicrowaveConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([WhirlpoolMicrowaveFan(entry.runtime_data)])


class WhirlpoolMicrowaveFan(WhirlpoolMicrowaveEntity, FanEntity):
    _attr_translation_key = "hood_fan"
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
    _attr_speed_count = len(FAN_ORDERED)

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, key="fan")

    @property
    def is_on(self) -> bool | None:
        speed = self.microwave.get_fan_speed()
        return None if speed is None else speed != "off"

    @property
    def percentage(self) -> int | None:
        speed = self.microwave.get_fan_speed()
        if speed is None or speed == "off":
            return 0
        return ordered_list_item_to_percentage(FAN_ORDERED, speed)

    async def async_set_percentage(self, percentage: int) -> None:
        speed = "off" if percentage == 0 else percentage_to_ordered_list_item(FAN_ORDERED, percentage)
        if not await self.microwave.set_fan_speed(speed):
            raise HomeAssistantError("failed to set hood fan speed")
        await self.coordinator.async_request_refresh()

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        if percentage is None:
            percentage = ordered_list_item_to_percentage(FAN_ORDERED, "high")
        await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_set_percentage(0)
