"""MCP tools for discovering and reading support tickets."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ..data.models import TICKET_ID_RE, Persona, Severity, Status, Ticket
from ..data.repository import Repository

_MAX_LIMIT = 200

_ENUM_FILTERS = {"persona": Persona, "status": Status, "severity": Severity}


def _summaries(tickets: list[Ticket]) -> list[TicketSummary]:
    return [
        TicketSummary(
            ticket_id=t.ticket_id,
            title=t.title,
            azure_product=t.azure_product,
            persona=t.persona,
            severity=t.severity,
            status=t.status,
        )
        for t in tickets
    ]


class TicketSummary(BaseModel):
    ticket_id: str
    title: str
    azure_product: str
    persona: str
    severity: str
    status: str


class TicketListResult(BaseModel):
    status: str = Field(description="'ok' | 'invalid_request'")
    total: int = Field(description="Total tickets matching (before pagination)")
    offset: int
    limit: int
    tickets: list[TicketSummary]
    message: str | None = Field(default=None, description="Explanation for non-ok status")


class TicketDetailResult(BaseModel):
    status: str = Field(description="'ok' | 'not_found' | 'invalid_request'")
    ticket: Ticket | None = Field(default=None, description="Full ticket when status is 'ok'")
    message: str | None = Field(default=None, description="Explanation for non-ok status")


def register_ticket_tools(mcp: FastMCP, repo: Repository) -> None:
    @mcp.tool(
        description=(
            "Get the full detail of a single support ticket by its id "
            "(format TICKET-XXXXXXXX). Returns status 'ok' with the ticket, or "
            "'not_found' / 'invalid_request' with a message."
        )
    )
    def get_ticket(ticket_id: str) -> TicketDetailResult:
        if not TICKET_ID_RE.match(ticket_id):
            return TicketDetailResult(
                status="invalid_request",
                message=f"ticket_id must match TICKET-XXXXXXXX (8 digits); got {ticket_id!r}",
            )
        ticket = repo.get_ticket(ticket_id)
        if ticket is None:
            return TicketDetailResult(
                status="not_found", message=f"No ticket found for {ticket_id}"
            )
        return TicketDetailResult(status="ok", ticket=ticket)

    @mcp.tool(
        description=(
            "List support tickets (summary view) with pagination. Use offset/limit "
            "to page; results are bounded and returned in a stable order. Returns "
            "total count so you know how many exist."
        )
    )
    def list_tickets(offset: int = 0, limit: int = 50) -> TicketListResult:
        offset = max(0, offset)
        limit = max(1, min(limit, _MAX_LIMIT))
        tickets, total = repo.list_tickets(offset, limit)
        return TicketListResult(
            status="ok", total=total, offset=offset, limit=limit, tickets=_summaries(tickets)
        )

    @mcp.tool(
        description=(
            "Search/filter tickets by attributes (AND semantics), all optional:\n"
            "- persona: one of ['windows_admin', 'azure_developer']\n"
            "- status: one of ['New', 'Active', 'Pending', 'Resolved']\n"
            "- severity: one of ['Sev1', 'Sev2', 'Sev3', 'Sev4']\n"
            "- azure_product: exact product name (e.g. 'Azure Virtual Machines')\n"
            "- resource_id: an ARM resource id the ticket references\n"
            "No matches returns status 'ok' with an empty list. Invalid enum values "
            "return status 'invalid_request' with the allowed values."
        )
    )
    def search_tickets(
        persona: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        azure_product: str | None = None,
        resource_id: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> TicketListResult:
        for value, field in ((persona, "persona"), (status, "status"), (severity, "severity")):
            enum_cls = _ENUM_FILTERS[field]
            allowed = [e.value for e in enum_cls]
            if value is not None and value not in allowed:
                return TicketListResult(
                    status="invalid_request",
                    total=0,
                    offset=offset,
                    limit=limit,
                    tickets=[],
                    message=f"{field} must be one of {allowed}; got {value!r}",
                )
        offset = max(0, offset)
        limit = max(1, min(limit, _MAX_LIMIT))
        tickets, total = repo.search_tickets(
            persona=persona,
            status=status,
            severity=severity,
            azure_product=azure_product,
            resource_id=resource_id,
            offset=offset,
            limit=limit,
        )
        return TicketListResult(
            status="ok", total=total, offset=offset, limit=limit, tickets=_summaries(tickets)
        )
