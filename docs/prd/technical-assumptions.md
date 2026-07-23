# Technical Assumptions

## Repository Structure: Monorepo

A single repository holds the MCP server code, the mock data/scenario library, prompt templates, and classroom run/setup docs. This keeps the teaching artifact self-contained and easy to distribute to students as one unit.

## Service Architecture

**Monolith** — a single Python MCP server process. The server exposes tools/prompts and reads from an embedded mock data layer. There is a clear internal separation between the **MCP surface** (tool/prompt handlers) and the **mock data layer** (scenario/ticket/telemetry fixtures + query logic), so the dataset can grow independently of the server core. The server supports both stdio and network (streamable HTTP/SSE) transports from the same codebase. Stateless request/response; deterministic responses keyed on inputs.

## Testing Requirements

**Unit + Integration.** Unit tests cover the data-layer query logic and determinism guarantees. Integration tests exercise the MCP tools end-to-end (a test client invokes each tool and validates schemas, scoping, and scenario/telemetry consistency). A lightweight harness/script to manually invoke tools locally is desirable for authoring and classroom troubleshooting. Given the teaching purpose, a test that validates each scenario is internally consistent (ticket ↔ telemetry ↔ root cause) is valuable.

## Additional Technical Assumptions and Requests

- Language/runtime: **Python**, using the official Python MCP SDK.
- Transports: **stdio** (student local) and **streamable HTTP/SSE** (instructor network hosting) from a single server implementation.
- Data storage: embedded fixture files (e.g., JSON/YAML) and/or in-memory structures; no external database.
- Kusto emulation: mock tables approximate real Azure log schemas (ARM, Network, Compute host/guest) closely enough to be believable; exact schemas/columns to be defined with the Architect.
- Determinism: no `random`/time-of-day-dependent behavior in query responses; any variability must be seeded and reproducible.
- Distribution: runnable via a documented single command per transport mode (packaging approach — e.g., `uv`/`pip`/script — to be decided with the Architect).
- Classroom auth for network mode: assumed an open local endpoint is acceptable for MVP; revisit if identity is required.
