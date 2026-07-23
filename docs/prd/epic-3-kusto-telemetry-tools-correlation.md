# Epic 3 Kusto Telemetry Tools & Correlation

**Epic Goal:** Make end-to-end RCA possible. This epic defines the mock Kusto table schemas and telemetry data model, exposes query tools for ARM control-plane traces, Network logs, and Compute logs (host/platform and Windows guest, for VM and VMSS), backfills correlated telemetry for existing scenarios, and authors additional scenarios — including the first **multi-round** ones where the agent must query, hypothesize, and query again. By the end, a student's agent can go from a ticket all the way to a defensible root cause using correlated telemetry, on a cumulative library of roughly 60 scenarios.

## Story 3.1 Telemetry Data Model & Mock Kusto Table Schemas

As a server developer,
I want mock Kusto table schemas and a telemetry data model linked to scenarios and resources,
so that every telemetry tool queries one consistent, believable source correlated to tickets.

### Acceptance Criteria

1: Documented mock table schemas approximate real Azure log schemas for: **ARM control-plane traces**, **Network logs**, **Compute host/platform logs** (VM and VMSS), and **Compute Windows guest logs** (VM and VMSS), each with realistic, log-type-appropriate columns (including timestamps and a resource identifier).
2: The scenario data model is extended so telemetry rows are associated with a scenario and its resource(s), and reference the scenario's root cause (i.e., logs contain the evidence supporting that root cause).
3: The fixture loader loads telemetry deterministically alongside tickets, with schema validation and fail-fast on malformed telemetry.
4: A common query semantic is defined for all telemetry tools — scoping by resource identifier and time range, plus log-type-appropriate filters — returning structured rows.
5: Sample telemetry for a few existing scenarios is included and loads successfully, sufficient to develop and test the query tools.
6: Unit tests cover telemetry loading, schema validation (including a negative case), and determinism.

## Story 3.2 ARM Control-Plane Trace Query Tool

As a student's AI agent,
I want to query ARM control-plane traces for a resource,
so that I can investigate deployment, configuration, and control-plane operations related to an incident.

### Acceptance Criteria

1: A tool (e.g., `query_arm_traces`) accepts a resource identifier, an optional time range, and ARM-appropriate filters, and returns matching trace rows.
2: Results are scoped to the requested resource/time range and are deterministic for identical inputs.
3: Results are correlated to the scenario — for scenarios whose root cause is control-plane related, the traces contain the supporting evidence (with realistic surrounding noise where appropriate).
4: An empty result (no matching traces) returns an empty set, not an error; malformed inputs return a clear validation message.
5: The tool exposes a clear MCP schema documenting parameters, filters, and returned columns.
6: Integration tests assert correct, deterministic results for representative scenarios.

## Story 3.3 Network Log Query Tool

As a student's AI agent,
I want to query Network logs for a resource,
so that I can investigate connectivity, NSG/routing, and network-related incidents.

### Acceptance Criteria

1: A tool (e.g., `query_network_logs`) accepts a resource identifier, an optional time range, and network-appropriate filters, and returns matching log rows.
2: Results are scoped and deterministic for identical inputs.
3: Results are correlated to the scenario — network-root-caused scenarios contain supporting evidence with realistic noise.
4: Empty results return an empty set; malformed inputs return a clear validation message.
5: The tool exposes a clear MCP schema documenting parameters, filters, and returned columns.
6: Integration tests assert correct, deterministic results for representative scenarios.

## Story 3.4 Compute Log Query Tools (Host & Windows Guest, VM & VMSS)

As a student's AI agent,
I want to query Compute platform-host logs and Windows guest logs for VMs and VMSS,
so that I can investigate both the Azure host layer and the in-guest Windows behavior behind an incident.

### Acceptance Criteria

1: Tools are provided to query **Compute host/platform logs** and **Compute Windows guest logs**, each supporting both **VM** and **VMSS** resources (including addressing an individual instance within a VMSS).
2: Each tool accepts a resource identifier, an optional time range, and compute-appropriate filters, and returns matching rows scoped to that resource/instance and time range.
3: Results are deterministic for identical inputs and correlated to the scenario — compute-root-caused scenarios contain supporting evidence across host and/or guest logs, with realistic noise.
4: Guest logs are Windows-only, consistent with the MVP scope.
5: Empty results return an empty set; malformed inputs (e.g., a VMSS instance that doesn't exist) return a clear validation message.
6: Each tool exposes a clear MCP schema documenting parameters, filters, and returned columns.
7: Integration tests assert correct, deterministic results for representative VM and VMSS scenarios across host and guest logs.

## Story 3.5 Telemetry Backfill & Multi-Round Scenario Authoring

As an instructor,
I want existing scenarios backfilled with correlated telemetry and new multi-round scenarios added,
so that agents can perform full RCA and some incidents require iterative investigation.

### Acceptance Criteria

1: All seed scenarios from Epic 2 are backfilled with correlated telemetry across the relevant tables, so each has an evidence trail supporting its defined root cause.
2: Additional scenarios are authored to reach a cumulative total of ~60 distinct scenarios, spanning ARM/Network/Compute root causes across both personas.
3: At least a handful of scenarios are **multi-round**: the ticket symptom alone is insufficient, and the supporting evidence is distributed such that an agent must query telemetry, form a hypothesis, and query again (a different table, time range, or resource/instance) to reach the root cause.
4: For each multi-round scenario, the intended investigation path (which queries reveal which evidence) is documented to support lab authoring and grading.
5: The consistency check is extended to verify, for every scenario, that the telemetry actually contains evidence consistent with the defined root cause; it runs in the test suite and fails on any inconsistency.
6: End-to-end tests demonstrate at least one single-round and one multi-round scenario solved via the tool sequence (ticket → resource → telemetry → root cause).
