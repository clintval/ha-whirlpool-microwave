"""Tests for the microwave binary sensors and sensors."""
from homeassistant.helpers import entity_registry as er

from tests.conftest import MOCK_ATTRS, setup_integration


async def test_door_closed(hass):
    await setup_integration(hass, dict(MOCK_ATTRS))  # door = "0"
    reg = er.async_get(hass)
    eid = reg.async_get_entity_id("binary_sensor", "whirlpool_microwave", "FAKESAID00001-door")
    assert eid is not None
    state = hass.states.get(eid)
    assert state is not None
    assert state.state == "off"


async def test_running_off_when_idle(hass):
    await setup_integration(hass, dict(MOCK_ATTRS))  # idle = "1" -> running off
    reg = er.async_get(hass)
    eid = reg.async_get_entity_id("binary_sensor", "whirlpool_microwave", "FAKESAID00001-running")
    assert eid is not None
    state = hass.states.get(eid)
    assert state is not None
    assert state.state == "off"


async def test_cook_time_remaining(hass):
    attrs = dict(MOCK_ATTRS)
    attrs["Mwo_TimeStatusCookTimeRemaining"] = "90"
    await setup_integration(hass, attrs)
    reg = er.async_get(hass)
    eid = reg.async_get_entity_id("sensor", "whirlpool_microwave", "FAKESAID00001-cook_time_remaining")
    assert eid is not None
    state = hass.states.get(eid)
    assert state is not None
    assert state.state == "90"
