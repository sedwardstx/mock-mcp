"""Integration tests for telemetry query tools over an MCP client.

ARM (3.2). Network and Compute tools (3.3/3.4) extend this file.
"""

from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from contoso_support_mcp.server import build_server

VM_RID = (
    "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-prod"
    "/providers/Microsoft.Compute/virtualMachines/prod-web-01"
)
VMSS_RID = (
    "/subscriptions/00000000-0000-0000-0000-000000000002/resourceGroups/rg-api"
    "/providers/Microsoft.Compute/virtualMachineScaleSets/api-vmss"
)
GUEST_VM_RID = (
    "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-data"
    "/providers/Microsoft.Compute/virtualMachines/sql-node-01"
)
HOST_VMSS_RID = (
    "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-data"
    "/providers/Microsoft.Compute/virtualMachineScaleSets/data-vmss"
)


async def test_arm_traces_returns_allocation_failure_evidence():
    """3.2-INT-001: ARM query surfaces the 409/AllocationFailed evidence row."""
    async with client_session(build_server()) as client:
        result = await client.call_tool("query_arm_traces", {"resource_id": VM_RID})
        sc = result.structuredContent
        assert sc["status"] == "ok"
        assert sc["count"] >= 1
        assert any(r["sub_status"] == "AllocationFailed" for r in sc["rows"])
        assert any(r["http_status_code"] == 409 for r in sc["rows"])


async def test_arm_traces_time_range_scoping():
    """3.2-INT-002: a narrow time range excludes the earlier benign read."""
    async with client_session(build_server()) as client:
        result = await client.call_tool(
            "query_arm_traces",
            {"resource_id": VM_RID, "time_range": "2026-05-14T09:10:00Z/2026-05-14T09:20:00Z"},
        )
        sc = result.structuredContent
        assert sc["status"] == "ok"
        assert all(r["activity_status"] == "Failed" for r in sc["rows"])
        assert sc["count"] == 1


async def test_arm_traces_unrelated_resource_is_empty():
    """3.2-INT-003: a resource with no ARM traces returns ok + empty rows."""
    async with client_session(build_server()) as client:
        result = await client.call_tool(
            "query_arm_traces", {"resource_id": "/subscriptions/none/vm/missing"}
        )
        sc = result.structuredContent
        assert result.isError is False
        assert sc["status"] == "ok"
        assert sc["rows"] == []


async def test_arm_traces_bad_time_range_invalid():
    """3.2-INT-004: malformed time_range → invalid_request."""
    async with client_session(build_server()) as client:
        result = await client.call_tool(
            "query_arm_traces", {"resource_id": VM_RID, "time_range": "garbage"}
        )
        assert result.isError is False
        assert result.structuredContent["status"] == "invalid_request"


async def test_network_logs_returns_deny_evidence():
    """3.3-INT-001: network query surfaces the Deny evidence row (dst 1433)."""
    async with client_session(build_server()) as client:
        result = await client.call_tool("query_network_logs", {"resource_id": VMSS_RID})
        sc = result.structuredContent
        assert sc["status"] == "ok"
        deny = [r for r in sc["rows"] if r["action"] == "Deny"]
        assert deny
        assert deny[0]["destination_port"] == 1433
        assert deny[0]["nsg_rule_name"] == "DenyDbOutbound"


async def test_network_logs_action_filter():
    """3.3-INT-002: action='Deny' returns only Deny rows."""
    async with client_session(build_server()) as client:
        result = await client.call_tool(
            "query_network_logs", {"resource_id": VMSS_RID, "action": "Deny"}
        )
        sc = result.structuredContent
        assert sc["count"] == 1
        assert all(r["action"] == "Deny" for r in sc["rows"])


async def test_network_logs_unrelated_resource_empty():
    """3.3-INT-003: a resource with no network logs → ok + empty."""
    async with client_session(build_server()) as client:
        result = await client.call_tool(
            "query_network_logs", {"resource_id": "/subscriptions/none/vm/x"}
        )
        assert result.structuredContent["status"] == "ok"
        assert result.structuredContent["rows"] == []


async def test_network_logs_bad_time_range_invalid():
    """3.3-INT-004: malformed time_range → invalid_request."""
    async with client_session(build_server()) as client:
        result = await client.call_tool(
            "query_network_logs", {"resource_id": VMSS_RID, "time_range": "nope"}
        )
        assert result.structuredContent["status"] == "invalid_request"


async def test_guest_logs_windows_event_evidence():
    """3.4-INT-001: guest query on a VM surfaces Windows event 7031 (Windows-only)."""
    async with client_session(build_server()) as client:
        result = await client.call_tool("query_compute_guest_logs", {"resource_id": GUEST_VM_RID})
        sc = result.structuredContent
        assert sc["status"] == "ok"
        assert any(r["event_id"] == 7031 for r in sc["rows"])
        assert any(r["provider_name"] == "Service Control Manager" for r in sc["rows"])


async def test_host_logs_vmss_instance_scoping():
    """3.4-INT-002: host query for a specific VMSS instance returns only that instance's rows."""
    async with client_session(build_server()) as client:
        result = await client.call_tool(
            "query_compute_host_logs",
            {"resource_id": HOST_VMSS_RID, "instance_id": "data-vmss_0"},
        )
        sc = result.structuredContent
        assert sc["status"] == "ok"
        assert sc["count"] == 1
        assert sc["rows"][0]["instance_id"] == "data-vmss_0"
        assert sc["rows"][0]["health_status"] == "Degraded"


async def test_host_logs_unknown_instance_invalid():
    """3.4-INT-003: an instance not on the VMSS → invalid_request with allowed instances."""
    async with client_session(build_server()) as client:
        result = await client.call_tool(
            "query_compute_host_logs",
            {"resource_id": HOST_VMSS_RID, "instance_id": "data-vmss_99"},
        )
        sc = result.structuredContent
        assert sc["status"] == "invalid_request"
        assert "data-vmss_0" in sc["message"]


async def test_compute_unrelated_resource_empty():
    """3.4-INT-004: unrelated resource → ok empty for both host and guest."""
    async with client_session(build_server()) as client:
        host = await client.call_tool(
            "query_compute_host_logs", {"resource_id": "/subscriptions/none/vmss/x"}
        )
        guest = await client.call_tool(
            "query_compute_guest_logs", {"resource_id": "/subscriptions/none/vm/x"}
        )
        assert host.structuredContent["rows"] == []
        assert guest.structuredContent["rows"] == []


async def test_host_logs_all_instances_when_none_specified():
    """3.4-INT-005: without instance_id, all instances' host rows are returned."""
    async with client_session(build_server()) as client:
        result = await client.call_tool("query_compute_host_logs", {"resource_id": HOST_VMSS_RID})
        sc = result.structuredContent
        instances = {r["instance_id"] for r in sc["rows"]}
        assert {"data-vmss_0", "data-vmss_1"} <= instances


async def test_compute_query_deterministic():
    """3.4-INT-006: identical query twice → identical rows."""
    async with client_session(build_server()) as client:
        a = await client.call_tool("query_compute_guest_logs", {"resource_id": GUEST_VM_RID})
        b = await client.call_tool("query_compute_guest_logs", {"resource_id": GUEST_VM_RID})
        assert a.structuredContent["rows"] == b.structuredContent["rows"]
