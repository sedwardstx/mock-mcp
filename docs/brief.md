# Project Brief: Contoso Support Ticketing MCP Server

## Executive Summary

The **Contoso Support Ticketing MCP Server** is a self-contained, fully-mocked Model Context Protocol (MCP) server designed as a classroom teaching tool. It emulates a realistic enterprise support-ticketing platform for "Contoso," a fictional Microsoft-style organization whose customers file Azure-related support incidents. Running locally on an instructor's laptop, it exposes MCP **tools**, **prompts**, and mock **resources** that students connect to while learning to build AI Agents and Skills.

- **Product concept:** A local MCP server that returns believable support tickets and correlated Azure telemetry (Kusto/ARM/Network/Compute logs) — all mocked, no cloud dependencies.
- **Primary problem solved:** Students learning to build AI Agents need a safe, realistic, offline data source to practice tool-calling, prompt design, and multi-step diagnostic reasoning — without provisioning real Azure resources or exposing production data.
- **Target market:** Instructors and students in AI Agent / Skill development courses (internal Microsoft enablement or partner training).
- **Key value proposition:** A single, dependency-light server that turns abstract "connect your agent to an MCP server" lab instructions into a concrete, repeatable, realistic exercise mirroring real Azure support-engineering workflows.

## Problem Statement

**Current state and pain points.** When teaching students to build AI Agents and Skills against MCP servers, instructors need a backend that is (a) realistic enough to demonstrate genuine agentic diagnostic workflows, (b) safe enough to run in a classroom without credentials or data-governance risk, and (c) reliable enough to behave identically on every student's connection. Today, instructors either point students at trivial "hello world" MCP servers (too shallow to teach real tool orchestration) or attempt to use live systems (require Azure subscriptions, incur cost, leak real data, and break when the network is flaky).

**Impact.** Shallow demos fail to teach the core skill: reasoning across multiple tool calls to correlate a customer-reported symptom with underlying platform telemetry. Live systems introduce setup friction that consumes lab time, produces inconsistent student experiences, and creates compliance risk.

**Why existing solutions fall short.** Generic sample MCP servers don't model a domain with enough depth (multiple correlated data sources, realistic IDs, layered logs) to exercise agent planning. Real ticketing/observability platforms can't be safely handed to a classroom.

**Urgency.** As AI Agent and Skill development becomes a core competency, hands-on labs are the bottleneck. A purpose-built, mock, Azure-flavored ticketing MCP server unblocks an entire curriculum of agent-building labs.

## Proposed Solution

Build a **stateless, fully-mocked MCP server** that presents itself as the "Contoso Support" backend. It ships with a curated, deterministic mock dataset covering:

- **Support tickets** in `TICKET-XXXXXXXX` format, representing Azure product/platform incidents reported by Windows administrators and Azure developers.
- **Kusto-style telemetry tables** associated with the customer's Azure resources — ARM control-plane traces, Network logs, and Compute logs (VM and VMSS, both platform/host logs and per-machine guest logs; Windows-only for mock guest data).

The server exposes:
- **Tools** to query tickets and to gather the correlated logs/traces from the mock Kusto tables.
- **Prompts** — crafted, reusable prompt templates that guide students' agents toward effective use of the tools (e.g., a triage/diagnosis workflow).

The dataset is intentionally deep: **at least 100 distinct problem scenarios**, each with a customer-reported symptom, a matching underlying root cause, and correlated telemetry across the Kusto tables. Scenarios are designed so a student's agent must **scope the problem, ask follow-up questions, and perform root-cause analysis (RCA)** to either resolve the issue or determine next steps. A meaningful subset of scenarios require **multiple rounds of investigation and tool calls** — the symptom in the ticket is not enough; the agent must pull logs, form a hypothesis, pull more logs to confirm, and iterate.

**Key differentiators:**
- **Domain depth:** Multiple correlated data sources mirror real Azure support-engineering, so agents must *plan* — read a ticket, identify the resource, pull the right Kusto table, correlate.
- **Zero external dependencies:** Runs entirely on the instructor's laptop; no Azure subscription, credentials, or internet required.
- **Deterministic & repeatable:** Every student sees the same data, so labs are reproducible and gradeable.

**Why it will succeed:** It hits the sweet spot between "too trivial to teach anything" and "too risky/heavy to run in class," giving students an authentic Azure-support feel in a controlled sandbox.

**High-level vision:** The definitive teaching backend for MCP-based agent labs, extensible to additional Azure domains and log types over time.

## Target Users

### Primary User Segment: Students Learning to Build AI Agents & Skills

