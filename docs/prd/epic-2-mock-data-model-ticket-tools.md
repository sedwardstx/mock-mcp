# Epic 2 Mock Data Model & Ticket Tools

**Epic Goal:** Give the server a realistic support-ticketing surface. This epic defines the scenario/ticket/resource data model and a deterministic loader for embedded fixtures, exposes the ticket tools (list, search/filter, get) plus the ticket→resource pivot, and authors a first batch of ~20–30 scenarios. By the end, a student's agent can browse and filter believable `TICKET-XXXXXXXX` incidents and pivot from a ticket to its affected Azure resource(s) — the foundation the telemetry tools will correlate against.

## Story 2.1 Scenario & Ticket Data Model + Deterministic Loader

As a server developer,
I want a well-defined scenario/ticket/resource data model with a deterministic fixture loader,
so that all tools read from one consistent, extensible source and later scenarios can be added without code changes.

### Acceptance Criteria

1: A documented data model defines a **scenario** and its linked entities: ticket (id, product/service, symptom/problem statement, severity, status, customer persona, timestamps), affected Azure resource(s) and subscription, references to correlated telemetry (populated in Epic 3), and a defined root cause + resolution/next-step.
2: Ticket identifiers conform to `TICKET-XXXXXXXX` (8 digits) and are unique across the dataset.
3: A loader reads scenarios from embedded fixture files (e.g., JSON/YAML) into in-memory structures at startup, with no external database.
4: Loading is **deterministic** — the same fixtures yield the same in-memory data and the same tool responses every run (no query-time randomization).
5: The loader validates fixtures on load and fails fast with a clear error identifying the offending scenario/field if the schema is violated.
6: A small set of representative sample scenarios (enough to develop and test the ticket tools) is included and loads successfully.
7: Unit tests cover the loader, schema validation (including a negative case), and the determinism guarantee.

## Story 2.2 Ticket Retrieval Tools (List & Get)

As a student's AI agent,
I want to list tickets and fetch a single ticket by its ID,
so that I can discover incidents to work and read the full details of one.

### Acceptance Criteria

1: A `get_ticket` tool accepts a `TICKET-XXXXXXXX` id and returns the full ticket detail (symptom, product, severity, status, persona, affected resource reference(s), timestamps).
2: A `list_tickets` tool returns a summary list of tickets and supports pagination or a bounded result size suitable for an agent context.
3: Requesting a non-existent or malformed ticket id returns a clear, structured "not found"/validation response rather than an error/stack trace.
4: Both tools expose clear MCP schemas and descriptions sufficient for an agent to select and call them without external docs.
5: Integration tests invoke both tools via an MCP client and assert correct, deterministic results against known sample scenarios.

## Story 2.3 Ticket Search & Filter Tool

As a student's AI agent,
I want to search and filter tickets by their attributes,
so that I can find the specific incident(s) relevant to a lab or investigation.

### Acceptance Criteria

1: A `search_tickets` tool supports filtering by attributes including Azure product/service, status, severity, customer persona (Windows admin vs. Azure developer), and affected resource.
2: Filters are combinable (AND semantics) and return a bounded, paginated summary result set.
3: A search matching no tickets returns an empty result set (not an error), and invalid filter values return a clear validation message.
4: The tool exposes a clear MCP schema documenting each supported filter and its allowed values.
5: Integration tests assert deterministic search results for representative filter combinations against known sample scenarios.

## Story 2.4 Ticket → Resource Pivot Tool

As a student's AI agent,
I want to retrieve the Azure resource(s) and subscription associated with a ticket,
so that I can pivot from the reported incident to the resources whose telemetry I'll investigate.

### Acceptance Criteria

1: A tool (e.g., `get_ticket_resources`) accepts a `TICKET-XXXXXXXX` id and returns the associated Azure resource(s) — including resource type (e.g., VM, VMSS), resource identifier, and subscription context.
2: Returned resource identifiers are consistent with those the Epic 3 telemetry tools will accept as scoping input.
3: A ticket with no/unknown resource, or a non-existent ticket id, returns a clear structured response rather than an error.
4: The tool exposes a clear MCP schema and description.
5: Integration tests assert the pivot returns the correct, deterministic resource(s) for known sample scenarios.

## Story 2.5 Seed Scenario Batch & Consistency Validation

As an instructor,
I want a first batch of ~20–30 realistic, internally consistent scenarios,
so that early labs have believable ticket content spanning both customer personas and several Azure products.

### Acceptance Criteria

1: The dataset contains ~20–30 distinct scenarios authored as tickets, covering a spread of Azure products/platforms and both customer personas (Windows admins and Azure developers).
2: Each scenario includes a coherent symptom/problem statement, affected resource(s), severity/status, and a defined root cause + resolution/next-step (telemetry to be added in Epic 3).
3: Ticket ids, resources, and personas are internally consistent, and all scenarios pass the loader's schema validation.
4: An automated consistency check verifies, for every scenario, that required fields are present and that ticket↔resource references resolve correctly; it runs in the test suite and fails on any inconsistency.
5: The ticket list/search/get and resource-pivot tools return correct results across the full seed batch, verified by tests.
