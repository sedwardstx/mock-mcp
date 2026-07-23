# Requirements

## Functional

- FR1: The system SHALL run as a Model Context Protocol (MCP) server implemented in Python that connecting AI agents/Skills can discover and invoke tools, prompts, and resources against.
- FR2: The server SHALL support two transport modes selectable at startup: (a) local **stdio** for offline student self-hosting, and (b) a **network transport** (streamable HTTP/SSE over a configurable host:port) for a single instructor-hosted deployment serving the class.
- FR3: The server SHALL expose ticket tools to **list**, **search/filter**, and **get** support tickets, where every ticket identifier uses the format `TICKET-XXXXXXXX` (8 digits).
- FR4: Ticket search SHALL support filtering by attributes such as Azure product/service, ticket status, severity, customer persona (Windows admin vs. Azure developer), and affected resource.
- FR5: Each ticket SHALL contain realistic content — a customer-reported symptom/problem statement, affected Azure product/platform, associated Azure resource(s) and subscription, severity, status, and timestamps.
- FR6: The server SHALL expose a tool to retrieve the Azure resource(s) and subscription context associated with a given ticket, so an agent can pivot from a ticket to its resources.
- FR7: The server SHALL expose Kusto-style telemetry query tools covering, at minimum: **ARM control-plane traces**, **Network logs**, **Compute host/platform logs** (VM and VMSS), and **Compute Windows guest logs** (VM and VMSS).
- FR8: Telemetry query tools SHALL accept scoping parameters (e.g., resource identifier, time range, and log-type-appropriate filters) and return only the rows relevant to that scope.
- FR9: The mock dataset SHALL contain **at least 100 distinct problem scenarios**, each linking a ticket → symptom → affected resource(s) → correlated telemetry across the relevant Kusto tables → a defined root cause and resolution/next-step.
- FR10: At least **25% of scenarios** SHALL require **multiple rounds of investigation** — i.e., the initial ticket symptom is insufficient, and the agent must query telemetry, form a hypothesis, and query further (revealing new evidence) to reach the root cause.
- FR11: For identical inputs, all tools SHALL return **deterministic, identical responses** across sessions and machines (no randomization at query time).
- FR12: The server SHALL expose crafted MCP **prompts** that guide a student's agent through the diagnostic workflow: scoping the problem, asking follow-up questions, iterative investigation across tools, and producing an RCA that either resolves the issue or documents next steps.
- FR13: Telemetry returned by the tools SHALL be internally consistent with the ticket and root cause for a given scenario (e.g., the logs contain evidence that plausibly supports the defined root cause), including realistic noise where appropriate.
- FR14: The server SHALL provide a lightweight health/identity tool (e.g., a status or "about" tool) so students can confirm a successful connection before beginning a lab.
- FR15: Tool inputs and outputs SHALL be described with clear MCP schemas and descriptions sufficient for an agent to select and call the right tool without external documentation.
- FR16: The server SHALL expose a read-only **known-issues KB tool** (`search_known_issues`) returning **generic** Azure remediation guidance filterable by product, root-cause category, and keyword. Its data SHALL be a separate curated dataset, decoupled from per-scenario root causes, so it does not reveal the per-ticket grading answer.
- FR17: The repository SHALL ship an **Azure-themed Copilot workshop starter scaffold** enabling the Day-1 labs: custom instructions, reusable prompt files, an agent skill (procedure + helper script + reference table), and sample logs/tickets/queries.
- FR18: The repository SHALL ship **Copilot custom agents** — three domain specialists (compute, network, control-plane), a routing coordinator, and a ticket-writer — plus a `.vscode/mcp.json` that wires this server, supporting the Day-2 MCP + agent labs.
- FR19: The participant workbook SHALL be **Azure-themed** and its MCP labs SHALL target this server — correct `.vscode/mcp.json`, real `TICKET-XXXXXXXX` ids, and this server's actual tool names.

## Non Functional

- NFR1: The server SHALL run entirely offline with no external network calls, cloud services, credentials, or Azure subscriptions required.
- NFR2: All ticket and telemetry data SHALL be mocked and embedded/bundled with the server (e.g., in-memory or local fixture files); no real customer or production data is present.
- NFR3: Tool responses SHALL typically return in under one second on a standard laptop.
- NFR4: In instructor-hosted network mode, the server SHALL support concurrent connections from a full classroom of students without external services or degradation.
- NFR5: The server SHALL run cross-platform where feasible, with Windows as the primary supported instructor/student platform.
- NFR6: Startup SHALL be simple — a single documented command per transport mode — enabling class-wide time-to-first-successful-tool-call of under 10 minutes.
- NFR7: The mock guest-OS telemetry SHALL be Windows-only for the MVP.
- NFR8: The server SHALL conform to the MCP specification such that any MCP-compatible agent framework or Skill can connect and use its tools/prompts.
- NFR9: The scenario dataset SHALL be authored/structured for maintainability and extensibility, allowing new scenarios to be added without code changes to the server core.
- NFR10: Tickets SHALL be read-only in the MVP (no create/update/resolve operations).
- NFR11: Workshop starter assets and sample data SHALL contain no secrets and no customer PII; the server SHALL require no credentials to run in either transport.
