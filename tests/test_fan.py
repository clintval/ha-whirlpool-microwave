"""Tests for the hood exhaust fan."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from custom_components.whirlpool_microwave.const import FAN_ORDERED
from tests.conftest import MOCK_ATTRS, setup_integration


@pytest.mark.parametrize(
    "speed,expected_pct",
    [("low", 25), ("medium", 50), ("medium_high", 75), ("high", 100)],
)
def test_speed_percentage_mapping(speed, expected_pct):
    assert ordered_list_item_to_percentage(FAN_ORDERED, speed) == expected_pct
    assert percentage_to_ordered_list_item(FAN_ORDERED, expected_pct) == speed


async def test_fan_set_percentage_maps_to_medium(hass):
    await setup_integration(hass, dict(MOCK_ATTRS))
    fan_ids = hass.states.async_entity_ids("fan")
    assert len(fan_ids) == 1
    eid = fan_ids[0]

    with patch(
        "custom_components.whirlpool_microwave.microwave.Microwave.set_fan_speed",
        new=AsyncMock(return_value=True),
    ) as set_speed:
        await hass.services.async_call(
            "fan",
            "set_percentage",
            {"entity_id": eid, "percentage": 50},
            blocking=True,
        )
    set_speed.assert_awaited_once_with("medium")


async def test_fan_turn_off(hass):
    await setup_integration(hass, dict(MOCK_ATTRS))
    fan_ids = hass.states.async_entity_ids("fan")
    assert len(fan_ids) == 1
    eid = fan_ids[0]

    with patch(
        "custom_components.whirlpool_microwave.microwave.Microwave.set_fan_speed",
        new=AsyncMock(return_value=True),
    ) as set_speed:
        await hass.services.async_call(
            "fan", "turn_off", {"entity_id": eid}, blocking=True
        )
    set_speed.assert_awaited_once_with("off")


async def test_fan_set_percentage_failure_raises(hass):
    """When set_fan_speed returns False, set_percentage should raise HomeAssistantError."""
    await setup_integration(hass, dict(MOCK_ATTRS))
    fan_ids = hass.states.async_entity_ids("fan")
    assert len(fan_ids) == 1
    eid = fan_ids[0]

    with (
        patch(
            "custom_components.whirlpool_microwave.microwave.Microwave.set_fan_speed",
            new=AsyncMock(return_value=False),
        ),
        pytest.raises(HomeAssistantError),
    ):
        await hass.services.async_call(
            "fan",
            "set_percentage",
            {"entity_id": eid, "percentage": 50},
            blocking=True,
        )