- **Profile:** Developers and IT pros enrolled in AI Agent / Skill development training. Mixed background — some are Windows administrators, some are software developers building on Azure.
- **Current behaviors/workflows:** Following structured lab instructions; connecting an agent framework or Skill to an MCP server; iterating on prompts and tool-calling logic.
- **Specific needs:** A realistic, always-available backend; clear tool schemas; example prompts to learn from; deterministic data so their agent's output can be checked against expected results.
- **Goals:** Learn to design agents that plan and execute multi-step tool workflows — scoping a problem, asking follow-up questions, iterating across multiple tool calls, and performing RCA to reach a resolution or documented next step. Build confidence to later target real systems.

### Secondary User Segment: Instructors / Lab Authors

- **Profile:** The instructor running the classroom (and curriculum authors who write the labs).
- **Current behaviors/workflows:** Standing up lab infrastructure on a laptop; distributing connection details; authoring lab exercises and grading criteria.
- **Specific needs:** One-command startup; predictable behavior across all student connections; a dataset rich enough to support many distinct lab scenarios; easy to reset.
- **Goals:** Deliver reliable, repeatable labs; minimize setup friction and support burden during class; map lab exercises to specific tickets and expected telemetry.

## Goals & Success Metrics

### Business Objectives

- Enable a full curriculum of MCP agent-building labs runnable entirely offline on a single instructor laptop by first classroom delivery.
- Reduce lab setup/connection time to under 10 minutes for a classroom of students.
- Ship a dataset of **at least 100 distinct problem scenarios** with matching symptoms and correlated logs, a meaningful subset requiring multi-round investigation.
- Support both deployment modes: **student-hosted local** (no network) and **instructor-hosted over the network**.

### User Success Metrics

- A student can connect an agent to the server and successfully complete a ticket-triage lab without instructor intervention.
- Students exercise multi-step tool orchestration (ticket → resource → Kusto query) rather than single-shot calls.
- Provided prompts measurably improve student agent success versus no prompt guidance.

### Key Performance Indicators (KPIs)

- **Lab completion rate:** % of students completing the core triage lab unaided — target ≥ 90%.
- **Time-to-connect:** Median minutes from server start to first successful tool call — target ≤ 10 min.
- **Data realism:** Instructor rating that mock data believably represents Azure support telemetry — target ≥ 4/5.
- **Determinism:** 100% identical tool responses for identical queries across student sessions.
- **Scenario depth:** ≥ 100 distinct scenarios, with ≥ 25% requiring multiple rounds of investigation/tool calls to reach RCA.

## MVP Scope

### Core Features (Must Have)

- **MCP server scaffold (Python):** A runnable MCP server built with the Python MCP SDK, supporting **two transport modes**: (1) **local stdio** for student self-hosting with no network access, and (2) a **network transport** (e.g., streamable HTTP / SSE over a local host:port) for a single instructor-hosted server the whole class connects to.
- **Ticket tools:** Tools to list/search/get support tickets in `TICKET-XXXXXXXX` format, with realistic Azure-incident content authored for Windows-admin and Azure-developer personas.
- **Kusto telemetry tools:** Tools to query mock Kusto tables for a resource — ARM traces, Network logs, and Compute logs (VM & VMSS; platform/host logs and Windows guest logs).
- **Mock data layer:** A deterministic, embedded dataset of **≥ 100 distinct problem scenarios**, each linking a ticket → symptom → Azure resource → correlated telemetry with a defined root cause, so RCA labs work end-to-end. A meaningful subset (≥ 25%) require **multiple rounds of investigation/tool calls** — the initial symptom is insufficient and the agent must iterate (hypothesis → pull more logs → confirm).
- **Crafted prompts:** MCP prompt templates guiding effective tool use across the full workflow — scoping, follow-up questioning, iterative investigation, and RCA to resolution-or-next-steps.
- **Startup & docs:** Simple run instructions for both transport modes and connection details for the classroom.

### Out of Scope for MVP

- Real Azure / Kusto connectivity or authentication.
- Persisting ticket state or write operations (create/update/resolve tickets).
- Non-Windows guest OS logs.
- Multi-tenant or per-student isolated datasets.
- Web UI / dashboards.

### MVP Success Criteria

Students can, using only the server's tools and prompts, connect an agent (via either transport mode) that scopes a ticket, identifies the affected Azure resource, retrieves the correct correlated Kusto telemetry, iterates through follow-up investigation where needed, and produces a plausible RCA — either resolving the issue or documenting next steps — with identical results across all student machines.

## Post-MVP Vision

### Phase 2 Features

- Write/mutation tools (add ticket notes, change status) to teach stateful agent workflows.
- Additional telemetry domains (Storage, App Service, Key Vault) and non-Windows guest logs.
- Injectable "scenario packs" so instructors can swap datasets per lab.

### Long-term Vision

Become the standard, extensible teaching backend for MCP agent labs — a library of realistic, safe, domain-rich mock servers spanning multiple Azure and enterprise scenarios.

### Expansion Opportunities

