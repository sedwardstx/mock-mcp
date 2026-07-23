# Workshop Starter Bundle

This folder holds the **Azure-themed GitHub Copilot workshop** starter assets, kept
separate from the repo's other tooling. It is a **copy-into-place bundle**: GitHub
Copilot and VS Code only auto-discover these files at canonical paths
(`.github/…`, `.vscode/mcp.json`) and by relative path (`samples/…`), so before the
workshop copy the bundle contents into your working repo root.

## Contents (mirrors the target layout)

```
docs/assets/workshop/
├── .github/
│   ├── copilot-instructions.md          # Layer 1 (Lab 1)
│   ├── instructions/kql.instructions.md # Layer 1 scoped (Lab 1 Stretch)
│   ├── prompts/                         # Layer 2 (Lab 2)
│   ├── skills/log-triage/               # Layer 3 (Lab 3)
│   └── agents/                          # Layer 4 (Labs 5–6)
├── .vscode/mcp.json                     # Layer 5 (Lab 4) — wires the contoso-support server
└── samples/{logs,tickets,queries}/      # data the Day-1 labs read
```

## Set up (copy into place)

From the repo root:

```bash
# copy the whole bundle into your working tree
cp -a docs/assets/workshop/.github  .
cp -a docs/assets/workshop/.vscode  .
cp -a docs/assets/workshop/samples  .
```

Then Copilot picks up the instructions/prompts/skills/agents, VS Code discovers
`.vscode/mcp.json`, and the labs' `samples/…` paths resolve.

> Alternatively, **build the files yourself during the labs** as the workbook
> instructs — this bundle is the facilitator's reference / answer copy.

## Notes

- The server itself is **not** here — it's the `contoso_support_mcp` package under
  `src/`. `.vscode/mcp.json` launches it via `uv` and `${workspaceFolder}`, so copy
  the bundle into a workspace that contains this repo (or adjust the `--directory`).
- No secrets and no PII. The mock server needs no credentials.
- The `AZURE-####` codes in `samples/logs/*` match `skills/log-triage/error-codes.md`
  and the `parse_logs.py` regex.
