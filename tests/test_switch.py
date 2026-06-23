"""Tests for the microwave switches: quiet mode, control lock, turntable."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from tests.conftest import MOCK_ATTRS, setup_integration


async def test_quiet_mode_state_on(hass):
    """MOCK_ATTRS has quiet mode = "1", so the switch should report on."""
    await setup_integration(hass, dict(MOCK_ATTRS))

    reg = er.async_get(hass)
    eid = reg.async_get_entity_id("switch", "whirlpool_microwave", "FAKESAID00001-quiet_mode")
    assert eid is not None

    state = hass.states.get(eid)
    assert state is not None
    assert state.state == "on"


async def test_control_lock_turn_on(hass):
    """Calling turn_on on the control_lock switch should invoke set_control_lock(True)."""
    await setup_integration(hass, dict(MOCK_ATTRS))

    reg = er.async_get(hass)
    eid = reg.async_get_entity_id("switch", "whirlpool_microwave", "FAKESAID00001-control_lock")
    assert eid is not None

    with patch(
        "custom_components.whirlpool_microwave.microwave.Microwave.set_control_lock",
        new=AsyncMock(return_value=True),
    ) as set_lock:
        await hass.services.async_call(
            "switch", "turn_on", {"entity_id": eid}, blocking=True
        )
    set_lock.assert_awaited_once_with(True)


async def test_control_lock_turn_on_failure_raises(hass):
    """When set_control_lock returns False, turn_on should raise HomeAssistantError."""
    await setup_integration(hass, dict(MOCK_ATTRS))

    reg = er.async_get(hass)
    eid = reg.async_get_entity_id("switch", "whirlpool_microwave", "FAKESAID00001-control_lock")
    assert eid is not None

    with (
        patch(
            "custom_components.whirlpool_microwave.microwave.Microwave.set_control_lock",
            new=AsyncMock(return_value=False),
        ),
        pytest.raises(HomeAssistantError),
    ):
        await hass.services.async_call(
            "switch", "turn_on", {"entity_id": eid}, blocking=True
        )
