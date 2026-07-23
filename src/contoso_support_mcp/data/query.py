"""Common query semantic shared by all telemetry tools.

Deterministic filtering of telemetry rows by resource id, optional time range,
optional VMSS instance, and optional log-type-appropriate field filters.
No randomness or wall-clock — results depend only on inputs and fixtures.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel

RowT = TypeVar("RowT", bound=BaseModel)


class TimeRangeError(ValueError):
    """Raised when a time_range string cannot be parsed."""


def parse_time_range(time_range: str | None) -> tuple[datetime | None, datetime | None]:
    """Parse a 'startISO/endISO' range. Either side may be blank for open-ended."""
    if time_range is None or time_range == "":
        return None, None
    if "/" not in time_range:
        raise TimeRangeError(
            "time_range must be 'START/END' ISO-8601 (either side may be blank); "
            f"got {time_range!r}"
        )
    start_str, end_str = time_range.split("/", 1)
    try:
        start = datetime.fromisoformat(start_str.replace("Z", "+00:00")) if start_str else None
        end = datetime.fromisoformat(end_str.replace("Z", "+00:00")) if end_str else None
    except ValueError as exc:
        raise TimeRangeError(
            f"Invalid ISO-8601 datetime in time_range {time_range!r}: {exc}"
        ) from exc
    return start, end


def query_rows(
    rows: Iterable[RowT],
    *,
    resource_id: str,
    time_range: str | None = None,
    instance_id: str | None = None,
    filters: dict[str, object] | None = None,
) -> list[RowT]:
    """Return the subset of rows scoped to a resource (and optional time/instance/filters).

    Preserves the input order (deterministic). Rows carry timezone-aware
    `time_generated`; the range bounds are compared inclusively.
    """
    start, end = parse_time_range(time_range)
    result: list[RowT] = []
    for row in rows:
        if row.resource_id != resource_id:
            continue
        if instance_id is not None and getattr(row, "instance_id", "") != instance_id:
            continue
        ts: datetime = row.time_generated  # type: ignore[attr-defined]
        if start is not None and ts < start:
            continue
        if end is not None and ts > end:
            continue
        if filters and not all(getattr(row, key, None) == value for key, value in filters.items()):
            continue
        result.append(row)
    return result


def as_dicts(rows: Sequence[BaseModel]) -> list[dict]:
    """Serialize rows to JSON-friendly dicts (for tool responses)."""
    return [r.model_dump(mode="json") for r in rows]
