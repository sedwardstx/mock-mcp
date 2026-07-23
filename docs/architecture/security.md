# Security

The system handles **no real data, credentials, secrets, or PII** and makes **no external calls**, which removes most conventional attack surface. Requirements below are scoped to what actually applies.

## Input Validation

- **Validation Library:** Pydantic.
- **Validation Location:** At the MCP tool boundary, before repository access.
- **Required Rules:** All external inputs validated; whitelist allowed enum/filter values; reject malformed ids/time ranges with a structured error.

## Authentication & Authorization

- **Auth Method:** **None in MVP (confirmed).** Open local endpoint. For stdio mode this is inherent (local process). For instructor-hosted HTTP mode, it runs on a trusted classroom LAN with no auth/TLS — confirmed acceptable for the classroom context. A token/auth check, if ever needed, would slot in cleanly at the transport layer without touching the surface or data layers.
- **Session Management:** N/A (stateless).

## Secrets Management

- **Development / Production:** No secrets exist. Enforce "never hardcode secrets" as a standing rule even though none are needed.

## API Security

- **Rate Limiting:** Not required for MVP (classroom scale, read-only, no cost). Note as a Phase-2 option if abuse is a concern.
- **CORS / Security Headers / HTTPS:** HTTP transport serves a trusted LAN; TLS not required for MVP. Revisit with the auth open item if exposed beyond the classroom.

## Data Protection

- **Encryption at Rest/Transit:** N/A — mock data only, trusted local network.
- **PII Handling:** No real PII; mock personas/emails are fictional (e.g., `@contoso.com`).
- **Logging Restrictions:** Do not log full request payloads at INFO; keep logs to lifecycle + tool name + ids.

## Dependency Security

- **Scanning Tool:** GitHub Dependabot / `pip-audit` (optional).
- **Update Policy:** Pin versions in `uv.lock`; update deliberately and re-run the full suite.
- **Approval Process:** New runtime deps must preserve the offline guarantee.
