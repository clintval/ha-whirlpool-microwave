"""Config flow tests."""
from unittest.mock import AsyncMock, patch

from homeassistant.data_entry_flow import FlowResultType

from custom_components.whirlpool_microwave.const import CONF_BRAND, CONF_REGION, DOMAIN
from tests.conftest import MOCK_OWNED


async def _submit(hass, errors_expected=None):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] is FlowResultType.FORM
    return await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "email": "user@example.com",
            "password": "secret",
            CONF_REGION: "US",
            CONF_BRAND: "Whirlpool",
        },
    )


async def test_flow_success(hass):
    with (
        patch("custom_components.whirlpool_microwave.config_flow.Auth.do_auth", new=AsyncMock()),
        patch(
            "custom_components.whirlpool_microwave.config_flow.Auth.is_access_token_valid",
            return_value=True,
        ),
        patch(
            "custom_components.whirlpool_microwave.config_flow.WhirlpoolMicrowaveConfigFlow._find_cooking",
            new=AsyncMock(return_value=MOCK_OWNED["1234567"]["Kitchen"][0]),
        ),
        patch("custom_components.whirlpool_microwave.async_setup_entry", return_value=True),
    ):
        result = await _submit(hass)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["said"] == "FAKESAID00001"


async def test_flow_invalid_auth(hass):
    with (
        patch("custom_components.whirlpool_microwave.config_flow.Auth.do_auth", new=AsyncMock()),
        patch(
            "custom_components.whirlpool_microwave.config_flow.Auth.is_access_token_valid",
            return_value=False,
        ),
    ):
        result = await _submit(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}
