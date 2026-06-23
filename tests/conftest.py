"""Shared fixtures for the Whirlpool Microwave tests."""
import pytest

from custom_components.whirlpool_microwave import const

# A representative attribute payload: light off, fan off, switches on, idle.
MOCK_ATTRS: dict[str, str] = {
    const.ATTR_LIGHT: "0",
    const.ATTR_FAN: "0",
    const.ATTR_QUIET: "1",
    const.ATTR_LOCK: "0",
    const.ATTR_TURNTABLE: "1",
    const.ATTR_DOOR: "0",
    const.ATTR_IDLE: "1",
    const.ATTR_COOK_REMAINING: "0",
    "Online": "1",
}

# Owned-appliances response shape returned by the cloud (one Cooking unit).
ACCOUNT_ID = "1234567"
MOCK_OWNED = {
    ACCOUNT_ID: {
        "Kitchen": [
            {
                "SAID": "FAKESAID00001",
                "APPLIANCE_NAME": "Kitchen Microwave",
                "CATEGORY_NAME": "Cooking",
                "DATA_MODEL_KEY": "DDM_COOKING_MHC76_V1",
                "MODEL_NO": "WMH78019HZ01",
                "SERIAL": "FAKESERIAL",
            }
        ]
    }
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Make HA discover custom_components/whirlpool_microwave during tests."""
    yield


@pytest.fixture
def mock_attrs() -> dict[str, str]:
    """A fresh, mutable copy of the attribute payload per test."""
    return dict(MOCK_ATTRS)


from unittest.mock import AsyncMock, patch

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.whirlpool_microwave.const import CONF_BRAND, CONF_REGION, DOMAIN
from custom_components.whirlpool_microwave.microwave import Microwave

ENTRY_DATA = {
    CONF_EMAIL: "user@example.com",
    CONF_PASSWORD: "secret",
    CONF_REGION: "US",
    CONF_BRAND: "Whirlpool",
    "said": "FAKESAID00001",
    "name": "Kitchen Microwave",
    "model": "WMH78019HZ01",
    "data_model": "DDM_COOKING_MHC76_V1",
}


async def setup_integration(hass, attrs: dict[str, str]):
    """Set up the integration with auth + fetch_data mocked; entity state reads `attrs`."""
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, unique_id="FAKESAID00001")
    entry.add_to_hass(hass)

    async def fake_fetch(self):
        self._data_dict = {"attributes": {k: {"value": v} for k, v in attrs.items()}}
        return True

    with (
        patch("custom_components.whirlpool_microwave.Auth.do_auth", new=AsyncMock()),
        patch(
            "custom_components.whirlpool_microwave.Auth.is_access_token_valid",
            return_value=True,
        ),
        patch.object(Microwave, "fetch_data", new=fake_fetch),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry
