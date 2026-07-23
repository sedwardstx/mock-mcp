"""MCP tool to pivot from a ticket to its associated Azure resource(s)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ..data.models import TICKET_ID_RE, AzureResource
from ..data.repository import Repository


class ResourceResult(BaseModel):
    status: str = Field(description="'ok' | 'not_found' | 'invalid_request'")
    resources: list[AzureResource] = Field(default_factory=list)
    message: str | None = Field(default=None, description="Explanation for non-ok status")


def register_resource_tools(mcp: FastMCP, repo: Repository) -> None:
    @mcp.tool(
        description=(
            "Get the Azure resource(s) associated with a ticket (format "
            "TICKET-XXXXXXXX). Returns each resource's ARM resource_id, "
            "resource_type, subscription, and (for VMSS) instance ids. Use the "
            "returned resource_id as the scoping input for the telemetry query "
            "tools. Returns 'not_found' for an unknown ticket, 'invalid_request' "
            "for a malformed id, and 'ok' with an empty list if the ticket has no "
            "associated resources."
        )
    )
    def get_ticket_resources(ticket_id: str) -> ResourceResult:
        if not TICKET_ID_RE.match(ticket_id):
            return ResourceResult(
                status="invalid_request",
                message=f"ticket_id must match TICKET-XXXXXXXX (8 digits); got {ticket_id!r}",
            )
        resources = repo.get_resources(ticket_id)
        if resources is None:
            return ResourceResult(
                status="not_found", message=f"No ticket found for {ticket_id}"
            )
        return ResourceResult(status="ok", resources=resources)
