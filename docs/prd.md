# Contoso Support Ticketing MCP Server Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Deliver a fully-mocked, offline-capable Python MCP server that students can connect AI Agents and Skills to during hands-on labs.
- Emulate a realistic Azure support-engineering backend: `TICKET-XXXXXXXX` incidents plus correlated Kusto telemetry (ARM, Network, Compute).
- Provide a curated library of **≥ 100 distinct problem scenarios** with matching symptoms, correlated logs, and defined root causes.
- Ensure a meaningful subset (≥ 25%) of scenarios require **multiple rounds of investigation and tool calls** to reach a root-cause analysis (RCA).
- Support two deployment modes: **student-hosted local (stdio, no network)** and **instructor-hosted over the network**.
- Guarantee deterministic, repeatable tool responses so labs are consistent and gradeable across all student machines.
- Ship crafted MCP **prompts** that guide student agents through scoping, follow-up questioning, iterative investigation, and RCA.
- Reduce classroom setup/connection time to under 10 minutes for a class of students.

### Background Context

Students learning to build AI Agents and Skills need a realistic, safe, and reliable backend to practice tool orchestration and multi-step diagnostic reasoning. Today they are limited to trivial "hello world" MCP servers (too shallow to teach real agent planning) or live systems (which require Azure subscriptions, incur cost, expose real data, and break in flaky classroom networks). Neither teaches the core skill: reasoning across multiple correlated data sources to connect a customer-reported symptom to its underlying platform root cause.

The Contoso Support Ticketing MCP Server closes that gap. It presents a believable "Contoso Support" backend whose customers — a mix of Windows administrators and Azure developers — file incidents against Azure products and platforms. Behind each ticket sits mocked, correlated telemetry across Kusto tables (ARM control-plane traces, Network logs, and Compute logs for VMs/VMSS including platform-host and Windows guest logs). All data is mocked and embedded, so the server runs entirely offline on a laptop with zero external dependencies, giving students an authentic Azure-support feel in a controlled, deterministic sandbox.

### Change Log

| Date       | Version | Description                        | Author       |
|------------|---------|------------------------------------|--------------|
| 2026-07-23 | 1.0     | Initial PRD draft from Project Brief | John (PM)  |

## Requirements

### Functional

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

### Non Functional

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

## Technical Assumptions

### Repository Structure: Monorepo

A single repository holds the MCP server code, the mock data/scenario library, prompt templates, and classroom run/setup docs. This keeps the teaching artifact self-contained and easy to distribute to students as one unit.

### Service Architecture

**Monolith** — a single Python MCP server process. The server exposes tools/prompts and reads from an embedded mock data layer. There is a clear internal separation between the **MCP surface** (tool/prompt handlers) and the **mock data layer** (scenario/ticket/telemetry fixtures + query logic), so the dataset can grow independently of the server core. The server supports both stdio and network (streamable HTTP/SSE) transports from the same codebase. Stateless request/response; deterministic responses keyed on inputs.

### Testing Requirements

**Unit + Integration.** Unit tests cover the data-layer query logic and determinism guarantees. Integration tests exercise the MCP tools end-to-end (a test client invokes each tool and validates schemas, scoping, and scenario/telemetry consistency). A lightweight harness/script to manually invoke tools locally is desirable for authoring and classroom troubleshooting. Given the teaching purpose, a test that validates each scenario is internally consistent (ticket ↔ telemetry ↔ root cause) is valuable.

### Additional Technical Assumptions and Requests

- Language/runtime: **Python**, using the official Python MCP SDK.
- Transports: **stdio** (student local) and **streamable HTTP/SSE** (instructor network hosting) from a single server implementation.
- Data storage: embedded fixture files (e.g., JSON/YAML) and/or in-memory structures; no external database.
- Kusto emulation: mock tables approximate real Azure log schemas (ARM, Network, Compute host/guest) closely enough to be believable; exact schemas/columns to be defined with the Architect.
- Determinism: no `random`/time-of-day-dependent behavior in query responses; any variability must be seeded and reproducible.
- Distribution: runnable via a documented single command per transport mode (packaging approach — e.g., `uv`/`pip`/script — to be decided with the Architect).
- Classroom auth for network mode: assumed an open local endpoint is acceptable for MVP; revisit if identity is required.

## Epic List

