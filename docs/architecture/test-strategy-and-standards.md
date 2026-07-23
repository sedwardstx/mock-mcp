# Test Strategy and Standards

## Testing Philosophy

- **Approach:** Test-after for scaffolding; test-alongside for the data layer and tools. The **consistency suite is the safety net** for the growing scenario library.
- **Coverage Goals:** High coverage on the data layer (loader, query, validation) and every tool/prompt; ~80%+ overall as a guide, not a gate.
- **Test Pyramid:** Many unit (query/validation/determinism) → fewer integration (tools/prompts over a real MCP client) → few e2e (full RCA journeys) → a dedicated consistency suite over all fixtures.

## Test Types and Organization

- **Unit Tests:** pytest 8.x; `tests/unit/`; cover loader parsing, schema validation (incl. negative cases), filter/time-range/pagination logic, and the determinism guarantee (same input → same output). Mock nothing internal; use tiny inline fixtures.
- **Integration Tests:** pytest + pytest-asyncio; `tests/integration/`; spin up the FastMCP server with an in-memory/loopback MCP client and invoke each tool/prompt over **both** stdio and HTTP transports; assert schemas, scoping, not-found/empty/invalid handling.
- **End-to-End Tests:** `tests/e2e/`; drive at least one single-round and one multi-round scenario through the full tool sequence and assert the evidence needed for the correct RCA is reachable.
- **Consistency Tests:** `tests/consistency/`; iterate **every** scenario fixture and assert: schema valid, ticket↔resource references resolve, telemetry contains evidence matching the declared root_cause, `difficulty` honestly reflects the investigation_path, and ≥25% of the library is `multi_round`.

## Test Data Management

- **Strategy:** The production fixtures ARE the primary test corpus (consistency/e2e). Unit tests use small purpose-built fixtures.
- **Fixtures:** `src/contoso_support_mcp/fixtures/scenarios/` (shipped) + `tests/**/fixtures/` (unit).
- **Factories:** Optional Pydantic model factories for unit tests.
- **Cleanup:** None needed — read-only, no external state.

## Continuous Testing

- **CI Integration:** GitHub Actions runs Ruff + unit + integration + e2e + consistency on push/PR.
- **Performance Tests:** A lightweight check that representative tool calls return <1s; a concurrency smoke test for HTTP mode simulating many simultaneous clients.
- **Security Tests:** N/A beyond dependency scanning (see Security).
