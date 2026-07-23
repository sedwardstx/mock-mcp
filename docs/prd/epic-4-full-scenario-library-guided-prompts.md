# Epic 4 Full Scenario Library & Guided Prompts

**Epic Goal:** Complete the MVP teaching experience. This epic grows the scenario library to the full **100+** with the target difficulty mix (≥25% multi-round) and broad Azure-product/persona coverage, validates consistency across the whole library at scale, and authors the crafted MCP **prompts** that guide student agents through scoping, follow-up questioning, iterative investigation, and RCA. It also produces the instructor-facing scenario index and final classroom-readiness docs so labs can be mapped, run, and graded.

## Story 4.1 Expand Scenario Library to 100+ with Coverage

As an instructor,
I want the scenario library grown to at least 100 distinct, well-distributed scenarios,
so that I have enough varied material to run many labs without repetition.

### Acceptance Criteria

1: The library contains **≥ 100 distinct scenarios**, each with ticket, resource(s), correlated telemetry, and a defined root cause + resolution/next-step.
2: Scenarios span a broad spread of Azure products/platforms and both customer personas (Windows admins and Azure developers), with root causes distributed across ARM, Network, and Compute domains.
3: Ticket ids remain unique and all scenarios conform to the data model and pass loader validation.
4: A coverage summary (by product/domain/persona) is generated or documented so gaps are visible.
5: All ticket and telemetry tools return correct, deterministic results across the full library, verified by the test suite.

## Story 4.2 Difficulty Tagging & Multi-Round Distribution

As an instructor,
I want scenarios tagged by difficulty with a verified multi-round proportion,
so that I can select scenarios of appropriate challenge and guarantee the intended learning progression.

### Acceptance Criteria

1: Each scenario carries a difficulty indicator (e.g., single-round vs. multi-round, and/or a difficulty level).
2: **At least 25%** of scenarios are multi-round, verified by an automated check over the library.
3: Multi-round scenarios each retain a documented intended investigation path (from Epic 3) to support grading.
4: A distribution report (counts by difficulty/round-type and by domain) is produced and documented.
5: The difficulty tags are queryable/visible to instructors (e.g., via a documented field or a filter), enabling scenario selection for a given lab.

## Story 4.3 Guided MCP Prompts for the Diagnostic Workflow

As a student's AI agent,
I want crafted MCP prompts that guide the diagnostic workflow,
so that I use the tools effectively — scoping, asking follow-ups, iterating, and producing an RCA.

### Acceptance Criteria

1: The server exposes MCP **prompts** covering the workflow: scoping/triage of a ticket, formulating follow-up questions, iterative investigation across the telemetry tools, and producing an RCA that resolves the issue or documents next steps.
2: Prompts reference the actual tool surface (ticket, resource, and telemetry tools) and encourage correct multi-step, multi-round tool use.
3: Prompts are discoverable via the MCP protocol with clear names and descriptions.
4: Prompts are parameterized where useful (e.g., by ticket id) per MCP prompt conventions.
5: A documented example shows an agent using a prompt to progress from a ticket to an RCA on a representative scenario (including a multi-round one).
6: Integration tests assert the prompts are discoverable and return well-formed prompt content.

## Story 4.4 Full-Library Consistency Validation & Classroom Readiness

As an instructor,
I want whole-library validation and classroom-ready materials,
so that I can trust the data and run graded labs on day one.

### Acceptance Criteria

1: The consistency check runs across the entire 100+ library and verifies, for every scenario, that ticket↔resource↔telemetry↔root-cause are coherent; it passes in CI/test and fails on any inconsistency.
2: An instructor-facing **scenario index** is produced (id, product/domain, persona, difficulty/round-type, one-line summary, and the intended root cause/investigation path) to support mapping labs to scenarios and grading.
3: Classroom run docs are finalized for both transport modes, including how to select scenarios and verify connectivity.
4: A full test run (unit + integration + end-to-end) passes against the complete library and tool/prompt surface.
5: The determinism guarantee is verified across the full library (identical inputs → identical outputs) as an automated check.
