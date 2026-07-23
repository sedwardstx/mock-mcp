"""MCP tools for discovering and reading support tickets."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ..data.models import TICKET_ID_RE, Ticket
from ..data.repository import Repository

_MAX_LIMIT = 200


class TicketSummary(BaseModel):
    ticket_id: str
    title: str
    azure_product: str
    persona: str
    severity: str
    status: str


class TicketListResult(BaseModel):
    status: str = Field(description="'ok'")
    total: int = Field(description="Total tickets available")
    offset: int
    limit: int
    tickets: list[TicketSummary]


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
        summaries = [
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
        return TicketListResult(
            status="ok", total=total, offset=offset, limit=limit, tickets=summaries
        )
