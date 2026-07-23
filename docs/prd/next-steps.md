# Next Steps

## UX Expert Prompt

Not applicable. The Contoso Support Ticketing MCP Server is a headless MCP server with no user interface; there is no UX/UI work for this MVP. Prompt-authoring for agent guidance is covered within the PRD (Epic 4).

## Architect Prompt

Please create the architecture for the **Contoso Support Ticketing MCP Server** using this PRD (`docs/prd.md`) as input. This is a fully-mocked, offline Python MCP server for a classroom. Key design work: (1) define concrete mock **Kusto table schemas** (columns) for ARM control-plane traces, Network logs, and Compute host and Windows guest logs (VM and VMSS) that are believable approximations of real Azure schemas; (2) design the **scenario/ticket/resource/telemetry data model** and fixture format that scales to 100+ scenarios without code changes and models **multi-round investigation** (evidence distributed so follow-up queries reveal new evidence); (3) specify the **Python MCP server** structure with dual transport (stdio + streamable HTTP/SSE) from one codebase, guaranteeing deterministic responses; (4) choose the **packaging/run** approach (e.g., uv/pip/script) with a single command per mode; and (5) address classroom-scale concurrency for the network transport. Honor the constraints: no external services/credentials, all data embedded, read-only tickets, Windows-only guest logs, MCP-spec compliant. Flag any assumptions for confirmation.
