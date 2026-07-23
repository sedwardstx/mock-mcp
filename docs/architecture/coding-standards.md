# Coding Standards

## Core Standards

- **Languages & Runtimes:** Python 3.12; type hints required on public functions.
- **Style & Linting:** Ruff (lint + format); config in `pyproject.toml`. CI fails on lint errors.
- **Test Organization:** `tests/{unit,integration,e2e,consistency}/`; files `test_*.py`; test names describe behavior.

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| MCP tool name | snake_case verb_noun | `query_network_logs` |
| Pydantic model | PascalCase | `ComputeGuestLog` |
| Fixture file | `TICKET-XXXXXXXX.yaml` | `TICKET-10000001.yaml` |

## Critical Rules

- **No stdout writes except the MCP transport:** never `print()`; use the logger (stderr). A stray stdout write corrupts stdio-mode framing.
- **No randomness or wall-clock at query time:** no `random`, no `datetime.now()` affecting results. All variability is authored in fixtures. Determinism is a hard requirement.
- **All tool inputs validated at the boundary** via Pydantic before touching the repository.
- **Tools return structured results, never raise past the handler:** map errors to `{status, message, detail}`.
- **No new runtime dependency on network/cloud/DB:** the server must run fully offline.
- **Scenarios are data, not code:** adding/editing scenarios must never require server code changes.
