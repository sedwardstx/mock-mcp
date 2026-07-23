# Goals and Background Context

## Goals

- Deliver a fully-mocked, offline-capable Python MCP server that students can connect AI Agents and Skills to during hands-on labs.
- Emulate a realistic Azure support-engineering backend: `TICKET-XXXXXXXX` incidents plus correlated Kusto telemetry (ARM, Network, Compute).
- Provide a curated library of **≥ 100 distinct problem scenarios** with matching symptoms, correlated logs, and defined root causes.
- Ensure a meaningful subset (≥ 25%) of scenarios require **multiple rounds of investigation and tool calls** to reach a root-cause analysis (RCA).
- Support two deployment modes: **student-hosted local (stdio, no network)** and **instructor-hosted over the network**.
- Guarantee deterministic, repeatable tool responses so labs are consistent and gradeable across all student machines.
- Ship crafted MCP **prompts** that guide student agents through scoping, follow-up questioning, iterative investigation, and RCA.
- Reduce classroom setup/connection time to under 10 minutes for a class of students.

## Background Context

Students learning to build AI Agents and Skills need a realistic, safe, and reliable backend to practice tool orchestration and multi-step diagnostic reasoning. Today they are limited to trivial "hello world" MCP servers (too shallow to teach real agent planning) or live systems (which require Azure subscriptions, incur cost, expose real data, and break in flaky classroom networks). Neither teaches the core skill: reasoning across multiple correlated data sources to connect a customer-reported symptom to its underlying platform root cause.

The Contoso Support Ticketing MCP Server closes that gap. It presents a believable "Contoso Support" backend whose customers — a mix of Windows administrators and Azure developers — file incidents against Azure products and platforms. Behind each ticket sits mocked, correlated telemetry across Kusto tables (ARM control-plane traces, Network logs, and Compute logs for VMs/VMSS including platform-host and Windows guest logs). All data is mocked and embedded, so the server runs entirely offline on a laptop with zero external dependencies, giving students an authentic Azure-support feel in a controlled, deterministic sandbox.

## Change Log

| Date       | Version | Description                        | Author       |
|------------|---------|------------------------------------|--------------|
| 2026-07-23 | 1.0     | Initial PRD draft from Project Brief | John (PM)  |