- **Epic 1 — Foundation & Connectable MCP Server:** Establish the Python project, MCP server scaffold with dual transport (stdio + network), configuration, a health/identity tool, and run docs — delivering a server students can connect to and confirm.
- **Epic 2 — Mock Data Model & Ticket Tools:** Define the scenario/ticket/resource data model, expose ticket tools (list, search/filter, get) and the ticket→resource pivot, and author a first batch of scenarios — establishing the data foundation and ticket-browsing value.
- **Epic 3 — Kusto Telemetry Tools & Correlation:** Add Kusto-style query tools (ARM traces, Network logs, Compute host + Windows guest logs for VM/VMSS) returning scenario-correlated telemetry, backfill telemetry for existing scenarios, and author more scenarios including the first multi-round ones — enabling full end-to-end RCA.
- **Epic 4 — Full Scenario Library & Guided Prompts:** Grow the library to 100+ scenarios hitting the target single-shot vs. ≥25% multi-round distribution, validate consistency at scale, and author the crafted MCP prompts for scoping / follow-up / investigation / RCA — completing the MVP.

## Epic 1 Foundation & Connectable MCP Server

**Epic Goal:** Stand up the Python project and a working MCP server that students and instructors can actually connect to, in both deployment modes. By the end of this epic the server starts via a single documented command in either **stdio** (student-local, offline) or **network** (instructor-hosted) mode, exposes a health/identity tool so a connecting agent can confirm the link, and ships with the project scaffolding, test harness, and run docs that every later epic builds on.

### Story 1.1 Project Scaffold & Health Tool (stdio)

As an instructor setting up the teaching server,
I want a Python MCP server project that starts over stdio and exposes a health/identity tool,
so that I have a runnable, connectable foundation and can confirm an agent is talking to the right server.

#### Acceptance Criteria

1: A Python project is initialized with dependency management (e.g., pyproject/`uv` or `pip`), the official Python MCP SDK as a dependency, and a documented project structure that separates the MCP surface from the (future) mock data layer.
2: A unit + integration test harness is configured and runnable via a single command, with at least one passing smoke test.
3: The server runs over **stdio** via a single documented command and is discoverable by a standard MCP client.
4: The server exposes a health/identity tool (e.g., `get_server_info` / `ping`) that returns server name, version, and a static status, with a clear MCP schema and description.
5: An integration test connects an MCP client over stdio, invokes the health tool, and asserts the returned identity/status.
6: A brief README section documents how to install dependencies and run the server over stdio.

### Story 1.2 Network Transport Mode (Instructor Hosting)

As an instructor hosting the server for the class,
I want to run the same server over a network transport,
so that many students can connect to a single instructor-hosted endpoint.

#### Acceptance Criteria

1: The server supports a **network transport** (streamable HTTP/SSE) exposing the identical tool surface as stdio mode, from the same codebase.
2: The transport mode is selectable at startup (CLI flag and/or config), with host and port configurable.
3: A remote MCP client can connect over the network transport, invoke the health/identity tool, and receive the correct response.
4: The server accepts multiple concurrent client connections and responds correctly to each (validated by a test simulating concurrent clients).
5: An integration test exercises the health tool over the network transport.
6: No external services, credentials, or internet access are required to run the network mode.

### Story 1.3 Configuration & Classroom Run Documentation

As an instructor or student preparing for a lab,
I want clear configuration and a single documented command per mode,
so that I can start the correct server for my scenario in under 10 minutes.

#### Acceptance Criteria

1: Configuration (transport mode, host, port, and any core settings) is settable via a documented mechanism (CLI flags and/or a config file) with sensible defaults.
2: The documentation provides one copy-paste command to start **student-local stdio** mode and one to start **instructor-hosted network** mode.
3: The docs describe how a student confirms a successful connection using the health/identity tool.
4: Invalid configuration (e.g., a bad port) produces a clear, actionable error message rather than a stack trace.
5: The run docs are validated by following them from a clean environment to a successful health-tool call in both modes.

## Epic 2 Mock Data Model & Ticket Tools

**Epic Goal:** Give the server a realistic support-ticketing surface. This epic defines the scenario/ticket/resource data model and a deterministic loader for embedded fixtures, exposes the ticket tools (list, search/filter, get) plus the ticket→resource pivot, and authors a first batch of ~20–30 scenarios. By the end, a student's agent can browse and filter believable `TICKET-XXXXXXXX` incidents and pivot from a ticket to its affected Azure resource(s) — the foundation the telemetry tools will correlate against.

### Story 2.1 Scenario & Ticket Data Model + Deterministic Loader

