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
