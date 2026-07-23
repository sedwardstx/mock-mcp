"""Crafted MCP prompts guiding the diagnostic workflow.

These prompts teach a connected agent to use the server's tools effectively:
scope a ticket, ask follow-ups, investigate iteratively (including multi-round),
and produce a root-cause analysis. Registered as MCP prompts, discoverable and
parameterized by ticket id.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

_TOOLS_LINE = (
    "Available tools: get_ticket, list_tickets, search_tickets, get_ticket_resources, "
    "query_arm_traces, query_network_logs, query_compute_host_logs, query_compute_guest_logs."
)


def register_diagnostic_prompts(mcp: FastMCP) -> None:
    @mcp.prompt(
        description=(
            "Scope/triage a support ticket: read it, identify the product, persona, "
            "severity, and affected resource before investigating."
        )
    )
    def triage_ticket(ticket_id: str) -> str:
        return (
            f"You are a Contoso Azure support engineer triaging ticket {ticket_id}.\n\n"
            f"1. Call get_ticket with ticket_id={ticket_id} to read the reported symptom, "
            "Azure product, customer persona, and severity.\n"
            f"2. Call get_ticket_resources with ticket_id={ticket_id} to identify the affected "
            "Azure resource(s) and note each resource_id (you will scope telemetry "
            "queries to it).\n"
            "3. Summarize, in two sentences: what the customer reports, which resource is "
            "affected, and which telemetry domain (ARM control-plane, Network, or Compute "
            "host/guest) you "
            "suspect first and why.\n\n"
            f"{_TOOLS_LINE}"
        )

    @mcp.prompt(
        description=(
            "Full diagnostic workflow for a ticket: scope, ask follow-ups, investigate "
            "iteratively across telemetry (including a second round if inconclusive), and "
            "produce an RCA. Best starting prompt for a lab."
        )
    )
    def investigate_incident(ticket_id: str) -> str:
        return (
            f"You are diagnosing Contoso support ticket {ticket_id}. Work methodically.\n\n"
            "STEP 1 — Scope: get_ticket and get_ticket_resources for "
            f"{ticket_id}. Note the affected resource_id (and, for a scale set (VMSS), the "
            "instance ids).\n"
            "STEP 2 — Follow-up questions: before querying, state 1-2 clarifying questions you "
            "would ask the customer (e.g. exact time window, whether a recent change was made).\n"
            "STEP 3 — Investigate: choose the telemetry tool for your suspected domain and query "
            "it scoped to the resource_id (and a time_range if known):\n"
            "  - ARM control-plane issues  -> query_arm_traces\n"
            "  - connectivity / NSG issues -> query_network_logs\n"
            "  - Azure host/platform events -> query_compute_host_logs "
            "(use instance_id for VMSS)\n"
            "  - in-guest Windows issues    -> query_compute_guest_logs "
            "(use instance_id for VMSS)\n"
            "STEP 4 — Iterate if needed: if the first query is inconclusive (only benign rows), "
            "form a new hypothesis and query a DIFFERENT table or instance. Some incidents require "
            "multiple rounds — do not stop at the first look.\n"
            "STEP 5 — RCA: state the root cause and either the resolution or the recommended next "
            "steps, citing the specific telemetry rows that support your conclusion.\n\n"
            f"{_TOOLS_LINE}"
        )

    @mcp.prompt(
        description=(
            "Produce a concise root-cause analysis writeup for a ticket once you have "
            "gathered the supporting telemetry."
        )
    )
    def summarize_rca(ticket_id: str) -> str:
        return (
            f"Write a concise RCA for ticket {ticket_id}. Include: (1) the customer-reported "
            "symptom, (2) the affected resource, (3) the root cause, (4) the specific telemetry "
            "evidence (tool + the key rows) that supports it, and (5) the resolution or next "
            "steps. If the investigation required multiple rounds, briefly note which query was "
            "inconclusive and which one revealed the cause."
        )