As a server developer,
I want a well-defined scenario/ticket/resource data model with a deterministic fixture loader,
so that all tools read from one consistent, extensible source and later scenarios can be added without code changes.

#### Acceptance Criteria

1: A documented data model defines a **scenario** and its linked entities: ticket (id, product/service, symptom/problem statement, severity, status, customer persona, timestamps), affected Azure resource(s) and subscription, references to correlated telemetry (populated in Epic 3), and a defined root cause + resolution/next-step.
2: Ticket identifiers conform to `TICKET-XXXXXXXX` (8 digits) and are unique across the dataset.
3: A loader reads scenarios from embedded fixture files (e.g., JSON/YAML) into in-memory structures at startup, with no external database.
4: Loading is **deterministic** — the same fixtures yield the same in-memory data and the same tool responses every run (no query-time randomization).
5: The loader validates fixtures on load and fails fast with a clear error identifying the offending scenario/field if the schema is violated.
6: A small set of representative sample scenarios (enough to develop and test the ticket tools) is included and loads successfully.
7: Unit tests cover the loader, schema validation (including a negative case), and the determinism guarantee.

### Story 2.2 Ticket Retrieval Tools (List & Get)

As a student's AI agent,
I want to list tickets and fetch a single ticket by its ID,
so that I can discover incidents to work and read the full details of one.

#### Acceptance Criteria

1: A `get_ticket` tool accepts a `TICKET-XXXXXXXX` id and returns the full ticket detail (symptom, product, severity, status, persona, affected resource reference(s), timestamps).
2: A `list_tickets` tool returns a summary list of tickets and supports pagination or a bounded result size suitable for an agent context.
3: Requesting a non-existent or malformed ticket id returns a clear, structured "not found"/validation response rather than an error/stack trace.
4: Both tools expose clear MCP schemas and descriptions sufficient for an agent to select and call them without external docs.
5: Integration tests invoke both tools via an MCP client and assert correct, deterministic results against known sample scenarios.

### Story 2.3 Ticket Search & Filter Tool

As a student's AI agent,
I want to search and filter tickets by their attributes,
so that I can find the specific incident(s) relevant to a lab or investigation.

#### Acceptance Criteria

1: A `search_tickets` tool supports filtering by attributes including Azure product/service, status, severity, customer persona (Windows admin vs. Azure developer), and affected resource.
2: Filters are combinable (AND semantics) and return a bounded, paginated summary result set.
3: A search matching no tickets returns an empty result set (not an error), and invalid filter values return a clear validation message.
4: The tool exposes a clear MCP schema documenting each supported filter and its allowed values.
5: Integration tests assert deterministic search results for representative filter combinations against known sample scenarios.

### Story 2.4 Ticket → Resource Pivot Tool

As a student's AI agent,
I want to retrieve the Azure resource(s) and subscription associated with a ticket,
so that I can pivot from the reported incident to the resources whose telemetry I'll investigate.

#### Acceptance Criteria

1: A tool (e.g., `get_ticket_resources`) accepts a `TICKET-XXXXXXXX` id and returns the associated Azure resource(s) — including resource type (e.g., VM, VMSS), resource identifier, and subscription context.
2: Returned resource identifiers are consistent with those the Epic 3 telemetry tools will accept as scoping input.
3: A ticket with no/unknown resource, or a non-existent ticket id, returns a clear structured response rather than an error.
4: The tool exposes a clear MCP schema and description.
5: Integration tests assert the pivot returns the correct, deterministic resource(s) for known sample scenarios.

### Story 2.5 Seed Scenario Batch & Consistency Validation

As an instructor,
I want a first batch of ~20–30 realistic, internally consistent scenarios,
so that early labs have believable ticket content spanning both customer personas and several Azure products.

#### Acceptance Criteria

1: The dataset contains ~20–30 distinct scenarios authored as tickets, covering a spread of Azure products/platforms and both customer personas (Windows admins and Azure developers).
2: Each scenario includes a coherent symptom/problem statement, affected resource(s), severity/status, and a defined root cause + resolution/next-step (telemetry to be added in Epic 3).
3: Ticket ids, resources, and personas are internally consistent, and all scenarios pass the loader's schema validation.
4: An automated consistency check verifies, for every scenario, that required fields are present and that ticket↔resource references resolve correctly; it runs in the test suite and fails on any inconsistency.
5: The ticket list/search/get and resource-pivot tools return correct results across the full seed batch, verified by tests.

## Epic 3 Kusto Telemetry Tools & Correlation

