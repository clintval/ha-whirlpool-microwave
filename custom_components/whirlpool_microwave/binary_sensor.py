"""Microwave binary sensors: door open, running."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WhirlpoolMicrowaveConfigEntry
from .entity import WhirlpoolMicrowaveEntity
from .microwave import Microwave


@dataclass(frozen=True, kw_only=True)
class MicrowaveBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[Microwave], bool | None]


BINARY_SENSORS: tuple[MicrowaveBinarySensorDescription, ...] = (
    MicrowaveBinarySensorDescription(
        key="door",
        translation_key="door",
        device_class=BinarySensorDeviceClass.DOOR,
        value_fn=lambda microwave: microwave.get_door_open(),
    ),
    MicrowaveBinarySensorDescription(
        key="running",
        translation_key="running",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda microwave: microwave.get_running(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WhirlpoolMicrowaveConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        WhirlpoolMicrowaveBinarySensor(coordinator, desc) for desc in BINARY_SENSORS
    )


class WhirlpoolMicrowaveBinarySensor(WhirlpoolMicrowaveEntity, BinarySensorEntity):
    entity_description: MicrowaveBinarySensorDescription

    def __init__(
        self, coordinator, description: MicrowaveBinarySensorDescription
    ) -> None:
        super().__init__(coordinator, key=description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.microwave)
