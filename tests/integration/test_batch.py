"""Tools behave correctly across the full seed batch (2.5-INT-001)."""

from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from contoso_support_mcp.server import build_server


async def test_tools_across_full_batch():
    async with client_session(build_server()) as client:
        listed = await client.call_tool("list_tickets", {"limit": 200})
        total = listed.structuredContent["total"]
        assert total >= 20

        # get + pivot for a generated scenario
        got = await client.call_tool("get_ticket", {"ticket_id": "TICKET-10000006"})
        assert got.structuredContent["status"] == "ok"
        pivot = await client.call_tool("get_ticket_resources", {"ticket_id": "TICKET-10000006"})
        assert pivot.structuredContent["status"] == "ok"
        assert len(pivot.structuredContent["resources"]) == 1

        # search by persona returns a non-empty subset
        searched = await client.call_tool("search_tickets", {"persona": "azure_developer"})
        assert searched.structuredContent["status"] == "ok"
        assert searched.structuredContent["total"] >= 1
