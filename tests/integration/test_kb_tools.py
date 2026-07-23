"""Integration tests for the KB tool over an MCP client (5.1-INT-001..004)."""

from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from contoso_support_mcp.server import build_server


async def test_kb_no_args_lists_all():
    """5.1-INT-001: no-arg search returns ok + the full KB."""
    async with client_session(build_server()) as client:
        result = await client.call_tool("search_known_issues", {})
        sc = result.structuredContent
        assert sc["status"] == "ok"
        assert sc["total"] >= 12
        assert len(sc["matches"]) == sc["total"]


async def test_kb_category_and_product_filters():
    """5.1-INT-002: category and product filters."""
    async with client_session(build_server()) as client:
        net = await client.call_tool("search_known_issues", {"category": "network"})
        assert all(m["category"] == "network" for m in net.structuredContent["matches"])

        vmss = await client.call_tool(
            "search_known_issues", {"product": "Azure Virtual Machine Scale Sets"}
        )
        matches = vmss.structuredContent["matches"]
        assert matches
        assert all(m["product"] == "Azure Virtual Machine Scale Sets" for m in matches)


async def test_kb_keyword_and_empty():
    """5.1-INT-003: keyword hit + empty (no-match) is ok."""
    async with client_session(build_server()) as client:
        hit = await client.call_tool("search_known_issues", {"query": "allocation"})
        assert any(m["id"] == "KB-ARM-001" for m in hit.structuredContent["matches"])

        empty = await client.call_tool("search_known_issues", {"query": "zzz-nomatch"})
        assert empty.structuredContent["status"] == "ok"
        assert empty.structuredContent["matches"] == []
        assert empty.structuredContent["total"] == 0


async def test_kb_invalid_category():
    """5.1-INT-004: invalid category → invalid_request with allowed values."""
    async with client_session(build_server()) as client:
        result = await client.call_tool("search_known_issues", {"category": "martian"})
        sc = result.structuredContent
        assert result.isError is False
        assert sc["status"] == "invalid_request"
        assert "network" in sc["message"]


async def test_kb_tool_is_registered():
    """5.1-INT-001: the tool is discoverable alongside the existing surface."""
    async with client_session(build_server()) as client:
        tools = await client.list_tools()
        names = {t.name for t in tools.tools}
        assert "search_known_issues" in names
        # the ticket + telemetry tools remain
        assert {"get_ticket", "query_arm_traces"} <= names
