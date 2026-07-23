# Source Tree

```plaintext
mock-mcp/
├── pyproject.toml                     # deps, entry point, tool config (uv/ruff/pytest)
├── uv.lock                            # pinned, reproducible deps
├── README.md                          # setup + run (both transport modes)
├── src/
│   └── contoso_support_mcp/
│       ├── __init__.py
│       ├── __main__.py                # CLI: transport/host/port/fixtures-path
│       ├── config.py                  # Settings model + validation
│       ├── server.py                  # FastMCP app; registers tools + prompts
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── health.py              # get_server_info
│       │   ├── tickets.py             # get_ticket, list_tickets, search_tickets
│       │   ├── resources.py           # get_ticket_resources
│       │   └── telemetry.py           # query_arm_traces, query_network_logs,
│       │                              #   query_compute_host_logs, query_compute_guest_logs
│       ├── prompts/
│       │   └── diagnostics.py         # scoping, follow-up, investigation, RCA prompts
│       ├── data/
│       │   ├── __init__.py
│       │   ├── models.py              # Pydantic: Scenario, Ticket, AzureResource, telemetry rows
│       │   ├── loader.py              # discover + parse + validate fixtures → Dataset
│       │   ├── repository.py          # in-memory indices + query methods
│       │   └── query.py               # filter/time-range/pagination helpers
│       └── fixtures/
│           └── scenarios/             # one YAML per scenario (100+)
│               ├── TICKET-10000001.yaml
│               └── ...
├── tests/
│   ├── unit/                          # loader, validation, determinism, query logic
│   ├── integration/                   # tools/prompts via in-memory MCP client, both transports
│   ├── e2e/                           # ticket→resource→telemetry→RCA (single + multi-round)
│   └── consistency/                   # whole-library ticket↔telemetry↔root-cause checks
└── scripts/
    ├── validate_scenarios.py          # standalone fixture validation / coverage report
    └── run_dev.sh                     # convenience launcher
```
