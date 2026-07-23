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


def test_search_single_filter_persona():
    tickets, total = _repo().search_tickets(persona="windows_admin")
    assert total >= 1
    assert all(t.persona == "windows_admin" for t in tickets)


def test_search_combined_filters_and_semantics():
    repo = _repo()
    combined, ctotal = repo.search_tickets(
        persona="windows_admin", azure_product="Azure Virtual Machines"
    )
    # Every result satisfies BOTH filters (AND semantics)...
    assert all(
        t.persona == "windows_admin" and t.azure_product == "Azure Virtual Machines"
        for t in combined
    )
    # ...and the combined set is no larger than either single-filter set.
    _, persona_total = repo.search_tickets(persona="windows_admin")
    _, product_total = repo.search_tickets(azure_product="Azure Virtual Machines")
    assert ctotal <= min(persona_total, product_total)


def test_search_no_match_returns_empty():
    tickets, total = _repo().search_tickets(status="Resolved")
    assert total == 0
    assert tickets == []


def test_search_deterministic_order():
    tickets, _ = _repo().search_tickets(persona="windows_admin")
    ids = [t.ticket_id for t in tickets]
    assert ids == sorted(ids)


def test_get_resources_known_ticket():
    resources = _repo().get_resources("TICKET-10000001")
    assert resources is not None
    assert len(resources) == 1
    assert resources[0].resource_type == "Microsoft.Compute/virtualMachines"


def test_get_resources_unknown_ticket_returns_none():
    assert _repo().get_resources("TICKET-00000000") is None
