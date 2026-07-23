# Per-Story Development Workflow

Standard pipeline run for **every** story, autonomously, pausing only for genuine blockers. A ship summary is produced at the end of each story.

## Pipeline

| # | Agent | Step | Output |
|---|-------|------|--------|
| 1 | SM (Bob) | Draft story from sharded epic + architecture | `docs/stories/{e}.{s}.*.md` (Status: Draft) |
| 2 | PO (Sarah) | Validate draft (anti-hallucination, readiness) | Validation report → story Status: Approved |
| 3 | QA (Quinn) | Risk analysis + test design | `docs/qa/assessments/{e}.{s}-risk-*.md`, `-test-design-*.md` |
| 4 | Dev (James) | Implement (code + tests, run them) | Source + tests; story Dev Agent Record; Status: Review |
| 5 | QA (Quinn) | Review + gate | `docs/qa/gates/{e}.{s}-*.yml`; story QA Results |
| 6 | PO (Sarah) | Close | Status: Done |
| 7 | — | Ship summary | What shipped + notes for the user |

## Rules

- Run steps 1→7 without stopping unless a genuine blocker requires a user decision.
- Each gate decision (PASS/CONCERNS/FAIL/WAIVED) is recorded. CONCERNS with low residual risk may proceed; FAIL stops for fixes.
- Commit at the end of each story (after PO close).
- Environment: Python 3.11.8, uv 0.11.19 (architecture targeted 3.12; adapted to `>=3.11`).

## Progress Tracker

| Story | Title | Status |
|-------|-------|--------|
| 1.1 | Project Scaffold & Health Tool (stdio) | ✅ Done (Gate PASS) |
| 1.2 | Network Transport Mode | ✅ Done (Gate PASS) |
| 1.3 | Configuration & Classroom Run Docs | ✅ Done (Gate PASS) |
| 2.1 | Scenario & Ticket Data Model + Loader | ✅ Done (Gate PASS) |
| 2.2 | Ticket Retrieval Tools (List & Get) | ✅ Done (Gate PASS) |
| 2.3 | Ticket Search & Filter Tool | ✅ Done (Gate PASS) |
| 2.4 | Ticket → Resource Pivot Tool | ✅ Done (Gate PASS) |
| 2.5 | Seed Scenario Batch & Consistency Validation | ✅ Done (Gate PASS) |
| 3.1 | Telemetry Data Model & Mock Kusto Schemas | ✅ Done (Gate PASS) |
| 3.2 | ARM Control-Plane Trace Query Tool | ✅ Done (Gate PASS) |
| 3.3 | Network Log Query Tool | ✅ Done (Gate PASS) |
| 3.4 | Compute Log Query Tools | ✅ Done (Gate PASS) |
| 3.5 | Telemetry Backfill & Multi-Round Authoring | ✅ Done (Gate PASS) |
| 4.1 | Expand Scenario Library to 100+ | ✅ Done (Gate PASS) |
| 4.2 | Difficulty Tagging & Multi-Round Distribution | ✅ Done (Gate PASS) |
| 4.3 | Guided MCP Prompts | ✅ Done (Gate PASS) |
| 4.4 | Full-Library Consistency & Classroom Readiness | ✅ Done (Gate PASS) |
| 5.1 | Known-Issues KB Tool | ✅ Done (Gate PASS) |
| 5.2 | Day-1 Workshop Starter Scaffold | ✅ Done (Gate PASS) |
| 5.3 | Day-2 Custom Agents | Pending |
| 5.4 | Workbook Azure Re-Theme | Pending |
