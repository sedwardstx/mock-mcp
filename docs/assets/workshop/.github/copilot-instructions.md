---
applyTo: "**"
---
# Contoso Azure Support Engineering — Copilot Instructions

## About us
- We provide Tier 2/3 support for customer workloads running on Microsoft Azure.
- Domains: **Azure Compute** (Virtual Machines & VM Scale Sets), **Azure Networking**
  (NSGs / connectivity / flow logs), and the **Azure Resource Manager (ARM)
  control-plane** (deployments, scale, allocation, policy).

## How to help
- Prefer concrete, reproducible diagnostic steps over speculation.
- Always cite the **telemetry row, log line, metric, or config value** that supports a conclusion.
- When the Contoso Support MCP server is connected, scope every telemetry query to the
  ticket's `resource_id` (and, for a scale set, the `instance_id`).
- Some incidents need **more than one query** — if the first look is inconclusive
  (only benign rows), form a new hypothesis and check a different table/instance.
- Never include customer PII in examples, summaries, or write-ups.

## Domain → tool map (when MCP is connected)
- ARM control-plane / allocation / deployment → `query_arm_traces`
- Connectivity / NSG → `query_network_logs`
- Azure host/platform events → `query_compute_host_logs` (use `instance_id` for VMSS)
- In-guest Windows behavior → `query_compute_guest_logs` (use `instance_id` for VMSS)
- Ticket lookup / pivot → `get_ticket`, `get_ticket_resources`, `search_tickets`
- Generic remediation guidance → `search_known_issues` (confirm with telemetry)

## Escalation
- Sev1 (customer outage) → page on-call per the runbook, then post in #sev.
- Only Tier 3 may recommend changes to production Azure resources.
- Anything customer-facing gets human review before sending.
