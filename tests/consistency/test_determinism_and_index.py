"""Full-library determinism + scenario-index tests (4.4-UNIT-001/002, 4.4-INT-001)."""

import sys
from pathlib import Path

from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from contoso_support_mcp.config import DEFAULT_FIXTURES_PATH
from contoso_support_mcp.data.loader import load_scenarios
from contoso_support_mcp.server import build_server

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from scenario_index import build_index  # noqa: E402


def test_full_library_load_is_deterministic():
    """4.4-UNIT-001: two full-library loads yield identical data."""
    first = load_scenarios(DEFAULT_FIXTURES_PATH)
    second = load_scenarios(DEFAULT_FIXTURES_PATH)
    assert [s.model_dump(mode="json") for s in first.scenarios] == [
        s.model_dump(mode="json") for s in second.scenarios
    ]


def test_scenario_index_has_row_per_scenario():
    """4.4-UNIT-002: the index builds one row per scenario incl. root cause + tools."""
    dataset = load_scenarios(DEFAULT_FIXTURES_PATH)
    index = build_index(dataset)
    # header + separator + intro lines, then one row per scenario.
    row_lines = [ln for ln in index.splitlines() if ln.startswith("| TICKET-")]
    assert len(row_lines) == len(dataset)
    # Spot-check a row carries the investigation tool sequence.
    assert any("query_" in ln for ln in row_lines)


async def test_tool_query_is_deterministic():
    """4.4-INT-001: a telemetry tool called twice returns identical rows."""
    rid = (
        "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-prod"
        "/providers/Microsoft.Compute/virtualMachines/prod-web-01"
    )
    async with client_session(build_server()) as client:
        a = await client.call_tool("query_arm_traces", {"resource_id": rid})
        b = await client.call_tool("query_arm_traces", {"resource_id": rid})
        assert a.structuredContent["rows"] == b.structuredContent["rows"]
