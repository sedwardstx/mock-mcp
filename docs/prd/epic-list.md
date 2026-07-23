# Epic List

- **Epic 1 — Foundation & Connectable MCP Server:** Establish the Python project, MCP server scaffold with dual transport (stdio + network), configuration, a health/identity tool, and run docs — delivering a server students can connect to and confirm.
- **Epic 2 — Mock Data Model & Ticket Tools:** Define the scenario/ticket/resource data model, expose ticket tools (list, search/filter, get) and the ticket→resource pivot, and author a first batch of scenarios — establishing the data foundation and ticket-browsing value.
- **Epic 3 — Kusto Telemetry Tools & Correlation:** Add Kusto-style query tools (ARM traces, Network logs, Compute host + Windows guest logs for VM/VMSS) returning scenario-correlated telemetry, backfill telemetry for existing scenarios, and author more scenarios including the first multi-round ones — enabling full end-to-end RCA.
- **Epic 4 — Full Scenario Library & Guided Prompts:** Grow the library to 100+ scenarios hitting the target single-shot vs. ≥25% multi-round distribution, validate consistency at scale, and author the crafted MCP prompts for scoping / follow-up / investigation / RCA — completing the MVP.
