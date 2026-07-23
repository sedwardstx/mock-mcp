# Error Handling Strategy

## General Approach

- **Error Model:** Two distinct classes. (1) **Startup errors** (bad fixtures/config) → fail fast, abort process with a precise, actionable message. (2) **Request-time errors** (bad tool input, not-found, empty result) → return a **structured MCP tool result** (never an unhandled exception/stack trace to the agent).
- **Exception Hierarchy:** `ContosoMcpError` base → `FixtureValidationError`, `ConfigError` (startup); request-time issues are represented as structured results, not raised past the handler.
- **Error Propagation:** Handlers catch, map to a structured `{status, message, detail}` payload, and log; startup errors propagate to the process exit.

## Logging Standards

- **Library:** Python `logging` (stdlib).
- **Format:** Structured/plain text to stderr. **Critical for stdio mode:** logs MUST go to stderr, never stdout (stdout is the MCP transport channel).
- **Levels:** DEBUG (dev), INFO (lifecycle: startup, scenario count loaded, transport), WARNING (recoverable/empty-with-context), ERROR (startup failures).
- **Required Context:** tool name and (where applicable) ticket_id/resource_id; no correlation-id infra needed (stateless, single process). No user/PII context (data is mocked).

## Error Handling Patterns

- **External API Errors:** N/A — no external calls.
- **Business Logic Errors:**
  - **Not found** (ticket/resource): structured `status: "not_found"` result with the offending id.
  - **Validation** (malformed id, bad filter/time range, unknown VMSS instance): structured `status: "invalid_request"` with which field failed and allowed values.
  - **Empty result** (valid query, no rows): `status: "ok"` with an empty list — NOT an error (PRD-specified behavior).
- **Data Consistency:** Enforced at **load time**, not request time. The loader validates schema + referential integrity + evidence-consistency (telemetry supports the declared root cause) and refuses to start on any violation. Runtime data is immutable, so no transactions/idempotency concerns.
