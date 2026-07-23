"""Integration tests for the streamable-HTTP (instructor-hosted) transport.

Exercises a real localhost HTTP bind (background uvicorn) with the MCP
streamable-HTTP client. (1.2-INT-001/002/003.)
"""

from __future__ import annotations

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from contoso_support_mcp import SERVER_NAME


async def _call_health(url: str) -> dict:
    async with streamable_http_client(url) as (read, write, _get_session_id):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_server_info", {})
            assert result.isError is False
            return result.structuredContent


async def test_health_over_http(http_server: str):
    """1.2-INT-001: health tool reachable and correct over the network transport."""
    payload = await _call_health(http_server)
    assert payload["name"] == SERVER_NAME
    assert payload["status"] == "ok"


async def test_tool_surface_matches_stdio(http_server: str):
    """1.2-INT-003: the HTTP surface exposes the same tools as stdio."""
    async with streamable_http_client(http_server) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert "get_server_info" in [t.name for t in tools.tools]


async def test_concurrent_clients(http_server: str):
    """1.2-INT-002: multiple concurrent client sessions all get correct responses."""
    results = await asyncio.gather(*[_call_health(http_server) for _ in range(5)])
    assert [r["status"] for r in results] == ["ok"] * 5
