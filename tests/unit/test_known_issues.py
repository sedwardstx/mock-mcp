"""Unit tests for the known-issues KB (5.1-UNIT-001..004)."""

import pytest

from contoso_support_mcp.config import DEFAULT_FIXTURES_PATH, DEFAULT_KNOWN_ISSUES_PATH
from contoso_support_mcp.data.loader import (
    FixtureValidationError,
    load_known_issues,
    load_scenarios,
)
from contoso_support_mcp.data.models import KnownIssue
from contoso_support_mcp.data.repository import Repository


def _repo() -> Repository:
    return Repository(
        load_scenarios(DEFAULT_FIXTURES_PATH),
        known_issues=load_known_issues(DEFAULT_KNOWN_ISSUES_PATH),
    )


def test_loads_shipped_kb_deterministically():
    """5.1-UNIT-001: KB loads (>=12), ids unique, id-sorted (deterministic)."""
    a = load_known_issues(DEFAULT_KNOWN_ISSUES_PATH)
    b = load_known_issues(DEFAULT_KNOWN_ISSUES_PATH)
    assert len(a) >= 12
    ids = [k.id for k in a]
    assert len(set(ids)) == len(ids)
    assert ids == sorted(ids)
    assert [k.model_dump() for k in a] == [k.model_dump() for k in b]


def test_duplicate_id_rejected(tmp_path):
    """5.1-UNIT-002: a duplicate KB id fails fast."""
    f = tmp_path / "known_issues.yaml"
    f.write_text(
        "known_issues:\n"
        "  - {id: KB-ARM-001, title: t, product: p, category: arm, symptom: s, remediation: r}\n"
        "  - {id: KB-ARM-001, title: t2, product: p, category: arm, symptom: s2, remediation: r2}\n"
    )
    with pytest.raises(FixtureValidationError) as exc:
        load_known_issues(f)
    assert "Duplicate known-issue id" in str(exc.value)


def test_malformed_entry_names_file(tmp_path):
    """5.1-UNIT-002: a malformed entry raises an error naming the file."""
    f = tmp_path / "known_issues.yaml"
    f.write_text("known_issues:\n  - {id: KB-ARM-001, title: t}\n")  # missing required fields
    with pytest.raises(FixtureValidationError) as exc:
        load_known_issues(f)
    assert "known_issues.yaml" in str(exc.value)


def test_repository_search_filters():
    """5.1-UNIT-003: product/category/keyword/combined/no-match."""
    repo = _repo()
    net = repo.search_known_issues(category="network")
    assert net and all(str(k.category) == "network" for k in net)

    vmss = repo.search_known_issues(product="Azure Virtual Machine Scale Sets")
    assert vmss and all(k.product == "Azure Virtual Machine Scale Sets" for k in vmss)

    alloc = repo.search_known_issues(query="allocation")
    assert any(k.id == "KB-ARM-001" for k in alloc)

    combined = repo.search_known_issues(category="arm", product="Azure Virtual Machines")
    assert all(str(k.category) == "arm" and k.product == "Azure Virtual Machines" for k in combined)

    assert repo.search_known_issues(query="zzz-nomatch") == []


def test_model_rejects_bad_category_and_extra_keys():
    """5.1-UNIT-004: strict model + KB id validator."""
    from pydantic import ValidationError

    base = {
        "id": "KB-ARM-001",
        "title": "t",
        "product": "p",
        "category": "arm",
        "symptom": "s",
        "remediation": "r",
    }
    with pytest.raises(ValidationError):
        KnownIssue.model_validate({**base, "category": "martian"})
    with pytest.raises(ValidationError):
        KnownIssue.model_validate({**base, "extra": "x"})
    with pytest.raises(ValidationError):
        KnownIssue.model_validate({**base, "id": "BADID"})


def test_kb_not_loaded_as_scenario():
    """TECH-002: the KB file does not inflate the scenario count."""
    assert len(load_scenarios(DEFAULT_FIXTURES_PATH)) == 103
