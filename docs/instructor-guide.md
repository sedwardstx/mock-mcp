# Instructor Guide — Contoso Support Ticketing MCP Server

> Running the 2-day GitHub Copilot workshop? Pair this with the **[Facilitator Guide](facilitator-guide.md)** — per-lab talking points and worked demos with expected output. This guide covers the MCP-server hosting and RCA-grading specifics.


This guide covers running the server for a class, choosing which scenarios to
assign, and grading student root-cause analyses (RCAs). For the student-facing
setup and walkthroughs, hand out the **[Student Handbook](student-handbook.md)**.

---

## 1. Two ways to run a class

### Option A — You host one server (recommended)

Run a single server on your machine over the network; students connect by URL and
install nothing.

```bash
uv sync                       # once
uv run contoso-support-mcp --transport http --host 0.0.0.0 --port 8000
```

- The MCP endpoint is **`http://<your-ip>:8000/mcp`**. Give students that URL.
- `--host 0.0.0.0` serves the classroom LAN (use `127.0.0.1` for loopback-only
  testing). Pick any free `--port`.
- Find your IP with `ipconfig` (Windows) / `ip addr` or `ifconfig` (macOS/Linux).
- Make sure your OS firewall allows inbound connections on the chosen port.
- **No auth/TLS** — this is intended for a **trusted classroom network** only.
  Don't expose it to the public internet.

Students use the **online** config blocks in the Student Handbook with your URL.

### Option B — Students self-host

Each student clones the repo, runs `uv sync`, and connects over stdio (the
**offline** config blocks in the handbook). No network dependency; good for
take-home work or a flaky classroom network.

---

## 2. Verify the class is connected

Have every student call **`get_server_info`** first — a `status: "ok"` response
confirms the connection. If you're hosting (Option A), the server handles many
concurrent students; a quick "everyone call `get_server_info` now" is a good
smoke test before starting.

---

## 3. Choose which scenarios to assign

Two generated references (regenerate after any data change — see §6):

- **[`scenario-coverage.md`](scenario-coverage.md)** — distribution by persona,
  Azure product, root-cause domain, and difficulty, plus a **difficulty ×
  category** cross-tab. Use it to pick a balanced mix and spot gaps.
- **[`scenario-index.md`](scenario-index.md)** — one row per scenario with the
  **expected root cause** and the **intended investigation tool sequence**. This
  is your answer key.

The library today: **103 scenarios**, **~26% multi-round**, spanning ARM /
Network / Compute (host + Windows guest, VM + VMSS) across both personas
(Windows admins and Azure developers).

### Picking a difficulty progression

- **Warm-up (single-round):** e.g. `TICKET-10000001` (ARM allocation failure) —
  one query finds a `409 / AllocationFailed`.
- **Stretch (multi-round):** e.g. `TICKET-10000026` — the obvious in-guest query
  is inconclusive; the student must pivot to host logs to find the `Degraded`
  event. Multi-round scenarios are marked `multi_round` in the index and each
  carries a **≥2-step investigation path**.
- Filter the index/coverage tables for the domain (`arm`, `network`,
  `compute_host`, `compute_guest`) and persona you want to emphasize.

---

## 4. Design a lab

1. Pick 1–3 scenarios from the index that match your learning objective (a
   domain, a persona, a difficulty).
2. Give students the ticket id(s) and have them start from the
   **`investigate_incident`** prompt.
3. Optionally withhold the domain hint to make them reason from the symptom.
4. For an assessment, mix at least one multi-round scenario so students must
   demonstrate iteration, not just a single lucky query.

---

## 5. Grade an RCA

For each assigned ticket, open its row in **`scenario-index.md`**. A strong
student answer should:

1. **Identify the affected resource** (from `get_ticket_resources`).
2. **Reach the expected root cause** — compare to the index's *Root cause* column.
3. **Cite the supporting telemetry** — the specific tool + row(s). The index's
   *Investigation* column lists the intended tool sequence; for multi-round
   scenarios, a full-marks answer names the query that was inconclusive **and**
   the one that revealed the cause.
4. **State the resolution or next steps.**

Because the data is **deterministic**, every student querying the same scenario
sees identical rows — answers are directly comparable and the "correct" evidence
is fixed.

---

## 6. Edit or grow the scenario library

Scenarios are plain data — no server code changes needed.

- **Hand-authored** scenarios live as individual files in
  `src/contoso_support_mcp/fixtures/scenarios/*.yaml`
  (`TICKET-10000001`–`003` are hand-written examples).
- **Generated** scenarios (`TICKET-10000004`+) come from
  `scripts/author_seed_scenarios.py`. Edit the curated entries or templates
  there and re-run it to regenerate:

```bash
uv run python scripts/author_seed_scenarios.py   # regenerate generated scenarios
uv run python scripts/scenario_index.py          # refresh docs/scenario-index.md
uv run python scripts/coverage_report.py         # refresh docs/scenario-coverage.md
uv run pytest -q                                 # validate consistency + determinism
```

**Consistency is enforced:** the test suite fails if any scenario's telemetry
doesn't contain evidence for its declared root cause, if a ticket references a
missing resource, or if a `multi_round` scenario lacks a ≥2-step path. So if
`pytest` is green, your data is safe to grade against.

---

## 7. Operations & troubleshooting

- **Concurrency:** the hosted server serves a full class of simultaneous
  connections (read-only, in-memory). No tuning needed.
- **Restarting:** just re-run the command; there's no state to preserve. Data is
  reloaded (and re-validated) on startup — a malformed fixture fails fast with a
  clear error naming the file.
- **Students can't connect (Option A):** confirm the port is open in your
  firewall, that you used `--host 0.0.0.0`, that students used your machine's LAN
  IP, and that the URL ends in `/mcp`.
- **Determinism:** identical queries always return identical rows, so a demo you
  rehearse will behave the same in class.
- **CI:** `.github/workflows/ci.yml` runs lint + the full test suite (unit /
  integration / e2e / consistency) on every push, so the repo stays trustworthy
  as you customize it.

---

## 8. Quick reference

| Task | Command / File |
|------|----------------|
| Host for the class | `uv run contoso-support-mcp --transport http --host 0.0.0.0 --port 8000` |
| Endpoint students use | `http://<your-ip>:8000/mcp` |
| Answer key (grading) | [`docs/scenario-index.md`](scenario-index.md) |
| Scenario mix / gaps | [`docs/scenario-coverage.md`](scenario-coverage.md) |
| Student instructions | [`docs/student-handbook.md`](student-handbook.md) |
| Regenerate data + docs | `author_seed_scenarios.py`, `scenario_index.py`, `coverage_report.py` |
| Validate everything | `uv run pytest -q` |
