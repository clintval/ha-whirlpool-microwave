"""Unit tests for the Microwave appliance class (no HA framework needed)."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.whirlpool_microwave import const
from custom_components.whirlpool_microwave.microwave import Microwave


def make_microwave(attributes: dict[str, str]) -> Microwave:
    """Build a Microwave with mocked deps and a canned attribute payload."""
    microwave = Microwave(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    microwave._data_dict = {"attributes": {k: {"value": v} for k, v in attributes.items()}}
    return microwave


@pytest.mark.parametrize("value,expected", [("0", "off"), ("2", "low"), ("4", "high")])
def test_get_light_level(value, expected):
    assert make_microwave({const.ATTR_LIGHT: value}).get_light_level() == expected


def test_get_light_level_missing():
    assert make_microwave({}).get_light_level() is None


@pytest.mark.parametrize("level,value", [("off", "0"), ("low", "2"), ("high", "4")])
async def test_set_light_level(level, value):
    microwave = make_microwave({})
    microwave.send_attributes = AsyncMock(return_value=True)
    assert await microwave.set_light_level(level) is True
    microwave.send_attributes.assert_awaited_once_with({const.ATTR_LIGHT: value})


async def test_set_light_level_invalid():
    microwave = make_microwave({})
    microwave.send_attributes = AsyncMock()
    with pytest.raises(ValueError):
        await microwave.set_light_level("bogus")
    microwave.send_attributes.assert_not_awaited()


@pytest.mark.parametrize(
    "value,expected",
    [("0", "off"), ("2", "low"), ("4", "medium"), ("5", "medium_high"), ("6", "high")],
)
def test_get_fan_speed(value, expected):
    assert make_microwave({const.ATTR_FAN: value}).get_fan_speed() == expected


@pytest.mark.parametrize("speed,value", [("medium_high", "5"), ("high", "6")])
async def test_set_fan_speed(speed, value):
    microwave = make_microwave({})
    microwave.send_attributes = AsyncMock(return_value=True)
    assert await microwave.set_fan_speed(speed) is True
    microwave.send_attributes.assert_awaited_once_with({const.ATTR_FAN: value})


@pytest.mark.parametrize("value,expected", [("1", True), ("0", False)])
def test_get_quiet_mode(value, expected):
    assert make_microwave({const.ATTR_QUIET: value}).get_quiet_mode() is expected


async def test_set_quiet_mode():
    microwave = make_microwave({})
    microwave.send_attributes = AsyncMock(return_value=True)
    assert await microwave.set_quiet_mode(True) is True
    microwave.send_attributes.assert_awaited_once_with({const.ATTR_QUIET: "1"})


@pytest.mark.parametrize("value,expected", [("1", True), ("0", False)])
def test_get_control_lock(value, expected):
    assert make_microwave({const.ATTR_LOCK: value}).get_control_lock() is expected


async def test_set_control_lock():
    microwave = make_microwave({})
    microwave.send_attributes = AsyncMock(return_value=True)
    assert await microwave.set_control_lock(True) is True
    microwave.send_attributes.assert_awaited_once_with({const.ATTR_LOCK: "1"})


@pytest.mark.parametrize("value,expected", [("1", True), ("0", False)])
def test_get_turntable(value, expected):
    assert make_microwave({const.ATTR_TURNTABLE: value}).get_turntable() is expected


async def test_set_turntable():
    microwave = make_microwave({})
    microwave.send_attributes = AsyncMock(return_value=True)
    assert await microwave.set_turntable(True) is True
    microwave.send_attributes.assert_awaited_once_with({const.ATTR_TURNTABLE: "1"})


@pytest.mark.parametrize("idle,running", [("1", False), ("0", True)])
def test_get_running_inverts_idle(idle, running):
    assert make_microwave({const.ATTR_IDLE: idle}).get_running() is running


def test_get_running_missing():
    assert make_microwave({}).get_running() is None


def test_get_cook_time_remaining():
    assert make_microwave({const.ATTR_COOK_REMAINING: "90"}).get_cook_time_remaining() == 90


@pytest.mark.parametrize("value,expected", [("1", True), ("0", False)])
def test_get_door_open(value, expected):
    assert make_microwave({const.ATTR_DOOR: value}).get_door_open() is expected


def test_get_door_open_missing():
    assert make_microwave({}).get_door_open() is None
