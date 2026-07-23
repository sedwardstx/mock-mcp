"""Integration tests for the ticket tools over an MCP client (2.2-INT-001..004)."""

from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from contoso_support_mcp.server import build_server


async def test_get_ticket_ok():
    async with client_session(build_server()) as client:
        result = await client.call_tool("get_ticket", {"ticket_id": "TICKET-10000001"})
        sc = result.structuredContent
        assert sc["status"] == "ok"
        assert sc["ticket"]["ticket_id"] == "TICKET-10000001"
        assert sc["ticket"]["persona"] == "windows_admin"
        assert sc["ticket"]["azure_product"] == "Azure Virtual Machines"


async def test_get_ticket_not_found():
    async with client_session(build_server()) as client:
        result = await client.call_tool("get_ticket", {"ticket_id": "TICKET-99999999"})
        assert result.isError is False
        assert result.structuredContent["status"] == "not_found"


async def test_get_ticket_invalid_id():
    async with client_session(build_server()) as client:
        result = await client.call_tool("get_ticket", {"ticket_id": "not-a-ticket"})
        assert result.isError is False
        assert result.structuredContent["status"] == "invalid_request"


async def test_list_tickets():
    async with client_session(build_server()) as client:
        result = await client.call_tool("list_tickets", {})
        sc = result.structuredContent
        assert sc["status"] == "ok"
        assert sc["total"] >= 3
        ids = [t["ticket_id"] for t in sc["tickets"]]
        assert "TICKET-10000001" in ids
        assert "TICKET-10000002" in ids


async def test_search_by_status():
    async with client_session(build_server()) as client:
        result = await client.call_tool("search_tickets", {"status": "Active"})
        sc = result.structuredContent
        assert sc["status"] == "ok"
        assert sc["total"] >= 1
        assert all(True for _ in sc["tickets"])


async def test_search_no_match_is_empty_not_error():
    async with client_session(build_server()) as client:
        result = await client.call_tool("search_tickets", {"status": "Resolved"})
        sc = result.structuredContent
        assert result.isError is False
        assert sc["status"] == "ok"
        assert sc["tickets"] == []
        assert sc["total"] == 0


async def test_search_invalid_filter_value():
    async with client_session(build_server()) as client:
        result = await client.call_tool("search_tickets", {"persona": "martian"})
        sc = result.structuredContent
        assert result.isError is False
        assert sc["status"] == "invalid_request"
        assert "windows_admin" in sc["message"]


async def test_search_combined_persona_and_product():
    async with client_session(build_server()) as client:
        result = await client.call_tool(
            "search_tickets",
            {"persona": "azure_developer", "azure_product": "Azure Networking"},
        )
        sc = result.structuredContent
        assert sc["status"] == "ok"
        ids = [t["ticket_id"] for t in sc["tickets"]]
        # AND semantics: every result matches both filters; the seed VMSS-networking
        # sample TICKET-10000002 is among them.
        assert "TICKET-10000002" in ids
        assert all(t["persona"] == "azure_developer" for t in sc["tickets"])
