"""MCP tools for querying mock Kusto telemetry tables.

All tools are thin wrappers over `Repository.query_telemetry`, which uses the
shared `query_rows` semantic (resource + time-range + instance + filters).
Tools are added incrementally across Stories 3.2 (ARM), 3.3 (Network), and
3.4 (Compute host + guest).
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ..data.query import TimeRangeError, as_dicts
from ..data.repository import Repository


class TelemetryResult(BaseModel):
    status: str = Field(description="'ok' | 'invalid_request'")
    resource_id: str
    table: str
    count: int
    rows: list[dict]
    message: str | None = Field(default=None, description="Explanation for non-ok status")


def _query(
    repo: Repository,
    *,
    table: str,
    resource_id: str,
    time_range: str | None,
    instance_id: str | None = None,
    filters: dict[str, object] | None = None,
) -> TelemetryResult:
    active_filters = {k: v for k, v in (filters or {}).items() if v is not None}
    try:
        rows = repo.query_telemetry(
            table,
            resource_id,
            time_range=time_range,
            instance_id=instance_id,
            filters=active_filters or None,
        )
    except TimeRangeError as exc:
        return TelemetryResult(
            status="invalid_request", resource_id=resource_id, table=table, count=0, rows=[],
            message=str(exc),
        )
    dicts = as_dicts(rows)
    return TelemetryResult(
        status="ok", resource_id=resource_id, table=table, count=len(dicts), rows=dicts
    )


def register_telemetry_tools(mcp: FastMCP, repo: Repository) -> None:
    @mcp.tool(
        description=(
            "Query mock ARM control-plane traces (Azure Activity Log style) for a "
            "resource. Params: resource_id (required ARM id), time_range "
            "('START/END' ISO-8601, optional), activity_status (optional filter, "
            "e.g. 'Failed'). Returns rows with columns incl. operation_name, "
            "http_status_code, activity_status, sub_status, properties. Empty match "
            "returns status 'ok' with no rows."
        )
    )
    def query_arm_traces(
        resource_id: str,
        time_range: str | None = None,
        activity_status: str | None = None,
    ) -> TelemetryResult:
        return _query(
            repo,
            table="arm_control_plane_traces",
            resource_id=resource_id,
            time_range=time_range,
            filters={"activity_status": activity_status},
        )
