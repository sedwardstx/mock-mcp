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


def test_batch_size_in_range():
    """2.5-UNIT-001: seed batch size is in the ~20-30 range."""
    assert 20 <= len(_library()) <= 30


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
