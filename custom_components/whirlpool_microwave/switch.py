"""Microwave switches: quiet mode, control lock, turntable."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WhirlpoolMicrowaveConfigEntry
from .coordinator import WhirlpoolMicrowaveCoordinator
from .entity import WhirlpoolMicrowaveEntity
from .microwave import Microwave

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class MicrowaveSwitchDescription(SwitchEntityDescription):
    value_fn: Callable[[Microwave], bool | None]
    set_fn: Callable[[Microwave, bool], Awaitable[bool]]


SWITCHES: tuple[MicrowaveSwitchDescription, ...] = (
    MicrowaveSwitchDescription(
        key="quiet_mode",
        translation_key="quiet_mode",
        value_fn=lambda microwave: microwave.get_quiet_mode(),
        set_fn=lambda microwave, on: microwave.set_quiet_mode(on),
    ),
    MicrowaveSwitchDescription(
        key="control_lock",
        translation_key="control_lock",
        value_fn=lambda microwave: microwave.get_control_lock(),
        set_fn=lambda microwave, on: microwave.set_control_lock(on),
    ),
    MicrowaveSwitchDescription(
        key="turntable",
        translation_key="turntable",
        value_fn=lambda microwave: microwave.get_turntable(),
        set_fn=lambda microwave, on: microwave.set_turntable(on),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WhirlpoolMicrowaveConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(WhirlpoolMicrowaveSwitch(coordinator, desc) for desc in SWITCHES)


class WhirlpoolMicrowaveSwitch(WhirlpoolMicrowaveEntity, SwitchEntity):
    entity_description: MicrowaveSwitchDescription

    def __init__(self, coordinator: WhirlpoolMicrowaveCoordinator, description: MicrowaveSwitchDescription) -> None:
        super().__init__(coordinator, key=description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.microwave)

    async def async_turn_on(self, **kwargs: Any) -> None:
        if not await self.entity_description.set_fn(self.microwave, True):
            raise HomeAssistantError(f"failed to enable {self.entity_description.key}")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if not await self.entity_description.set_fn(self.microwave, False):
            raise HomeAssistantError(f"failed to disable {self.entity_description.key}")
        await self.coordinator.async_request_refresh()
