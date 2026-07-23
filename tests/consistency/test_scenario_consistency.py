"""Whole-library consistency + coverage tests (2.5-CON-001/002, 2.5-UNIT-001/002/003)."""

from contoso_support_mcp.config import DEFAULT_FIXTURES_PATH
from contoso_support_mcp.data.consistency import check_dataset
from contoso_support_mcp.data.loader import Dataset, load_scenarios
from contoso_support_mcp.data.models import Scenario


def _library() -> Dataset:
    return load_scenarios(DEFAULT_FIXTURES_PATH)


def test_shipped_library_loads_and_is_consistent():
    """2.5-CON-001/002: every shipped fixture loads and passes consistency."""
    dataset = _library()
    assert check_dataset(dataset) == []


def test_batch_size_grows():
    """2.5/3.5: the library has grown to a substantial size (>=20)."""
    assert len(_library()) >= 20


def test_library_reaches_100():
    """4.1-UNIT-001: the library contains >= 100 distinct scenarios."""
    dataset = _library()
    assert len(dataset) >= 100
    ids = [s.ticket.ticket_id for s in dataset.scenarios]
    assert len(set(ids)) == len(ids)  # unique


def test_multi_round_scenarios_present_and_documented():
    """3.5-UNIT-002/CON-002 + 4.2-UNIT-002: multi_round scenarios each have a >=2-step path."""
    dataset = _library()
    multi = [s for s in dataset.scenarios if str(s.difficulty) == "multi_round"]
    assert len(multi) >= 3
    assert all(len(s.investigation_path) >= 2 for s in multi)


def test_multi_round_at_least_25_percent():
    """4.2-UNIT-001: at least 25% of the library is multi_round."""
    dataset = _library()
    multi = sum(1 for s in dataset.scenarios if str(s.difficulty) == "multi_round")
    assert multi / len(dataset) >= 0.25


def test_every_scenario_has_root_cause_evidence():
    """3.5-CON-001: whole-library telemetry-evidence consistency (redundant with
    check_dataset but explicit)."""
    assert check_dataset(_library()) == []


def test_coverage_spread():
    """2.5-UNIT-002: both personas, >=3 products, all 4 root-cause categories."""
    dataset = _library()
    personas = {str(s.ticket.persona) for s in dataset.scenarios}
    products = {s.ticket.azure_product for s in dataset.scenarios}
    categories = {str(s.root_cause.category) for s in dataset.scenarios}
    assert {"windows_admin", "azure_developer"} <= personas
    assert len(products) >= 3
    assert {"arm", "network", "compute_host", "compute_guest"} <= categories


def _broken_scenario() -> Scenario:
    return Scenario.model_validate(
        {
            "scenario_id": "TICKET-18888888",
            "difficulty": "single_round",
            "ticket": {
                "ticket_id": "TICKET-18888888",
                "title": "t",
                "symptom": "s",
                "azure_product": "Azure Virtual Machines",
                "persona": "windows_admin",
                "severity": "Sev3",
                "status": "Active",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "resource_ids": ["/subscriptions/MISSING"],  # not in resources[]
            },
            "resources": [
                {
                    "resource_id": "/subscriptions/OTHER",
                    "resource_type": "Microsoft.Compute/virtualMachines",
                    "name": "n",
                    "resource_group": "rg",
                    "subscription_id": "x",
                    "location": "eastus",
                }
            ],
            "root_cause": {"category": "arm", "summary": "c", "resolution": "r"},
        }
    )


def test_validator_detects_broken_reference():
    """2.5-UNIT-003: the validator flags an unresolved ticket→resource reference."""
    issues = check_dataset(Dataset([_broken_scenario()]))
    assert any("not present in resources" in i for i in issues)


def _scenario_without_evidence() -> Scenario:
    """A well-formed scenario whose telemetry lacks root-cause evidence."""
    return Scenario.model_validate(
        {
            "scenario_id": "TICKET-17777777",
            "difficulty": "single_round",
            "ticket": {
                "ticket_id": "TICKET-17777777",
                "title": "t",
                "symptom": "s",
                "azure_product": "Azure Networking",
                "persona": "azure_developer",
                "severity": "Sev3",
                "status": "Active",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "resource_ids": ["/subscriptions/z"],
            },
            "resources": [
                {
                    "resource_id": "/subscriptions/z",
                    "resource_type": "Microsoft.Compute/virtualMachines",
                    "name": "n",
                    "resource_group": "rg",
                    "subscription_id": "z",
                    "location": "eastus",
                }
            ],
            # network root cause, but no Deny evidence in telemetry:
            "telemetry": {},
            "root_cause": {"category": "network", "summary": "c", "resolution": "r"},
        }
    )


def test_validator_detects_missing_root_cause_evidence():
    """3.5-UNIT-001: the validator flags telemetry with no root-cause evidence."""
    issues = check_dataset(Dataset([_scenario_without_evidence()]))
    assert any("no evidence supporting root_cause" in i for i in issues)