**Epic Goal:** Make end-to-end RCA possible. This epic defines the mock Kusto table schemas and telemetry data model, exposes query tools for ARM control-plane traces, Network logs, and Compute logs (host/platform and Windows guest, for VM and VMSS), backfills correlated telemetry for existing scenarios, and authors additional scenarios — including the first **multi-round** ones where the agent must query, hypothesize, and query again. By the end, a student's agent can go from a ticket all the way to a defensible root cause using correlated telemetry, on a cumulative library of roughly 60 scenarios.

### Story 3.1 Telemetry Data Model & Mock Kusto Table Schemas

As a server developer,
I want mock Kusto table schemas and a telemetry data model linked to scenarios and resources,
so that every telemetry tool queries one consistent, believable source correlated to tickets.

#### Acceptance Criteria

1: Documented mock table schemas approximate real Azure log schemas for: **ARM control-plane traces**, **Network logs**, **Compute host/platform logs** (VM and VMSS), and **Compute Windows guest logs** (VM and VMSS), each with realistic, log-type-appropriate columns (including timestamps and a resource identifier).
2: The scenario data model is extended so telemetry rows are associated with a scenario and its resource(s), and reference the scenario's root cause (i.e., logs contain the evidence supporting that root cause).
3: The fixture loader loads telemetry deterministically alongside tickets, with schema validation and fail-fast on malformed telemetry.
4: A common query semantic is defined for all telemetry tools — scoping by resource identifier and time range, plus log-type-appropriate filters — returning structured rows.
5: Sample telemetry for a few existing scenarios is included and loads successfully, sufficient to develop and test the query tools.
6: Unit tests cover telemetry loading, schema validation (including a negative case), and determinism.

### Story 3.2 ARM Control-Plane Trace Query Tool

As a student's AI agent,
I want to query ARM control-plane traces for a resource,
so that I can investigate deployment, configuration, and control-plane operations related to an incident.

#### Acceptance Criteria

1: A tool (e.g., `query_arm_traces`) accepts a resource identifier, an optional time range, and ARM-appropriate filters, and returns matching trace rows.
2: Results are scoped to the requested resource/time range and are deterministic for identical inputs.
3: Results are correlated to the scenario — for scenarios whose root cause is control-plane related, the traces contain the supporting evidence (with realistic surrounding noise where appropriate).
4: An empty result (no matching traces) returns an empty set, not an error; malformed inputs return a clear validation message.
5: The tool exposes a clear MCP schema documenting parameters, filters, and returned columns.
6: Integration tests assert correct, deterministic results for representative scenarios.

### Story 3.3 Network Log Query Tool

As a student's AI agent,
I want to query Network logs for a resource,
so that I can investigate connectivity, NSG/routing, and network-related incidents.

#### Acceptance Criteria

1: A tool (e.g., `query_network_logs`) accepts a resource identifier, an optional time range, and network-appropriate filters, and returns matching log rows.
2: Results are scoped and deterministic for identical inputs.
3: Results are correlated to the scenario — network-root-caused scenarios contain supporting evidence with realistic noise.
4: Empty results return an empty set; malformed inputs return a clear validation message.
5: The tool exposes a clear MCP schema documenting parameters, filters, and returned columns.
6: Integration tests assert correct, deterministic results for representative scenarios.

### Story 3.4 Compute Log Query Tools (Host & Windows Guest, VM & VMSS)

As a student's AI agent,
I want to query Compute platform-host logs and Windows guest logs for VMs and VMSS,
so that I can investigate both the Azure host layer and the in-guest Windows behavior behind an incident.

#### Acceptance Criteria

