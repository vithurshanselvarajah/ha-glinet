from unittest.mock import AsyncMock, MagicMock

from custom_components.ha_glinet.hub import GLinetHub
from custom_components.ha_glinet.models import AdGuardStatus


async def test_fetch_adguard_status() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._api = MagicMock()
    hub._adguard_status = None
    
    mock_config = {"enabled": True, "dns_enabled": False}
    hub._invoke_optional_api = AsyncMock(return_value=mock_config)
    
    await hub.fetch_adguard_status()
    
    assert hub.adguard_status.enabled is True
    assert hub.adguard_status.dns_enabled is False


async def test_set_adguard_enabled() -> None:
    hub = GLinetHub.__new__(GLinetHub)
    hub._api = MagicMock()
    hub._api.adguard.set_config = AsyncMock()
    hub._adguard_status = AdGuardStatus(enabled=False, dns_enabled=True)
    
    hub._invoke_api = AsyncMock()
    hub.fetch_adguard_status = AsyncMock()
    
    await hub.set_adguard_enabled(True)
    
    hub._invoke_api.assert_called_once()
    # To test the lambda, we'd need more complex mocking, but this is a start
