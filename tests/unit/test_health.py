"""Unit tests for the health/identity tool (1.1-UNIT-001, 1.1-UNIT-002)."""

from contoso_support_mcp import SERVER_NAME, __version__
from contoso_support_mcp.tools.health import ServerInfo, server_info


def test_server_info_returns_expected_identity():
    """1.1-UNIT-001 / 1.1-UNIT-002: identity fields are correct."""
    info = server_info()
    assert isinstance(info, ServerInfo)
    assert info.name == SERVER_NAME
    assert info.version == __version__
    assert info.status == "ok"
