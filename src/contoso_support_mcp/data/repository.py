"""In-memory repository: deterministic query methods over the loaded Dataset.

Thin, pure query layer. Ticket methods land in Story 2.2; search, resource, and
telemetry methods are added in later stories.
"""

from __future__ import annotations

from .loader import Dataset
from .models import Ticket


class Repository:
    def __init__(self, dataset: Dataset) -> None:
        self._dataset = dataset

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        scenario = self._dataset.get_by_ticket(ticket_id)
        return scenario.ticket if scenario is not None else None

    def list_tickets(self, offset: int = 0, limit: int = 50) -> tuple[list[Ticket], int]:
        """Return a page of tickets (in deterministic Dataset order) and the total count."""
        tickets = [s.ticket for s in self._dataset.scenarios]
        total = len(tickets)
        return tickets[offset : offset + limit], total