1: Tools are provided to query **Compute host/platform logs** and **Compute Windows guest logs**, each supporting both **VM** and **VMSS** resources (including addressing an individual instance within a VMSS).
2: Each tool accepts a resource identifier, an optional time range, and compute-appropriate filters, and returns matching rows scoped to that resource/instance and time range.
3: Results are deterministic for identical inputs and correlated to the scenario — compute-root-caused scenarios contain supporting evidence across host and/or guest logs, with realistic noise.
4: Guest logs are Windows-only, consistent with the MVP scope.
5: Empty results return an empty set; malformed inputs (e.g., a VMSS instance that doesn't exist) return a clear validation message.
6: Each tool exposes a clear MCP schema documenting parameters, filters, and returned columns.
7: Integration tests assert correct, deterministic results for representative VM and VMSS scenarios across host and guest logs.

### Story 3.5 Telemetry Backfill & Multi-Round Scenario Authoring

As an instructor,
I want existing scenarios backfilled with correlated telemetry and new multi-round scenarios added,
so that agents can perform full RCA and some incidents require iterative investigation.

#### Acceptance Criteria

1: All seed scenarios from Epic 2 are backfilled with correlated telemetry across the relevant tables, so each has an evidence trail supporting its defined root cause.
2: Additional scenarios are authored to reach a cumulative total of ~60 distinct scenarios, spanning ARM/Network/Compute root causes across both personas.
3: At least a handful of scenarios are **multi-round**: the ticket symptom alone is insufficient, and the supporting evidence is distributed such that an agent must query telemetry, form a hypothesis, and query again (a different table, time range, or resource/instance) to reach the root cause.
4: For each multi-round scenario, the intended investigation path (which queries reveal which evidence) is documented to support lab authoring and grading.
5: The consistency check is extended to verify, for every scenario, that the telemetry actually contains evidence consistent with the defined root cause; it runs in the test suite and fails on any inconsistency.
6: End-to-end tests demonstrate at least one single-round and one multi-round scenario solved via the tool sequence (ticket → resource → telemetry → root cause).

## Epic 4 Full Scenario Library & Guided Prompts

**Epic Goal:** Complete the MVP teaching experience. This epic grows the scenario library to the full **100+** with the target difficulty mix (≥25% multi-round) and broad Azure-product/persona coverage, validates consistency across the whole library at scale, and authors the crafted MCP **prompts** that guide student agents through scoping, follow-up questioning, iterative investigation, and RCA. It also produces the instructor-facing scenario index and final classroom-readiness docs so labs can be mapped, run, and graded.

### Story 4.1 Expand Scenario Library to 100+ with Coverage

As an instructor,
I want the scenario library grown to at least 100 distinct, well-distributed scenarios,
so that I have enough varied material to run many labs without repetition.

#### Acceptance Criteria

1: The library contains **≥ 100 distinct scenarios**, each with ticket, resource(s), correlated telemetry, and a defined root cause + resolution/next-step.
2: Scenarios span a broad spread of Azure products/platforms and both customer personas (Windows admins and Azure developers), with root causes distributed across ARM, Network, and Compute domains.
3: Ticket ids remain unique and all scenarios conform to the data model and pass loader validation.
4: A coverage summary (by product/domain/persona) is generated or documented so gaps are visible.
5: All ticket and telemetry tools return correct, deterministic results across the full library, verified by the test suite.

### Story 4.2 Difficulty Tagging & Multi-Round Distribution

As an instructor,
I want scenarios tagged by difficulty with a verified multi-round proportion,
so that I can select scenarios of appropriate challenge and guarantee the intended learning progression.

#### Acceptance Criteria

1: Each scenario carries a difficulty indicator (e.g., single-round vs. multi-round, and/or a difficulty level).
2: **At least 25%** of scenarios are multi-round, verified by an automated check over the library.
3: Multi-round scenarios each retain a documented intended investigation path (from Epic 3) to support grading.
4: A distribution report (counts by difficulty/round-type and by domain) is produced and documented.
5: The difficulty tags are queryable/visible to instructors (e.g., via a documented field or a filter), enabling scenario selection for a given lab.

### Story 4.3 Guided MCP Prompts for the Diagnostic Workflow

As a student's AI agent,
I want crafted MCP prompts that guide the diagnostic workflow,
so that I use the tools effectively — scoping, asking follow-ups, iterating, and producing an RCA.

#### Acceptance Criteria

1: The server exposes MCP **prompts** covering the workflow: scoping/triage of a ticket, formulating follow-up questions, iterative investigation across the telemetry tools, and producing an RCA that resolves the issue or documents next steps.
2: Prompts reference the actual tool surface (ticket, resource, and telemetry tools) and encourage correct multi-step, multi-round tool use.
3: Prompts are discoverable via the MCP protocol with clear names and descriptions.
4: Prompts are parameterized where useful (e.g., by ticket id) per MCP prompt conventions.
5: A documented example shows an agent using a prompt to progress from a ticket to an RCA on a representative scenario (including a multi-round one).
6: Integration tests assert the prompts are discoverable and return well-formed prompt content.

### Story 4.4 Full-Library Consistency Validation & Classroom Readiness

As an instructor,
I want whole-library validation and classroom-ready materials,
so that I can trust the data and run graded labs on day one.

#### Acceptance Criteria

1: The consistency check runs across the entire 100+ library and verifies, for every scenario, that ticket↔resource↔telemetry↔root-cause are coherent; it passes in CI/test and fails on any inconsistency.
2: An instructor-facing **scenario index** is produced (id, product/domain, persona, difficulty/round-type, one-line summary, and the intended root cause/investigation path) to support mapping labs to scenarios and grading.
3: Classroom run docs are finalized for both transport modes, including how to select scenarios and verify connectivity.
4: A full test run (unit + integration + end-to-end) passes against the complete library and tool/prompt surface.
5: The determinism guarantee is verified across the full library (identical inputs → identical outputs) as an automated check.

## Checklist Results Report

**Checklist:** PM Requirements Checklist — run in comprehensive mode on 2026-07-23.

### Executive Summary

- **Overall PRD completeness:** ~95%
- **MVP scope:** Just Right — genuinely minimal (read-only tickets, Windows-only guest logs, no auth) yet viable for real teaching labs; incremental scenario growth de-risks the heaviest authoring effort.
- **Readiness for architecture phase:** READY FOR ARCHITECT
- **Most critical gap:** Exact mock Kusto table schemas are intentionally deferred to the Architect (Story 3.1) — expected, but the largest open design item.

### Category Statuses

| Category                         | Status | Critical Issues |
| -------------------------------- | ------ | --------------- |
| 1. Problem Definition & Context  | PASS   | No formal competitive analysis (low relevance for an internal teaching tool). |
| 2. MVP Scope Definition          | PASS   | Explicit in/out scope with rationale; MVP success criteria defined. |
| 3. User Experience Requirements  | N/A    | Headless MCP server — no UI. "User journey" is the agent diagnostic workflow, captured via prompts (Epic 4) and story ACs; error/empty states specified. |
| 4. Functional Requirements       | PASS   | 15 FRs, WHAT-not-HOW, testable; stories in consistent format with testable ACs. |
| 5. Non-Functional Requirements   | PASS   | Performance, determinism, offline, concurrency, and no-real-data security posture defined. |
| 6. Epic & Story Structure        | PASS   | 4 sequential epics, 17 vertical-slice stories; Epic 1 establishes scaffold + local testability early. |
| 7. Technical Guidance            | PASS   | Constraints, decisions with rationale, and architect-investigation areas flagged. |
| 8. Cross-Functional Requirements | PASS   | Data model/entities defined; MCP integration + dual-transport operations covered; schema changes tied iteratively to stories. |
| 9. Clarity & Communication       | PASS   | Well-structured, consistent terminology, versioned via Change Log. |

### Top Issues by Priority

- **BLOCKERS:** None.
- **HIGH:** Define concrete mock Kusto schemas (columns) for ARM / Network / Compute host / Windows guest — owned by Architect (Open Question + Story 3.1).
- **MEDIUM:** Confirm packaging/run mechanism (uv/pip/script); confirm whether the instructor-hosted network endpoint needs any classroom auth.
- **LOW:** Add a small diagram of the ticket → resource → telemetry data model for the Architect.

### Final Decision

**READY FOR ARCHITECT** — the PRD and epics are comprehensive, properly structured, and appropriately scoped for MVP development.

## Next Steps

### UX Expert Prompt

Not applicable. The Contoso Support Ticketing MCP Server is a headless MCP server with no user interface; there is no UX/UI work for this MVP. Prompt-authoring for agent guidance is covered within the PRD (Epic 4).

### Architect Prompt

Please create the architecture for the **Contoso Support Ticketing MCP Server** using this PRD (`docs/prd.md`) as input. This is a fully-mocked, offline Python MCP server for a classroom. Key design work: (1) define concrete mock **Kusto table schemas** (columns) for ARM control-plane traces, Network logs, and Compute host and Windows guest logs (VM and VMSS) that are believable approximations of real Azure schemas; (2) design the **scenario/ticket/resource/telemetry data model** and fixture format that scales to 100+ scenarios without code changes and models **multi-round investigation** (evidence distributed so follow-up queries reveal new evidence); (3) specify the **Python MCP server** structure with dual transport (stdio + streamable HTTP/SSE) from one codebase, guaranteeing deterministic responses; (4) choose the **packaging/run** approach (e.g., uv/pip/script) with a single command per mode; and (5) address classroom-scale concurrency for the network transport. Honor the constraints: no external services/credentials, all data embedded, read-only tickets, Windows-only guest logs, MCP-spec compliant. Flag any assumptions for confirmation.
