# Contoso Support Ticketing MCP Server

A fully-mocked, offline **Model Context Protocol (MCP)** server that emulates an
Azure support-ticketing backend. Built as a classroom teaching tool: students
connect their AI agents/Skills to it and practice ticket triage and root-cause
analysis against realistic (but entirely mocked) support tickets and Kusto-style
telemetry.

All data is mocked and embedded — **no Azure subscription, credentials, or
internet access is required at runtime.**

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

## Develop & Test

```bash
uv run pytest        # unit + integration tests
uv run ruff check    # lint
uv run ruff format   # format
```

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
