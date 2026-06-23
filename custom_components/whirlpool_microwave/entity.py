"""Shared entity base for the Whirlpool Microwave."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WhirlpoolMicrowaveCoordinator


class WhirlpoolMicrowaveEntity(CoordinatorEntity[WhirlpoolMicrowaveCoordinator]):
    """Base class wiring device info, unique id, and availability."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: WhirlpoolMicrowaveCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self.microwave = coordinator.microwave
        said = self.microwave.said
        self._attr_unique_id = f"{said}-{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, said)},
            manufacturer="Whirlpool",
            name=self.microwave.name or said,
            model=coordinator.model,
        )

    @property
    def available(self) -> bool:
        return super().available and bool(self.microwave.get_online())
