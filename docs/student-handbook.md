# Student Handbook — Contoso Support Ticketing MCP Server

Welcome! In these labs you'll connect your **AI agent** to the **Contoso Support
Ticketing MCP server** and practice the core skill of an Azure support engineer:
taking a customer's reported symptom and working through telemetry to a
**root-cause analysis (RCA)**.

Everything the server returns is **mocked** — realistic support tickets and
Azure-style logs — so there's no Azure subscription, no credentials, and no
internet needed at runtime. You just connect and investigate.

> **Taking the instructor-led GitHub Copilot workshop?** The starter files
> (custom instructions, prompts, a log-triage skill, specialist/coordinator
> agents, sample data, and a ready `.vscode/mcp.json`) are provided as a bundle at
> **`docs/assets/workshop/`** — read its `README.md` for the copy-into-place setup,
> and follow **`docs/external/Participant_Workbook.md`** for the labs.

---

## 1. What you get

Once connected, your agent can call these **tools**:

| Tool | What it does |
|------|--------------|
| `get_server_info` | Confirms you're connected (returns `status: "ok"`) |
| `list_tickets` | Browse support tickets (paginated) |
| `search_tickets` | Filter tickets by product, status, severity, persona, resource |
| `get_ticket` | Read one ticket in full (symptom, product, severity, resource) |
| `get_ticket_resources` | Pivot from a ticket to its Azure resource(s) |
| `query_arm_traces` | ARM control-plane traces for a resource |
| `query_network_logs` | Network / NSG flow logs for a resource |
| `query_compute_host_logs` | Azure host/platform logs (VM & VMSS, per-instance) |
| `query_compute_guest_logs` | In-guest Windows logs (VM & VMSS, per-instance) |
| `search_known_issues` | Look up **generic** Azure remediation guidance by keyword/product/category (a hint — *not* the ticket-specific answer) |

…and these **guided prompts** (each takes a `ticket_id`):

- **`triage_ticket`** — scope a ticket.
- **`investigate_incident`** — the full workflow (scope → follow-ups → investigate → RCA). **Start here.**
- **`summarize_rca`** — write up your findings.

---

## 2. Prerequisites

Your instructor will tell you which setup applies:

- **Online (instructor-hosted):** you need **nothing installed** — just your MCP
  client and the server URL from your instructor.
