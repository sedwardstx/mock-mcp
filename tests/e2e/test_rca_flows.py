"""End-to-end RCA flows driving the real MCP tool sequence (3.5-E2E-001..003).

Single-round: ticket → resource → telemetry → evidence.
Multi-round:  the "obvious" query is inconclusive; a second query reveals the cause.
"""

from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from contoso_support_mcp.server import build_server


async def _resource_id_for(client, ticket_id: str) -> str:
    pivot = await client.call_tool("get_ticket_resources", {"ticket_id": ticket_id})
    return pivot.structuredContent["resources"][0]["resource_id"]


async def test_single_round_rca_arm():
    """3.5-E2E-001: TICKET-10000001 solved via ticket→resource→ARM query."""
    async with client_session(build_server()) as client:
        ticket = await client.call_tool("get_ticket", {"ticket_id": "TICKET-10000001"})
        assert ticket.structuredContent["status"] == "ok"

        rid = await _resource_id_for(client, "TICKET-10000001")
        traces = await client.call_tool("query_arm_traces", {"resource_id": rid})
        rows = traces.structuredContent["rows"]
        # Evidence for the ARM (allocation) root cause is present.
        assert any(r["activity_status"] == "Failed" for r in rows)


async def test_multi_round_rca_requires_second_query():
    """3.5-E2E-002/003: TICKET-10000026 (multi_round, compute_host cause).

    The "obvious" guest-log query is inconclusive (benign only); the host-log
    query reveals the degraded-host evidence.
    """
    async with client_session(build_server()) as client:
        rid = await _resource_id_for(client, "TICKET-10000026")

        # Round 1 — the obvious in-guest look is inconclusive (no Error-level rows).
        guest = await client.call_tool("query_compute_guest_logs", {"resource_id": rid})
        guest_rows = guest.structuredContent["rows"]
        assert all(r["level"] != "Error" for r in guest_rows)

        # Round 2 — the host logs reveal the real (platform) evidence.
        host = await client.call_tool("query_compute_host_logs", {"resource_id": rid})
        host_rows = host.structuredContent["rows"]
        assert any(r["health_status"] == "Degraded" for r in host_rows)


async def test_high_numbered_scenario_resolves_end_to_end():
    """4.1-E2E-001: a high-numbered generated scenario works ticket→resource→telemetry."""
    async with client_session(build_server()) as client:
        ticket = await client.call_tool("get_ticket", {"ticket_id": "TICKET-10000100"})
        assert ticket.structuredContent["status"] == "ok"
        rid = await _resource_id_for(client, "TICKET-10000100")
        # TICKET-10000100 has an ARM root cause → the ARM query surfaces the failure.
        traces = await client.call_tool("query_arm_traces", {"resource_id": rid})
        assert any(r["activity_status"] == "Failed" for r in traces.structuredContent["rows"])
