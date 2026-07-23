"""Integration tests for the ticket→resource pivot tool (2.4-INT-001..004)."""

from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from contoso_support_mcp.server import build_server

VM_RESOURCE_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-prod"
    "/providers/Microsoft.Compute/virtualMachines/prod-web-01"
)


async def test_pivot_returns_resource_with_exact_id():
    """2.4-INT-001: pivot returns the full resource; resource_id is unchanged
    (Epic 3 telemetry tools consume this exact id)."""
    async with client_session(build_server()) as client:
        result = await client.call_tool("get_ticket_resources", {"ticket_id": "TICKET-10000001"})
        sc = result.structuredContent
        assert sc["status"] == "ok"
        assert len(sc["resources"]) == 1
        assert sc["resources"][0]["resource_id"] == VM_RESOURCE_ID
        assert sc["resources"][0]["subscription_id"] == "00000000-0000-0000-0000-000000000001"


async def test_pivot_vmss_surfaces_instances():
    """2.4-INT-002: a VMSS ticket surfaces instance ids."""
    async with client_session(build_server()) as client:
        result = await client.call_tool("get_ticket_resources", {"ticket_id": "TICKET-10000002"})
        sc = result.structuredContent
        assert sc["status"] == "ok"
        res = sc["resources"][0]
        assert res["resource_type"] == "Microsoft.Compute/virtualMachineScaleSets"
        assert res["instances"] == ["api-vmss_0", "api-vmss_1"]


async def test_pivot_unknown_ticket_not_found():
    """2.4-INT-003: unknown ticket → not_found (no raise)."""
    async with client_session(build_server()) as client:
        result = await client.call_tool("get_ticket_resources", {"ticket_id": "TICKET-99999999"})
        assert result.isError is False
        assert result.structuredContent["status"] == "not_found"


async def test_pivot_invalid_id():
    """2.4-INT-004: malformed id → invalid_request."""
    async with client_session(build_server()) as client:
        result = await client.call_tool("get_ticket_resources", {"ticket_id": "nope"})
        assert result.isError is False
        assert result.structuredContent["status"] == "invalid_request"
