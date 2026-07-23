"""Integration tests for the guided diagnostic prompts (4.3-INT-001..004)."""

from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from contoso_support_mcp.server import build_server


async def test_prompts_are_discoverable():
    """4.3-INT-001: the diagnostic prompts are listed with declared arguments."""
    async with client_session(build_server()) as client:
        listed = await client.list_prompts()
        names = {p.name for p in listed.prompts}
        assert {"triage_ticket", "investigate_incident", "summarize_rca"} <= names
        # 4.3-INT-004: ticket_id argument is declared.
        investigate = next(p for p in listed.prompts if p.name == "investigate_incident")
        assert "ticket_id" in {a.name for a in (investigate.arguments or [])}


async def test_investigate_prompt_references_ticket_and_tools():
    """4.3-INT-002: get_prompt returns well-formed content referencing ticket + tools."""
    async with client_session(build_server()) as client:
        result = await client.get_prompt("investigate_incident", {"ticket_id": "TICKET-10000001"})
        text = " ".join(m.content.text for m in result.messages)
        assert "TICKET-10000001" in text
        assert "get_ticket" in text
        assert "get_ticket_resources" in text
        assert "query_arm_traces" in text
        assert "query_compute_guest_logs" in text


async def test_investigate_prompt_encourages_multi_round():
    """4.3-INT-003: the workflow prompt instructs iterative/multi-round investigation."""
    async with client_session(build_server()) as client:
        result = await client.get_prompt("investigate_incident", {"ticket_id": "TICKET-10000026"})
        text = " ".join(m.content.text for m in result.messages).lower()
        assert "inconclusive" in text
        assert "multiple rounds" in text or "iterate" in text