- **Offline (self-hosted):** you'll run the server yourself. You need:
  - [Python 3.11+](https://www.python.org/downloads/)
  - [`uv`](https://docs.astral.sh/uv/) (package/environment manager)
  - This repository cloned locally, then run once: `uv sync`

---

## 3. Connect your client

Add **one** server entry to your MCP client's config. Pick the block for your
client **and** your scenario (online vs offline). Replace
`/absolute/path/to/mock-mcp` with your clone location, and `INSTRUCTOR_HOST` with
the address your instructor gives you.

> A quick way to confirm success after configuring: ask your agent to call
> `get_server_info`. A `status: "ok"` reply means you're connected.

### Claude Code / Claude Desktop / Cursor

Uses the `mcpServers` key.

**Offline (stdio):**

```json
{
  "mcpServers": {
    "contoso-support": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mock-mcp",
        "contoso-support-mcp",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

**Online (HTTP):**

```json
{
  "mcpServers": {
    "contoso-support": {
      "type": "http",
      "url": "http://INSTRUCTOR_HOST:8000/mcp"
    }
  }
}
```

File location: **Claude Code** → `.mcp.json` at your project root (or run
`claude mcp add`); **Claude Desktop** → `claude_desktop_config.json`;
**Cursor** → `.cursor/mcp.json`.

### VS Code (`.vscode/mcp.json`)

Uses the `servers` key with an explicit `type`.

**Offline (stdio):**

```json
{
  "servers": {
    "contoso-support": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mock-mcp",
        "contoso-support-mcp",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

**Online (HTTP):**

```json
{
  "servers": {
    "contoso-support": {
      "type": "http",
      "url": "http://INSTRUCTOR_HOST:8000/mcp"
    }
  }
}
```

### GitHub Copilot CLI (`~/.copilot/mcp-config.json`)

Uses `mcpServers`, but stdio servers use `type: "local"` and each server needs a
`tools` field (`["*"]` = allow all).

**Offline (local/stdio):**

```json
{
  "mcpServers": {
    "contoso-support": {
      "type": "local",
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mock-mcp",
        "contoso-support-mcp",
        "--transport",
        "stdio"
      ],
      "env": {},
      "tools": ["*"]
    }
  }
}
```

**Online (HTTP):**

```json
{
  "mcpServers": {
    "contoso-support": {
      "type": "http",
      "url": "http://INSTRUCTOR_HOST:8000/mcp",
      "tools": ["*"]
    }
  }
}
```

You can also add it interactively with `/mcp add`. Config lives at
`~/.copilot/mcp-config.json` (override the directory with `COPILOT_HOME`).

After editing config, **restart or reload your client** so it picks up the new
server.

---

## 4. Your first investigation (single-round)

Try this end-to-end on ticket **`TICKET-10000001`**:

1. **Load the prompt.** Use `investigate_incident` with `ticket_id=TICKET-10000001`.
2. **Scope.** Your agent calls `get_ticket` (a VM won't start — allocation
   failure) and `get_ticket_resources` (note the VM's `resource_id`).
3. **Investigate.** The symptom points at the control plane, so query
   `query_arm_traces` for that `resource_id`. You'll see a `409` /
   `AllocationFailed` trace.
4. **RCA.** Conclude: the VM SKU had no capacity in the target zone. Resolution:
   retry in another zone or resize to an available SKU. (Use `summarize_rca` to
   write it up.)

---

## 5. When one look isn't enough (multi-round)

About a quarter of scenarios are **multi-round**: the first, obvious query is
inconclusive and you must form a new hypothesis and query again. Try
**`TICKET-10000026`**:

1. Scope the ticket and get its `resource_id`.
2. The symptom looks like an in-guest problem, so query
   `query_compute_guest_logs` — but the rows are all **benign** (no errors).
   Inconclusive.
3. Re-think: maybe it's the Azure **host**, not the guest. Query
   `query_compute_host_logs` — now you find a `Degraded` host event. That's the
   real root cause.
4. Write the RCA, citing the host-log row and noting the guest query was a dead
   end.

**Lesson:** don't stop at the first query. The `investigate_incident` prompt
reminds you to iterate — follow it.

---

## 6. Tips & troubleshooting

- **Always start with `get_server_info`** to confirm the connection before a lab.
- **Scope telemetry queries** by `resource_id` (get it from
  `get_ticket_resources`). For a scale set (VMSS), pass `instance_id` to target
  one instance; querying an instance that doesn't exist returns a clear
  `invalid_request` telling you the valid instances.
- **Empty results are normal**, not errors — they mean "no matching rows for that
  scope." A wrong domain/time window often returns empty; try another tool.
- **Known-issues KB:** `search_known_issues` gives general remediation guidance for
  a *class* of problem (filter by `query` keyword, `product`, or `category`). It's a
  starting hint, **not** the ticket's specific root cause — always confirm with the
  telemetry tools before you conclude.
- **Time ranges** use the format `"START/END"` in ISO-8601, e.g.
  `"2026-05-14T09:00:00Z/2026-05-14T10:00:00Z"`. Either side may be blank.
- **Offline server won't start?** Run `uv sync` in the repo first, and make sure
  the `--directory` path in your config points at your clone.
- **Online can't connect?** Double-check the `INSTRUCTOR_HOST`/port and that the
  URL ends in `/mcp`. You must be on the same network as the instructor's machine.
- **Deterministic by design:** the same query always returns the same rows, so
  your results are reproducible and gradeable.

---

Good luck — read the ticket, follow the evidence, and don't stop at the first
query. 🔍
