"""Tests for the hood light: pure helpers + entity behavior."""
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.whirlpool_microwave.light import brightness_to_level, level_to_brightness
from tests.conftest import MOCK_ATTRS, setup_integration


@pytest.mark.parametrize("level,expected", [("off", None), ("low", 128), ("high", 255), (None, None)])
def test_level_to_brightness(level, expected):
    assert level_to_brightness(level) == expected


@pytest.mark.parametrize("brightness,level", [(1, "low"), (128, "low"), (191, "low"), (192, "high"), (255, "high")])
def test_brightness_to_level(brightness, level):
    assert brightness_to_level(brightness) == level


async def test_light_turn_on_high(hass):
    attrs = dict(MOCK_ATTRS)
    await setup_integration(hass, attrs)

    light_ids = hass.states.async_entity_ids("light")
    assert len(light_ids) == 1
    eid = light_ids[0]

    with patch(
        "custom_components.whirlpool_microwave.microwave.Microwave.set_light_level",
        new=AsyncMock(return_value=True),
    ) as set_level:
        await hass.services.async_call(
            "light", "turn_on", {"entity_id": eid}, blocking=True
        )
    set_level.assert_awaited_once_with("high")
