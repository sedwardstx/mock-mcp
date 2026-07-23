# Tech Stack

## Cloud Infrastructure

- **Provider:** None. The server runs entirely locally (student laptop or instructor laptop). No cloud provider, credentials, or internet access are used at runtime (PRD NFR1).
- **Key Services:** N/A.
- **Deployment Regions:** N/A.

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|---|---|---|---|---|
| **Language** | Python | 3.12.x | Primary implementation language | Modern, widely available; matches PRD; strong typing via type hints + Pydantic |
| **MCP Framework** | `mcp` (Python SDK, FastMCP) | ≥ 1.9, < 2.0 | MCP server, tools, prompts, transports | Official SDK; provides stdio **and** streamable HTTP from one codebase (confirm exact version at setup) |
| **Data Validation** | Pydantic | 2.x | Models, fixture validation, tool I/O schemas | Fail-fast fixture validation; auto JSON schema for MCP tool descriptions |
| **Fixture Format** | YAML (`PyYAML` or `ruamel.yaml`) | PyYAML 6.x | Human-authorable scenario files | Readable, diff-friendly, one file per scenario |
| **ASGI Server** | Uvicorn | 0.30.x | Host the streamable HTTP transport | Standard async server for the network mode (used by FastMCP HTTP app) |
| **Package/Env Manager** | uv | ≥ 0.4 | Dependency mgmt, venv, run | Fast, reproducible; single-command setup for the classroom |
| **Test Framework** | pytest | 8.x | Unit / integration / e2e tests | De facto standard; fixtures map well to scenario testing |
| **Async Test Support** | pytest-asyncio | 0.23.x | Test async MCP client/server flows | Needed for integration tests over transports |
| **Lint/Format** | Ruff | ≥ 0.5 | Linting + formatting | Fast, single tool; enforces consistency for AI + human devs |
| **Type Checking** | mypy (optional) | 1.x | Static type checks | Optional gate; complements Pydantic at boundaries |

> **Note:** MCP SDK and adjacent versions evolve quickly — pin exact versions in `pyproject.toml`/lockfile at project init and verify the SDK's current transport API. Everything above must run fully offline after initial dependency install.
