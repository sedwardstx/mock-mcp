"""Unit tests for telemetry row models + typed loading (3.1-UNIT-001..004)."""

import pytest
from pydantic import ValidationError

from contoso_support_mcp.config import DEFAULT_FIXTURES_PATH
from contoso_support_mcp.data.loader import load_scenarios
from contoso_support_mcp.data.models import (
    ArmTraceRow,
    ComputeGuestLogRow,
    ComputeHostLogRow,
    NetworkLogRow,
)

RID = "/subscriptions/x/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm"


def test_row_models_validate_wellformed():
    """3.1-UNIT-001: each row model accepts a well-formed row."""
    ArmTraceRow(time_generated="2026-05-14T09:00:00Z", resource_id=RID, http_status_code=200)
    NetworkLogRow(time_generated="2026-05-14T09:00:00Z", resource_id=RID, destination_port=443)
    ComputeHostLogRow(time_generated="2026-05-14T09:00:00Z", resource_id=RID, event_name="Reboot")
    ComputeGuestLogRow(time_generated="2026-05-14T09:00:00Z", resource_id=RID, event_id=7031)


def test_row_missing_required_field_rejected():
    """3.1-UNIT-002: a row missing resource_id / time_generated fails validation."""
    with pytest.raises(ValidationError):
        ArmTraceRow(time_generated="2026-05-14T09:00:00Z")  # missing resource_id
    with pytest.raises(ValidationError):
        NetworkLogRow(resource_id=RID)  # missing time_generated


def test_loader_loads_typed_telemetry():
    """3.1-UNIT-003: backfilled sample telemetry loads as typed rows."""
    dataset = load_scenarios(DEFAULT_FIXTURES_PATH)
    arm_scenario = dataset.get_by_ticket("TICKET-10000001")
    assert arm_scenario is not None
    traces = arm_scenario.telemetry.arm_control_plane_traces
    assert len(traces) == 2
    assert all(isinstance(t, ArmTraceRow) for t in traces)
    assert any(t.sub_status == "AllocationFailed" for t in traces)

    net_scenario = dataset.get_by_ticket("TICKET-10000002")
    assert net_scenario is not None
    assert any(r.action == "Deny" for r in net_scenario.telemetry.network_logs)


def test_empty_telemetry_scenarios_still_load():
    """3.1-UNIT-004: scenarios with `telemetry: {}` remain valid (backward-compat)."""
    dataset = load_scenarios(DEFAULT_FIXTURES_PATH)
    generated = dataset.get_by_ticket("TICKET-10000010")
    assert generated is not None
    assert generated.telemetry.arm_control_plane_traces == []
