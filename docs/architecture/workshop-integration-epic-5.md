# Workshop Integration (Epic 5)

Beyond the server, the repo ships a **GitHub Copilot workshop starter bundle**. These assets are documentation/config (not part of the server runtime), Azure-themed, and wired to the server's real tools. They live under `docs/assets/workshop/` (mirroring their target paths) as a **copy-into-place bundle** — Copilot/VS Code only auto-discover them at the canonical locations shown in parentheses, so participants (or a setup step) copy the bundle into the working repo root before the labs. This keeps the workshop assets separate from the repo's BMad tooling (`.github/chatmodes/`) and CI (`.github/workflows/`).

```plaintext
docs/assets/workshop/                    # the copy-into-place bundle (+ README with setup)
  .github/
    copilot-instructions.md              # Layer 1  (target: .github/copilot-instructions.md)
    instructions/kql.instructions.md     # Layer 1 scoped (applyTo **/*.kql)
    prompts/                             # Layer 2: summarize-ticket, draft-customer-reply
    skills/log-triage/                   # Layer 3: SKILL.md + parse_logs.py + error-codes.md
    agents/                              # Layer 4: compute/network/controlplane specialists,
                                         #   support-triage coordinator, ticket-writer
  .vscode/mcp.json                       # Layer 5  (target: .vscode/mcp.json) — wires contoso-support
  samples/
    logs/*.log                           # Azure log excerpts; ERROR lines carry an AZURE-#### code
    tickets/*.md                         # ticket write-ups; ids match server fixtures
    queries/*.kql                        # KQL demo file (scoped-instruction target)
src/contoso_support_mcp/
  fixtures/known_issues.yaml             # KB dataset (server runtime; sibling of scenarios/; own glob)
  tools/kb.py                            # search_known_issues tool (server runtime)
docs/external/Participant_Workbook.md    # the 2-day workbook, re-themed to Azure
```

> The KB tool (`tools/kb.py`, `known_issues.yaml`) is **server runtime**, not a
> copy-into-place asset — it stays under `src/`. Note: workshop sample logs are
> content, so a `.gitignore` exception keeps `docs/assets/workshop/samples/logs/*.log`
> tracked despite the repo's broad `*.log` rule.

**Key design rules:**
- **KB is decoupled** from scenarios — `known_issues.yaml` is generic guidance and never contains a per-ticket `RootCause`, so it cannot leak the grading key (`docs/scenario-index.md`).
- **`AZURE-####` codes** are the single source of truth shared across `samples/logs/*`, the skill's `error-codes.md`, and `parse_logs.py`'s regex.
- **Agents reference the server by its `mcp.json` key** (`contoso-support`) and name specific tools in their persona bodies.
- **No secrets / no PII** in any asset; the server needs no credentials.
- These assets are docs/config only — they do not affect the server's tool surface except for the KB tool, and are **not** exercised by the Python test suite (validated via the workbook's manual lab steps + a filename/id/code consistency check).
