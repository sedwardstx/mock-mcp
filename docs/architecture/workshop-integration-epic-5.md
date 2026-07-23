# Workshop Integration (Epic 5)

Beyond the server, the repo doubles as the **GitHub Copilot workshop starter repo**. These assets are documentation/config (not part of the server runtime) and are Azure-themed and wired to the server's real tools:

```plaintext
.github/
  copilot-instructions.md              # Layer 1: always-on Azure support context
  instructions/kql.instructions.md     # Layer 1: scoped (applyTo **/*.kql)
  prompts/                             # Layer 2: summarize-ticket, draft-customer-reply
  skills/log-triage/                   # Layer 3: SKILL.md + parse_logs.py + error-codes.md
  agents/                              # Layer 4: compute/network/controlplane specialists,
                                       #   support-triage coordinator, ticket-writer
samples/
  logs/*.log                           # Azure log excerpts; ERROR lines carry an AZURE-#### code
  tickets/*.md                         # ticket write-ups; ids match server fixtures
  queries/*.kql                        # KQL demo file (scoped-instruction target)
.vscode/mcp.json                       # Layer 5: wires the contoso-support server (stdio + http)
src/contoso_support_mcp/
  fixtures/known_issues.yaml           # KB dataset (sibling of scenarios/; own glob)
  tools/kb.py                          # search_known_issues tool
docs/external/Participant_Workbook.md  # the 2-day workbook, re-themed to Azure
```

**Key design rules:**
- **KB is decoupled** from scenarios — `known_issues.yaml` is generic guidance and never contains a per-ticket `RootCause`, so it cannot leak the grading key (`docs/scenario-index.md`).
- **`AZURE-####` codes** are the single source of truth shared across `samples/logs/*`, the skill's `error-codes.md`, and `parse_logs.py`'s regex.
- **Agents reference the server by its `mcp.json` key** (`contoso-support`) and name specific tools in their persona bodies.
- **No secrets / no PII** in any asset; the server needs no credentials.
- These assets are docs/config only — they do not affect the server's tool surface except for the KB tool, and are **not** exercised by the Python test suite (validated via the workbook's manual lab steps + a filename/id/code consistency check).
