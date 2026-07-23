"""Integration tests: connect an MCP client to the server and exercise tools.

Uses the MCP SDK's in-memory connected client/server session, which exercises
the same tool-dispatch path a stdio-connected agent uses.
(1.1-INT-001 discoverability, 1.1-INT-002 invocation.)
"""

from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from contoso_support_mcp import SERVER_NAME
from contoso_support_mcp.server import build_server


async def test_health_tool_is_discoverable():
    """1.1-INT-001: the health tool is listed over an MCP client session."""
    server = build_server()
    async with client_session(server) as client:
        tools = await client.list_tools()
        assert "get_server_info" in [t.name for t in tools.tools]


async def test_health_tool_returns_identity():
    """1.1-INT-002: calling the health tool returns the server identity."""
    server = build_server()
    async with client_session(server) as client:
        result = await client.call_tool("get_server_info", {})
        assert result.isError is False
        assert result.structuredContent["name"] == SERVER_NAME
        assert result.structuredContent["status"] == "ok"
