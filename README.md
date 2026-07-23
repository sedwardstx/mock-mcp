# Contoso Support Ticketing MCP Server

A fully-mocked, offline **Model Context Protocol (MCP)** server that emulates an
Azure support-ticketing backend. Built as a classroom teaching tool: students
connect their AI agents/Skills to it and practice ticket triage and root-cause
analysis against realistic (but entirely mocked) support tickets and Kusto-style
telemetry.

All data is mocked and embedded — **no Azure subscription, credentials, or
internet access is required at runtime.**

## Quickstart

```bash
# 1. Install (once)
uv sync

# 2a. Student — local, offline (stdio)
uv run contoso-support-mcp --transport stdio

# 2b. Instructor — host for the class (network)
uv run contoso-support-mcp --transport http --host 0.0.0.0 --port 8000
```

**Confirm the connection:** from your agent/client, call the `get_server_info`
tool — a `status: "ok"` response means you're connected to the Contoso Support
server. Total time from a clean machine to first successful call is a couple of
minutes.

Invalid configuration (e.g. `--port 70000` or an unknown `--transport`) prints a
clear one-line error and exits — no stack trace.

## Requirements

- Python **3.11+**
- [`uv`](https://docs.astral.sh/uv/) (package/environment manager)

## Install

```bash
uv sync
```

This resolves dependencies and creates a reproducible `uv.lock`.

## Run

### Student (local, offline) — stdio transport

```bash
uv run contoso-support-mcp --transport stdio
```

Point your MCP-capable agent/client at this command. The server communicates
over stdio; **do not** write to stdout from any other process sharing the pipe.

### Instructor (network) — streamable HTTP transport

Host one server for the whole class over the local network:

```bash
uv run contoso-support-mcp --transport http --host 0.0.0.0 --port 8000
```

The MCP endpoint is served at `http://<host>:<port>/mcp`. Students point their
MCP clients at that URL. `--host` defaults to `127.0.0.1` (loopback only); use
`0.0.0.0` to serve the classroom LAN. No auth/TLS in the MVP — intended for a
trusted classroom network. Still fully offline: only a local port is bound.

### Confirm the connection

Once connected (either transport), have your agent call the **`get_server_info`**
tool. It returns the server name, version, and status (`ok`) — confirming your
agent is talking to the Contoso Support server.

> The ticket and telemetry tools arrive in later stories.

## Guided prompts

The server also exposes MCP **prompts** that coach an agent through a full
diagnosis. Discover them with your client's prompt list; each takes a `ticket_id`:

- **`triage_ticket`** — scope a ticket (product, persona, severity, affected resource).
- **`investigate_incident`** — the full workflow: scope → follow-up questions →
  iterative telemetry investigation (with a second round if the first is
  inconclusive) → root-cause analysis.
- **`summarize_rca`** — write up the root cause + evidence + resolution/next steps.

**Example (multi-round scenario `TICKET-10000026`):** load `investigate_incident`
with that ticket id. Following it, the agent scopes the ticket and resource, then
queries the in-guest logs — which come back **benign/inconclusive**. Prompted to
iterate, it forms a new hypothesis and queries the **host** logs, which reveal a
`Degraded` host event — the real root cause. It then produces an RCA citing that
row. (For a single-round example, use `TICKET-10000001`: the ARM traces show a
`409 AllocationFailed` directly.)

## Develop & Test

```bash
uv run pytest        # unit + integration tests
uv run ruff check    # lint
uv run ruff format   # format
```

## For instructors — selecting scenarios & grading

- **`docs/scenario-index.md`** — one row per scenario: ticket id, product, persona,
  difficulty, root-cause domain, title, the **expected root cause** (the grading
  answer), and the intended **investigation tool sequence**. Use it to map labs to
  scenarios and to grade student RCAs.
- **`docs/scenario-coverage.md`** — distribution by persona / product / category /
  difficulty (incl. a difficulty × category cross-tab) so you can pick an
  appropriate mix and spot gaps.
- Regenerate both after editing scenarios:
  `uv run python scripts/scenario_index.py` and
  `uv run python scripts/coverage_report.py`.

Every scenario is validated for consistency (ticket ↔ resource ↔ telemetry ↔
root cause) and determinism in CI, so the data you grade against is trustworthy.

## Project Layout

```
src/contoso_support_mcp/
  __main__.py     # CLI entry point (transport selection)
  server.py       # FastMCP app; registers tools/prompts
  config.py       # settings
  tools/          # MCP tool handlers (health today; tickets/telemetry later)
  prompts/        # guided diagnostic prompts (Epic 4)
  data/           # mock data layer: models, loader, repository (Epic 2+)
  fixtures/       # embedded scenario data (Epic 2+)
tests/            # unit + integration
```
