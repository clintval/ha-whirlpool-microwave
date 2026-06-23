"""Setup/teardown tests for the integration."""
from homeassistant.config_entries import ConfigEntryState

from tests.conftest import MOCK_ATTRS, setup_integration


async def test_setup_and_unload(hass):
    entry = await setup_integration(hass, MOCK_ATTRS)
    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data is not None

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
