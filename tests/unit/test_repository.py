"""Unit tests for the ticket repository (2.2-UNIT-001/002/003)."""

from contoso_support_mcp.config import DEFAULT_FIXTURES_PATH
from contoso_support_mcp.data.loader import load_scenarios
from contoso_support_mcp.data.repository import Repository


def _repo() -> Repository:
    return Repository(load_scenarios(DEFAULT_FIXTURES_PATH))


def test_get_ticket_known():
    ticket = _repo().get_ticket("TICKET-10000001")
    assert ticket is not None
    assert ticket.ticket_id == "TICKET-10000001"


def test_get_ticket_unknown_returns_none():
    assert _repo().get_ticket("TICKET-00000000") is None


def test_list_tickets_pagination_and_total():
    page, total = _repo().list_tickets(offset=0, limit=2)
    assert total >= 3
    assert len(page) == 2


def test_list_tickets_deterministic_order():
    page, _ = _repo().list_tickets(offset=0, limit=100)
    ids = [t.ticket_id for t in page]
    assert ids == sorted(ids)
