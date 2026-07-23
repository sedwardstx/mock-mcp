"""In-memory repository: deterministic query methods over the loaded Dataset.

Thin, pure query layer. Ticket methods land in Story 2.2; search, resource, and
telemetry methods are added in later stories.
"""

from __future__ import annotations

from pydantic import BaseModel

from .loader import Dataset
from .models import AzureResource, Ticket
from .query import query_rows


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

    def get_resource(self, resource_id: str) -> AzureResource | None:
        """Look up a single Azure resource by its ARM id across all scenarios."""
        for scenario in self._dataset.scenarios:
            for resource in scenario.resources:
                if resource.resource_id == resource_id:
                    return resource
        return None

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

    def query_telemetry(
        self,
        table: str,
        resource_id: str,
        *,
        time_range: str | None = None,
        instance_id: str | None = None,
        filters: dict[str, object] | None = None,
    ) -> list[BaseModel]:
        """Query one telemetry table for a resource via the shared query semantic.

        `table` is a Telemetry attribute name (e.g. 'arm_control_plane_traces').
        Gathers that table's rows across all scenarios (deterministic order),
        then scopes by resource_id / time_range / instance_id / filters.
        """
        rows: list[BaseModel] = []
        for scenario in self._dataset.scenarios:
            rows.extend(getattr(scenario.telemetry, table))
        return query_rows(
            rows,
            resource_id=resource_id,
            time_range=time_range,
            instance_id=instance_id,
            filters=filters,
        )
