"""Microwave sensors: cook time remaining."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WhirlpoolMicrowaveConfigEntry
from .entity import WhirlpoolMicrowaveEntity
from .microwave import Microwave


@dataclass(frozen=True, kw_only=True)
class MicrowaveSensorDescription(SensorEntityDescription):
    value_fn: Callable[[Microwave], int | None]


SENSORS: tuple[MicrowaveSensorDescription, ...] = (
    MicrowaveSensorDescription(
        key="cook_time_remaining",
        translation_key="cook_time_remaining",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda microwave: microwave.get_cook_time_remaining(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WhirlpoolMicrowaveConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        WhirlpoolMicrowaveSensor(coordinator, desc) for desc in SENSORS
    )


class WhirlpoolMicrowaveSensor(WhirlpoolMicrowaveEntity, SensorEntity):
    entity_description: MicrowaveSensorDescription

    def __init__(
        self, coordinator, description: MicrowaveSensorDescription
    ) -> None:
        super().__init__(coordinator, key=description.key)
        self.entity_description = description

    @property
    def native_value(self) -> int | None:
        return self.entity_description.value_fn(self.microwave)
