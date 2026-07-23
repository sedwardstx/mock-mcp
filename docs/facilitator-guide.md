# Facilitator Guide — Building AI Support Agents with GitHub Copilot

A comprehensive companion for **running** the 2-day workshop in
`docs/external/Participant_Workbook.md`. For every module and lab it gives you:
talking points, a **concrete example to present live** (exact commands + the
expected result), common gotchas, timing, and the checkpoint to confirm.

**Related docs**
- Participant lab manual → `docs/external/Participant_Workbook.md`
- Starter assets (copy-into-place) → `docs/assets/workshop/` (+ its `README.md`)
- MCP server hosting, scenario selection & **grading** → `docs/instructor-guide.md`
- Student quick-reference → `docs/student-handbook.md`
- Answer key (per-scenario root cause + tool path) → `docs/scenario-index.md`

---

## How to use this guide

Keep it open on your presenter machine. Each lab section is ordered
**Say → Show → Watch-for → Checkpoint** so you can talk, demo, help, and verify.
Every "Show" example has been run against the real server — the expected outputs
below are what you should actually see.

The room is mixed-skill. Pair people, insist everyone hits each **Checkpoint**
before moving on, and treat the Stretch goals as optional.

---

## Before the workshop (facilitator prep)

1. **Confirm org policy:** agent mode + MCP enabled (`chat.mcp.enabled`), Copilot
   licenses seated, latest VS Code + Copilot/Copilot Chat extensions.
2. **Get the repo** on your machine and every participant's (or a shared clone).
   Run `uv sync` once so `contoso-support-mcp` resolves.
3. **Put the starter bundle in place.** The assets live at `docs/assets/workshop/`
   as a copy-into-place bundle. From the repo root:
   ```bash
   cp -a docs/assets/workshop/.github docs/assets/workshop/.vscode docs/assets/workshop/samples .
   ```
   (Participants can instead build each file during the labs — the bundle is your
   reference/answer copy.)
4. **Decide how the MCP server runs** (Day 2):
   - **You host it** for the class (simplest): `uv run contoso-support-mcp --transport http --host 0.0.0.0 --port 8000` → give out `http://<your-ip>:8000/mcp`. Confirm your firewall allows the port. See `docs/instructor-guide.md` §1.
   - **Students self-host** over stdio via the bundled `.vscode/mcp.json`.
5. **Pre-run every "Show" example below once** so nothing surprises you live.
6. **Pick your scenarios** from `docs/scenario-coverage.md` / `docs/scenario-index.md`.

> ℹ **Tool names in agents.** `tools:` in the `.agent.md` files reference the MCP
> server by its `mcp.json` key `contoso-support`; the persona body names the
> specific tools. If a participant's Configure Tools picker shows namespaced names,
> that's fine — the server key grants all its tools.

---

# DAY 1 — Foundations

## Module 0 — Welcome & Setup (30 min)

**Say:** goals, agenda, ground rules (pair up, ask early). The five customization
layers are the mental model for the whole workshop.

**Show — the setup that everyone mirrors:**
- Open the repo in VS Code, confirm Copilot is signed in, model picker shows models.
- Copy the bundle into place (command above); point out the new `.github/`,
  `.vscode/mcp.json`, and `samples/` now present.
- Open Chat → **Agent** mode.

**Checkpoint:** everyone green — signed in, repo open, bundle copied, Agent mode on,
models visible.

## Module 1 — The Agent Landscape (45 min)

**Say:** agent vs autocomplete vs chat; the agentic loop (plan → act → observe →
repeat) with approval prompts; **Ask / Edit / Agent** modes; the five layers
(one diagram). Why it matters for support: turn runbooks + tribal knowledge into
shareable, consistent agents.

**Show — the marquee Day-1 demo (investigate a real Azure log):**
In Agent mode, type:
> `Investigate samples/logs/arm-allocation-failure.log and tell me the likely cause.`

Expected: the agent reads the file, reasons, and reports that the failure is the
`ERROR` line **`AZURE-1001 … http=409 subStatus=AllocationFailed`** — SKU
`Standard_D4s_v5` not available in availability **zone 1** — and notes the WARN
"capacity signal low" 30s earlier as the trigger. Narrate the loop + the approval
prompt for the file read.

**Watch-for:** if the agent hand-waves, ask the follow-up "Which exact log line
supports that?" to force evidence-citing — this previews the Lab 1 instructions.

## Lab 1 — First Agent-Mode Task + Team Instructions (60 min)

**Say:** capture team context so Copilot answers like a Contoso Azure support
engineer (cite evidence, no PII, escalation).

