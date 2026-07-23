"""In-memory repository: deterministic query methods over the loaded Dataset.

Thin, pure query layer. Ticket methods land in Story 2.2; search, resource, and
telemetry methods are added in later stories.
"""

from __future__ import annotations

from .loader import Dataset
from .models import AzureResource, Ticket


class Repository:
    def __init__(self, dataset: Dataset) -> None:
        self._dataset = dataset

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        scenario = self._dataset.get_by_ticket(ticket_id)
        return scenario.ticket if scenario is not None else None

    def get_resources(self, ticket_id: str) -> list[AzureResource] | None:
        """Resources for a ticket, or None if the ticket does not exist."""
        scenario = self._dataset.get_by_ticket(ticket_id)
        return list(scenario.resources) if scenario is not None else None

    def list_tickets(self, offset: int = 0, limit: int = 50) -> tuple[list[Ticket], int]:
        """Return a page of tickets (in deterministic Dataset order) and the total count."""
        tickets = [s.ticket for s in self._dataset.scenarios]
        total = len(tickets)
        return tickets[offset : offset + limit], total

    def search_tickets(
        self,
        *,
        persona: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        azure_product: str | None = None,
        resource_id: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Ticket], int]:
        """Filter tickets by attributes (AND semantics), preserving Dataset order."""

        def matches(ticket: Ticket) -> bool:
            if persona is not None and ticket.persona != persona:
                return False
            if status is not None and ticket.status != status:
                return False
            if severity is not None and ticket.severity != severity:
                return False
            if azure_product is not None and ticket.azure_product != azure_product:
                return False
            if resource_id is not None and resource_id not in ticket.resource_ids:
                return False
            return True

        matched = [s.ticket for s in self._dataset.scenarios if matches(s.ticket)]
        total = len(matched)
        return matched[offset : offset + limit], total
