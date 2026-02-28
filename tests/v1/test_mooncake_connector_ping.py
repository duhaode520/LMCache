# SPDX-License-Identifier: Apache-2.0
"""
Tests for MooncakestoreConnector ping/support_ping functionality.

Uses mock store to verify connector behavior without real Mooncake dependency.
"""

# Standard
from unittest.mock import MagicMock

# Third Party
import pytest


class TestMooncakeConnectorPing:
    """Test support_ping and ping on MooncakestoreConnector."""

    def _make_connector_with_mock_store(self, health_check_return=0):
        """Create a MooncakestoreConnector with a mocked store.

        We patch the __init__ to skip real Mooncake setup,
        then manually set the store mock.
        """
        # First Party
        from lmcache.v1.storage_backend.connector.mooncakestore_connector import (
            MooncakestoreConnector,
        )

        mock_store = MagicMock()
        mock_store.health_check.return_value = health_check_return

        # Create connector bypassing __init__
        connector = object.__new__(MooncakestoreConnector)
        connector.store = mock_store
        return connector, mock_store

    def test_support_ping_returns_true(self):
        """support_ping() should always return True."""
        connector, _ = self._make_connector_with_mock_store()
        assert connector.support_ping() is True

    @pytest.mark.asyncio
    async def test_ping_returns_zero_when_healthy(self):
        """ping() should return 0 when store.health_check() returns 0."""
        connector, mock_store = self._make_connector_with_mock_store(
            health_check_return=0
        )
        result = await connector.ping()
        assert result == 0
        mock_store.health_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_returns_one_when_not_initialized(self):
        """ping() should return 1 when store.health_check() returns 1."""
        connector, mock_store = self._make_connector_with_mock_store(
            health_check_return=1
        )
        result = await connector.ping()
        assert result == 1
        mock_store.health_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_returns_two_when_master_unreachable(self):
        """ping() should return 2 when store.health_check() returns 2."""
        connector, mock_store = self._make_connector_with_mock_store(
            health_check_return=2
        )
        result = await connector.ping()
        assert result == 2
        mock_store.health_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_propagates_exception(self):
        """ping() should propagate exceptions from store.health_check()."""
        connector, mock_store = self._make_connector_with_mock_store()
        mock_store.health_check.side_effect = RuntimeError("connection lost")

        with pytest.raises(RuntimeError, match="connection lost"):
            await connector.ping()