**Show:**
1. Re-run the investigate prompt above; note it forms a hypothesis and cites a line.
2. Show `.github/copilot-instructions.md` (Azure domains + domain→tool map +
   escalation). In a **fresh** chat, re-ask a similar question and point out the
   answer now cites a specific log line and respects the PII/escalation rules.

**Watch-for:** participants forgetting the file is repo-root `.github/…`; a fresh
chat is needed to see the instructions take effect.

**Checkpoint:** instructions file committed; a fresh agent answer cites a specific
line from `arm-allocation-failure.log`.

**Stretch (KQL scoped instruction):** open `.github/instructions/kql.instructions.md`
and `samples/queries/allocation-failures.kql` (matches) plus any non-`.kql` file
(doesn't) — the guidance only applies to the `.kql` file.

## Module 2 — Reusable Prompts (30 min)

**Say:** prompt-file anatomy + frontmatter (`description`, `agent`, `tools`,
`argument-hint`); `/name` invocation and the editor play button.

**Show:** run `/summarize-ticket` and paste a couple of lines of a ticket; show the
structured Problem / Impact / What-we-know / Next-step output.

## Lab 2 — Build Support Prompt Files (60 min)

**Show:**
- `/summarize-ticket samples/tickets/TICKET-10000001.md` → a <150-word summary:
  Problem (VM won't start — allocation failure), Impact (Sev2, `prod-web-01`),
  What we know (409 AllocationFailed, Standard_D4s_v5, zone 1), Next step (query
  ARM traces / retry in another zone).
- Take that diagnosis and run `/draft-customer-reply` → an empathetic reply with
  **no** internal hostnames/IPs and a realistic next step.

**Watch-for:** both prompts must appear under `/`; if not, the file is misnamed or
not under `.github/prompts/`.

**Checkpoint:** both prompts appear under `/` and produce useful output on a sample
ticket.

## Module 3 — Agent Skills (45 min)

**Say:** a skill = a folder Copilot loads when relevant; **progressive disclosure**
(name+description first, body on use, resources only when referenced); auto vs
manual (`/log-triage`) invocation.

**Show:** ask a natural log question and watch the `log-triage` skill load on its own.

## Lab 3 — Build a Troubleshooting Skill (75 min) — Day 1 Capstone

**Show — the helper across all four sample logs (this is the payoff demo):**
```bash
for f in samples/logs/*.log; do echo "== $f"; python .github/skills/log-triage/parse_logs.py "$f"; done
```
Expected ranked codes (each maps to a domain via `error-codes.md`):

| Sample log | Code | Meaning |
|---|---|---|
| `arm-allocation-failure.log` | `AZURE-1001` | ARM allocation/capacity failure |
| `nsg-deny-1433.log` | `AZURE-2003` | NSG Deny (outbound 1433) |
| `vm-host-degraded.log` | `AZURE-3005` | Compute host degraded |
| `vm-guest-service-crash.log` | `AZURE-4008` | In-guest Windows service crash (SCM 7031) |

Then in Agent mode: "Here's an Azure VM log with an allocation failure — what's the
root cause?" → the skill auto-loads, classifies, correlates the WARN, and reports
`AZURE-1001 / AllocationFailed` with the next step.

**Watch-for:** if the parser prints `UNCODED`, the log's ERROR line is missing its
`AZURE-####` code — the codes must match `error-codes.md` and the regex.

**Checkpoint:** the skill triggers automatically **and** via `/log-triage`, and the
helper prints a ranked code list.

**Day 1 wrap (30 min):** recap the five layers; preview Day 2 (MCP + specialists +
coordinator). Homework: sketch a skill/specialist for a real domain.

---

# DAY 2 — MCP, Custom Agents & Coordinators

## Module 4 — Recap & MCP Concepts (30 min)

**Say:** what MCP is (servers expose **tools / resources / prompts** over a standard
protocol); `.vscode/mcp.json` structure; server types (stdio / http / sse); the
**trust dialog**; secrets via `inputs`; least-privilege tooling. Our
`contoso-support` server exposes 10 tools + 3 prompts.

## Lab 4 — Connect to a Company MCP Server (75 min)

**Show — the end-to-end MCP flow (the Day-2 anchor demo):**
1. Open the bundled `.vscode/mcp.json`; accept the **trust dialog**;
   `MCP: List Servers` → `contoso-support` running. `Configure Tools` shows
   `get_ticket`, `search_tickets`, the four `query_*` tools, and
   `search_known_issues`.
2. In Agent mode:
   > `Look up TICKET-10000001, get its resources, then query the ARM control-plane traces for that resource and tell me the root cause.`

   Expected tool sequence + result:
   - `get_ticket` → VM won't start, allocation failure, `prod-web-01`, Sev2.
   - `get_ticket_resources` → `…/rg-prod/providers/Microsoft.Compute/virtualMachines/prod-web-01`.
   - `query_arm_traces` → a `Failed` / `409` / `AllocationFailed` trace row → RCA:
     no capacity for `Standard_D4s_v5` in zone 1; retry another zone or resize.
3. **KB tool:** `search_known_issues` with `query: "allocation"` → **`KB-ARM-001`**
   ("VM start or deployment fails with AllocationFailed") — generic guidance, a hint,
   not the ticket's answer.
4. **Prompts are a third primitive:** open the `/mcp` prompt picker → run
   `investigate_incident` with `ticket_id=TICKET-10000001` and watch it drive the
   whole scope→investigate→RCA loop.

**Watch-for:** `${workspaceFolder}` in the stdio config must resolve to this repo
(where the server lives); for http mode the URL must end in `/mcp` and be reachable.

**Checkpoint:** at least one MCP tool call succeeds in agent mode (a ticket lookup
returns data).

**Stretch:** toggle between the stdio and instructor-hosted http blocks; curate
tools to least privilege (e.g. only `get_ticket`, `get_ticket_resources`,
`query_arm_traces`, `search_known_issues`).

## Module 5 — Custom Agents (45 min)

**Say:** `.agent.md` anatomy (`description`, `tools`, `model`, `mcp-servers`,
persona body); agent = persona + curated tools (vs skill = procedure, instructions
= standards); selecting from the agents dropdown.

**Show:** select `compute-diagnostics` and give it a compute symptom (below).

## Lab 5 — Build a Specialist Troubleshooting Agent (75 min)

**Show — `compute-diagnostics` on a real guest-fault ticket:**
Select `compute-diagnostics`, then:
> `Diagnose TICKET-10000003 — a Windows service keeps crashing on the VM.`

Expected: it scopes with `get_ticket`/`get_ticket_resources` (VM `sql-node-01`),
queries `query_compute_guest_logs`, and finds the **Error / Service Control Manager
/ event 7031** row (alongside a benign MSSQLSERVER 17055) → concludes an **in-guest**
service crash, host healthy; recommends investigating the app/service, no prod change
without rollback. If you ask it about a network angle, it **defers** to
`network-diagnostics` — demonstrate staying in lane.

**Group assignment:** each group builds one of `compute-diagnostics`,
`network-diagnostics`, `controlplane-diagnostics` so Lab 6 has real sub-agents.
(Good single-domain test tickets: network → `TICKET-10000002`; control-plane →
`TICKET-10000001`; compute → `TICKET-10000003`.)

**Checkpoint:** the specialist appears in the dropdown and stays in its lane —
defers out-of-domain issues and names the right specialist.

## Module 6 — Coordinator Agents (45 min) — Marquee Topic

**Say:** the routing problem; `agents:` + the `agent` tool = sub-agent invocation;
`handoffs:` = guided transitions; patterns (router, sequential handoff, fallback);
when **not** to delegate.

## Lab 6 — Build the Coordinator (90 min) — Workshop Capstone

**Show — three beats with the `support-triage` coordinator:**

1. **Ambiguous → clarify + route.** Select `support-triage`, then:
   > `A VM came back online by itself overnight and a config change we pushed earlier failed — what happened?`

   Expected: it asks a **clarifying question** (e.g. the exact time window / region),
   then classifies and routes (compute-host and/or control-plane).

2. **Cross-domain → coordinate + synthesize.**
   > `VMSS instances are failing their health probes AND a recent scale-out didn't add capacity.`

   Expected: it engages `network-diagnostics` and `controlplane-diagnostics` in
   sequence and synthesizes.

3. **Multi-round → "don't stop at the first query" (the star demo).** Use
   `TICKET-10000026`:
   > `Investigate TICKET-10000026.`

   Expected: the coordinator routes to `compute-diagnostics`, which first checks
   `query_compute_guest_logs` → **only a benign `Information` row (inconclusive)** →
   forms a new hypothesis and checks `query_compute_host_logs` → **`HostDegraded` /
   `Degraded`** → the real root cause is a platform host event. This is the
   iteration lesson made concrete.

4. **Handoff.** After a confirmed diagnosis, accept the **"Draft the resolution"**
   handoff → it hands to `ticket-writer` (human-review gate).

**Watch-for (Appendix B gotcha):** if the coordinator won't delegate, its
`agents:` names must exactly match the specialist filenames and it needs
`tools: ['agent']`.

**Checkpoint:** the coordinator routes at least two different problem types and
offers the "Draft the resolution" handoff.

## Module 7 — Ship It: Governance (30 min)

**Say:** share via the repo (commit `.github/agents|prompts|skills` + `.vscode/mcp.json`);
version/review agents like code; **security** — MCP trust + least privilege, secrets
via `inputs`, approval gates, human-in-the-loop for anything customer-facing or
production-changing; avoid over-automation. (Our mock needs no secret — but the
`inputs` pattern is still the standard for real servers.)

## Capstone share-out & close (45 min)

Groups demo their coordinator + specialists (5 min each). Retro, resources,
completion checklist.

---

## Appendix A — Demo cheat-sheet (all examples in one place)

| Lab | Action to present | Expected result |
|---|---|---|
| 1 | Agent: *Investigate samples/logs/arm-allocation-failure.log …* | cites `AZURE-1001` / 409 `AllocationFailed`, SKU zone 1 |
| 1 | Add `.github/copilot-instructions.md`, ask again (fresh chat) | answer cites a specific log line; respects PII/escalation |
| 2 | `/summarize-ticket samples/tickets/TICKET-10000001.md` | Problem/Impact/Know/Next-step, <150 words |
| 2 | `/draft-customer-reply` on the diagnosis | empathetic reply, no hostnames/IPs |
| 3 | `python .github/skills/log-triage/parse_logs.py samples/logs/*.log` | ranked `AZURE-1001/2003/3005/4008` |
| 3 | Natural log question | `log-triage` auto-loads; reports the code + cause |
| 4 | Agent: *Look up TICKET-10000001 → resources → query_arm_traces* | 409 AllocationFailed trace → RCA |
| 4 | `search_known_issues` query `allocation` | `KB-ARM-001` |
| 4 | `/mcp` prompt `investigate_incident` ticket_id `TICKET-10000001` | full scope→investigate→RCA loop |
| 5 | `compute-diagnostics` on `TICKET-10000003` | guest SCM **event 7031** → in-guest crash, host healthy |
| 6 | `support-triage` ambiguous prompt | asks a clarifying question, classifies, routes |
| 6 | `support-triage` on `TICKET-10000026` | guest benign (inconclusive) → host `Degraded` (root cause) |
| 6 | Accept "Draft the resolution" | hands to `ticket-writer` (human-review gate) |

## Appendix B — Demo tickets (quick facts)

| Ticket | Domain | Resource | The evidence |
|---|---|---|---|
| `TICKET-10000001` | ARM control-plane | VM `prod-web-01` | ARM `409 AllocationFailed`, Standard_D4s_v5, zone 1 |
| `TICKET-10000002` | Network | VMSS `api-vmss` (`_0`,`_1`) | NSG `DenyDbOutbound`, outbound TCP 1433 |
| `TICKET-10000003` | Compute guest | VM `sql-node-01` | Guest **SCM event 7031** (service crash) |
| `TICKET-10000008` | Compute host | VMSS `data-vmss` | Host `HostDegraded`/`Degraded` on `data-vmss_0` |
| `TICKET-10000026` | Compute host (**multi-round**) | VM `host-26` | Guest benign → host `Degraded` (needs a 2nd query) |

## Appendix C — Timing at a glance

| Day 1 | min | Day 2 | min |
|---|---|---|---|
| Module 0 Setup | 30 | Module 4 MCP concepts | 30 |
| Module 1 Landscape | 45 | Lab 4 Connect MCP | 75 |
| Lab 1 Instructions | 60 | Module 5 Custom agents | 45 |
| Module 2 Prompts | 30 | Lab 5 Specialist | 75 |
| Lab 2 Prompt files | 60 | Module 6 Coordinators | 45 |
| Module 3 Skills | 45 | Lab 6 Coordinator | 90 |
| Lab 3 Skill (capstone) | 75 | Module 7 Governance | 30 |
| Day 1 wrap | 30 | Capstone & close | 45 |

## Appendix D — Common gotchas (facilitator quick-scan)

| Symptom | Fix |
|---|---|
| Agent mode missing | Extension outdated or org policy off — update / check admin |
| No models in picker | Not signed in / license not seated — re-auth |
| MCP server won't start (stdio) | `uv sync` first; `${workspaceFolder}` must be this repo; check MCP output |
| MCP server unreachable (http) | Wrong host/port; URL must end in `/mcp`; firewall/LAN |
| Skill not triggering | Weak description; test with `/log-triage` to confirm it loads |
| Parser prints `UNCODED` | Log ERROR line missing its `AZURE-####` code |
| Agent not in dropdown | Wrong folder or filename not `*.agent.md` |
| Coordinator won't delegate | Needs `tools: ['agent']`; `agents:` names must match specialist filenames |
| Empty tool result | Normal — no rows for that scope; try another tool/time window |

---

*This guide pairs with the Participant Workbook; for MCP-server hosting and RCA
grading specifics, see `docs/instructor-guide.md`.*
