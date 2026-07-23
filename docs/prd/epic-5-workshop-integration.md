# Epic 5 Workshop Integration

**Epic Goal:** Make our server the spine of the 2-day GitHub Copilot workshop (`docs/external/Participant_Workbook.md`). Add a read-only known-issues KB tool, ship the Azure-themed Copilot starter scaffold (instructions, prompts, a log-triage skill, sample data, custom agents, and `.vscode/mcp.json`) so this repo doubles as the workshop starter repo, and re-theme the participant workbook so its MCP labs (4–6) run against this server. All new data stays mocked/PII-free and the existing scenario dataset, tools, and grading key are untouched. (Brownfield enhancement — builds on Epics 1–4.)

## Story 5.1 Known-Issues KB Tool

As a student's AI agent,
I want to search a read-only Azure known-issues knowledge base,
so that I can look up generic remediation guidance for a symptom without it revealing the ticket-specific answer.

### Acceptance Criteria

1: A `search_known_issues` tool accepts optional `query` (keyword), `product`, and `category` filters (AND semantics) and returns matching known-issue entries (title, product, category, symptom, remediation, optional doc link).
2: The KB is a **separate curated dataset** (≥ 12 generic entries across ARM/Network/Compute-host/Compute-guest and the three products) that does NOT copy any per-scenario root cause/resolution — it cannot leak the grading key.
3: An invalid `category` returns a structured `invalid_request`; no matches returns `ok` with an empty list; results are deterministic.
4: The tool exposes a clear MCP schema/description stating it is generic guidance, not ticket-specific RCA.
5: Unit + integration tests cover loading/validation, each filter, keyword search, no-match, and invalid category; the KB loads at startup via the same fail-fast pattern as scenarios.

## Story 5.2 Day-1 Workshop Starter Scaffold

As an instructor,
I want the Azure-themed Copilot starter files (instructions, prompts, a log-triage skill, sample data, and MCP config) in this repo,
so that participants can run the Day-1 labs and connect to this server without a separate starter repo.

### Acceptance Criteria

1: `.github/copilot-instructions.md` (Azure support context: Compute/Networking/ARM control-plane; cite-evidence; no PII; escalation) and a scoped `.github/instructions/*.instructions.md` example are present.
2: Two reusable prompt files (`summarize-ticket`, `draft-customer-reply`) with correct frontmatter are present and Azure-worded.
3: A `.github/skills/log-triage/` skill (SKILL.md + `parse_logs.py` + `error-codes.md`) triages Azure logs; the helper ranks ERROR/FATAL lines by an `AZURE-####` code.
4: `samples/logs/*.log`, `samples/tickets/*.md`, and a `samples/queries/*.kql` exist with realistic Azure content; sample ticket ids match server fixtures; log codes match the skill's reference table and regex.
5: `.vscode/mcp.json` (top-level `servers`) wires this server for stdio (with a commented HTTP + inputs example); it does not disturb `.vscode/settings.json`.

## Story 5.3 Day-2 Custom Agents

As an instructor,
I want the specialist and coordinator custom agents wired to this server's tools,
so that participants can run the Day-2 agent + coordinator labs.

### Acceptance Criteria

1: Three specialist agents exist — compute-diagnostics, network-diagnostics, controlplane-diagnostics — each referencing this server and naming the specific telemetry tools it uses.
2: A `support-triage` coordinator agent (tools: ['agent']) routes to the three specialists and offers a "Draft the resolution" handoff.
3: A minimal `ticket-writer` agent exists so the coordinator handoff resolves out of the box.
4: Agent frontmatter follows the workbook's conventions; specialist names exactly match the coordinator's `agents:` list.

## Story 5.4 Workbook Azure Re-Theme

As an instructor,
I want the participant workbook re-themed to Azure with its MCP labs pointed at this server,
so that the whole workshop is consistent and runnable against our real server.

### Acceptance Criteria

1: The workbook's product fiction (Gateway/Vault/Store) and `CONTOSO-####` ids are replaced with our Azure domains (Compute/Networking/ARM control-plane) and real `TICKET-XXXXXXXX` ids.
2: Lab 4's MCP config is replaced with our `.vscode/mcp.json` (stdio + http), the example flow uses real tools (`get_ticket` → `get_ticket_resources` → `query_arm_traces`), and it notes the server's MCP prompts.
3: Labs 5–6 reference the three Azure specialists and the coordinator; the KB-only variant uses `search_known_issues`.
4: Filenames/ids/log codes referenced in the workbook match the Story 5.2 assets exactly; a grep confirms no residual `CONTOSO-`/`Gateway`/`Vault`/`Store`/`@contoso/mcp-ticketing`/`contoso-kb`.