- A generator that produces fresh deterministic datasets from a seed.
- Difficulty tiers (noisy logs, red-herring traces) to teach robust agent reasoning.
- Companion grading harness that checks student agent outputs against expected diagnoses.

## Technical Considerations

### Platform Requirements

- **Target Platforms:** Local execution on a laptop (Windows primary; cross-platform desirable). Two deployment modes: student-hosted (local, offline) and instructor-hosted (served over the local network to the class).
- **Browser/OS Support:** N/A (MCP server, not a web app); students connect via MCP-capable agent tooling.
- **Performance Requirements:** Sub-second tool responses; the instructor-hosted network mode must handle a classroom of concurrent student connections without external services.

### Technology Preferences

- **Frontend:** None (server exposes MCP tools/prompts/resources only).
- **Backend:** **Python**, using the official Python MCP SDK. Server supports both **stdio** (local student hosting) and a **network transport** (streamable HTTP / SSE for instructor hosting).
- **Database:** None external; deterministic mock data embedded in-process (in-memory / bundled fixture files, e.g. JSON/YAML).
- **Hosting/Infrastructure:** Runs locally; no cloud. Distributed as an easily-launched Python package/script runnable in either transport mode.

### Architecture Considerations

- **Repository Structure:** Single repo; clear separation of MCP surface (tools/prompts) from the mock data layer so datasets can evolve independently.
- **Service Architecture:** Stateless request/response; deterministic responses keyed on inputs.
- **Integration Requirements:** Conform to MCP spec so any MCP-compatible agent framework or Skill can connect.
- **Security/Compliance:** No real data, credentials, or network calls — eliminating data-governance risk in the classroom.

## Constraints & Assumptions

### Constraints

- **Budget:** Internal/enablement effort; no external service spend (offline by design).
- **Timeline:** Target readiness by first classroom delivery. _[Specific date TBD.]_
- **Resources:** Built and maintained by the instructor/curriculum team.
- **Technical:** Python + Python MCP SDK; must run offline on a laptop; all data mocked; conform to MCP spec; support both stdio and network transports.

### Key Assumptions

- Students use MCP-capable agent tooling able to connect to a locally-run server.
- A deterministic, curated dataset is sufficient (no need for live or randomized data) for teaching.
- Windows-only guest OS mock logs are acceptable for the target audience.
- A curated library of ≥ 100 well-authored scenarios (ticket + symptom + correlated telemetry + root cause) is enough to support the intended labs, with a subset requiring multi-round investigation.

## Risks & Open Questions

### Key Risks

- **Insufficient realism:** If mock tickets/telemetry feel fake, labs lose pedagogical value and instructor confidence.
- **Connection friction:** If connecting agents to the local server is fiddly, class time is lost — undermining the core value prop.
- **Concurrency at classroom scale:** Many simultaneous student connections could expose transport or performance issues.
- **Scope creep:** Temptation to add real integrations undermines the "safe, offline, deterministic" design goal.

### Open Questions

- What exact Kusto schemas/columns should the mock tables mirror for ARM, Network, and Compute logs?
- How should scenarios be authored/structured for maintainability at 100+ (e.g., one file per scenario vs. tables) and how are multi-round scenarios modeled so follow-up queries reveal new evidence?
- For instructor-hosted network mode, does MCP client auth/identity matter in the classroom, or is an open local endpoint acceptable?
- Which specific lab exercises map to which scenarios, and what defines a "correct" RCA for grading?
- How is the difficulty distribution set (single-shot vs. multi-round) across the 100+ scenarios?

### Areas Needing Further Research

- Representative real-world schemas for ARM traces, Azure Network logs, and Compute (VM/VMSS host + guest) logs to make mocks believable.
- Classroom-scale MCP connection patterns and best practices.
- Prompt patterns that most effectively guide student agents through multi-tool diagnostic workflows.

## Appendices

### C. References

- Model Context Protocol specification and SDKs (to be linked).
- Azure Monitor / Kusto (KQL) log schema references for ARM, Network, and Compute (to be linked).

## Next Steps

### Immediate Actions

1. Specify the mock Kusto table schemas (columns) for ARM, Network, and Compute logs.
2. Design the scenario data model that scales to 100+ scenarios and supports multi-round investigation (follow-up queries reveal new evidence).
3. Author the ≥ 100 scenarios: ticket + symptom + resource + correlated telemetry + defined root cause, with the target single-shot vs. multi-round distribution.
4. Draft the crafted MCP prompt templates for scoping, follow-up questioning, iterative investigation, and RCA.
5. Stand up the Python MCP server scaffold supporting stdio and network transports.
6. Hand off to PM to generate the PRD.

### PM Handoff

This Project Brief provides the full context for the **Contoso Support Ticketing MCP Server**. Please start in 'PRD Generation Mode', review the brief thoroughly to work with the user to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements.
