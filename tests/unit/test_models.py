"""Unit tests for the domain models (2.1-UNIT-001/002/003/008)."""

import pytest
from pydantic import ValidationError

from contoso_support_mcp.data.models import Scenario, Ticket

VALID_SCENARIO = {
    "scenario_id": "TICKET-19999999",
    "difficulty": "single_round",
    "ticket": {
        "ticket_id": "TICKET-19999999",
        "title": "Test",
        "symptom": "Something broke",
        "azure_product": "Azure Virtual Machines",
        "persona": "windows_admin",
        "severity": "Sev2",
        "status": "Active",
        "created_at": "2026-05-14T09:12:00Z",
        "updated_at": "2026-05-14T09:40:00Z",
        "resource_ids": ["/subscriptions/x/rg/y/vm/z"],
    },
    "resources": [
        {
            "resource_id": "/subscriptions/x/rg/y/vm/z",
            "resource_type": "Microsoft.Compute/virtualMachines",
            "name": "z",
            "resource_group": "y",
            "subscription_id": "x",
            "location": "eastus",
        }
    ],
    "root_cause": {"category": "arm", "summary": "cause", "resolution": "fix"},
}


def test_valid_scenario_parses():
    """2.1-UNIT-001: a valid scenario builds the full model graph."""
    scenario = Scenario.model_validate(VALID_SCENARIO)
    assert scenario.ticket.ticket_id == "TICKET-19999999"
    assert scenario.resources[0].instances == []  # 2.1-UNIT-008: default empty


def test_telemetry_defaults_empty():
    """2.1-UNIT-008: telemetry container defaults to empty lists (Epic 3 fills it)."""
    scenario = Scenario.model_validate(VALID_SCENARIO)
    assert scenario.telemetry.arm_control_plane_traces == []
    assert scenario.telemetry.network_logs == []
    assert scenario.telemetry.compute_host_logs == []
    assert scenario.telemetry.compute_guest_logs == []


@pytest.mark.parametrize("bad_id", ["TICKET-123", "FOO", "ticket-12345678", "TICKET-1234567X"])
def test_ticket_id_format_rejected(bad_id):
    """2.1-UNIT-002: malformed ticket ids are rejected."""
    with pytest.raises(ValidationError):
        Ticket.model_validate({**VALID_SCENARIO["ticket"], "ticket_id": bad_id})


def test_ticket_id_format_accepted():
    """2.1-UNIT-002: a well-formed ticket id is accepted."""
    ticket = Ticket.model_validate({**VALID_SCENARIO["ticket"], "ticket_id": "TICKET-12345678"})
    assert ticket.ticket_id == "TICKET-12345678"


def test_missing_required_field_names_field():
    """2.1-UNIT-003: a missing required field raises a clear ValidationError."""
    broken = {**VALID_SCENARIO["ticket"]}
    del broken["symptom"]
    with pytest.raises(ValidationError) as exc:
        Ticket.model_validate(broken)
    assert "symptom" in str(exc.value)
