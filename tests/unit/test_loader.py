"""Unit tests for the deterministic fixture loader (2.1-UNIT-004..007)."""

import pytest

from contoso_support_mcp.config import DEFAULT_FIXTURES_PATH
from contoso_support_mcp.data.loader import FixtureValidationError, load_scenarios

MINIMAL_FIXTURE = """\
scenario_id: {sid}
difficulty: single_round
ticket:
  ticket_id: {tid}
  title: T
  symptom: S
  azure_product: Azure Virtual Machines
  persona: windows_admin
  severity: Sev3
  status: Active
  created_at: "2026-01-01T00:00:00Z"
  updated_at: "2026-01-01T00:00:00Z"
  resource_ids: ["/subscriptions/x"]
resources:
  - resource_id: "/subscriptions/x"
    resource_type: "Microsoft.Compute/virtualMachines"
    name: n
    resource_group: rg
    subscription_id: x
    location: eastus
telemetry: {{}}
root_cause: {{category: arm, summary: c, resolution: r}}
"""


def _write(path, sid, tid):
    (path / f"{sid}.yaml").write_text(MINIMAL_FIXTURE.format(sid=sid, tid=tid))


def test_loads_shipped_samples():
    """2.1-UNIT-004: the shipped sample fixtures load into a Dataset."""
    dataset = load_scenarios(DEFAULT_FIXTURES_PATH)
    assert len(dataset) >= 3
    assert dataset.get_by_ticket("TICKET-10000001") is not None


def test_deterministic_ordering_and_content(tmp_path):
    """2.1-UNIT-007: two loads yield identical ordered ids and content."""
    _write(tmp_path, "TICKET-20000002", "TICKET-20000002")
    _write(tmp_path, "TICKET-20000001", "TICKET-20000001")
    first = load_scenarios(tmp_path)
    second = load_scenarios(tmp_path)
    assert [s.scenario_id for s in first.scenarios] == [
        "TICKET-20000001",
        "TICKET-20000002",
    ]
    assert [s.model_dump() for s in first.scenarios] == [
        s.model_dump() for s in second.scenarios
    ]


def test_duplicate_ticket_id_rejected(tmp_path):
    """2.1-UNIT-006: duplicate ticket ids across files fail fast."""
    _write(tmp_path, "TICKET-20000001", "TICKET-29999999")
    _write(tmp_path, "TICKET-20000002", "TICKET-29999999")
    with pytest.raises(FixtureValidationError) as exc:
        load_scenarios(tmp_path)
    assert "Duplicate ticket id" in str(exc.value)


def test_malformed_fixture_names_file(tmp_path):
    """2.1-UNIT-005: a malformed fixture raises an error naming the file."""
    (tmp_path / "TICKET-20000009.yaml").write_text("scenario_id: TICKET-20000009\nticket: {}\n")
    with pytest.raises(FixtureValidationError) as exc:
        load_scenarios(tmp_path)
    assert "TICKET-20000009.yaml" in str(exc.value)
