"""Unit tests for the common telemetry query semantic (3.1-UNIT-005..007)."""

import pytest

from contoso_support_mcp.data.models import NetworkLogRow
from contoso_support_mcp.data.query import TimeRangeError, parse_time_range, query_rows

RID_A = "/subscriptions/x/rg/vmA"
RID_B = "/subscriptions/x/rg/vmB"


def _rows() -> list[NetworkLogRow]:
    return [
        NetworkLogRow(time_generated="2026-06-02T14:00:00Z", resource_id=RID_A, action="Allow"),
        NetworkLogRow(time_generated="2026-06-02T14:30:00Z", resource_id=RID_A, action="Deny"),
        NetworkLogRow(time_generated="2026-06-02T15:30:00Z", resource_id=RID_A, action="Allow"),
        NetworkLogRow(time_generated="2026-06-02T14:30:00Z", resource_id=RID_B, action="Deny"),
    ]


def test_scopes_by_resource_id():
    """3.1-UNIT-005: only rows for the requested resource are returned."""
    result = query_rows(_rows(), resource_id=RID_A)
    assert len(result) == 3
    assert all(r.resource_id == RID_A for r in result)


def test_time_range_and_filter_boundary():
    """3.1-UNIT-006: time-range bounds are inclusive; field filters apply."""
    in_window = query_rows(
        _rows(), resource_id=RID_A, time_range="2026-06-02T14:00:00Z/2026-06-02T15:00:00Z"
    )
    assert len(in_window) == 2  # 14:00 and 14:30, not 15:30

    denies = query_rows(_rows(), resource_id=RID_A, filters={"action": "Deny"})
    assert len(denies) == 1
    assert denies[0].action == "Deny"


def test_deterministic_order_preserved():
    """3.1-UNIT-007: output preserves input order deterministically."""
    a = query_rows(_rows(), resource_id=RID_A)
    b = query_rows(_rows(), resource_id=RID_A)
    assert [r.time_generated for r in a] == [r.time_generated for r in b]


def test_bad_time_range_raises():
    with pytest.raises(TimeRangeError):
        parse_time_range("not-a-range")
