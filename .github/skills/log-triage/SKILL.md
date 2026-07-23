---
name: log-triage
description: Triage Azure control-plane, network (NSG), and compute host/guest logs to find the root-cause signal. Use when a user shares an Azure log file, activity-log excerpt, NSG flow log, or error output and needs the likely cause and next step.
argument-hint: path to a log file or pasted log lines
---
# Log Triage

Follow this procedure to triage Azure logs.

## 1. Classify
Scan for the first `ERROR` or `FATAL` line. Note its timestamp, Azure component
(ARM control-plane / Network / Compute host / Compute guest), and the signal code
(`AZURE-####`) plus any sub-status (e.g. `AllocationFailed`).

## 2. Look up the code
Match the code against [error-codes.md](./error-codes.md). If found, use its known
cause and first remediation.

## 3. Correlate
Check for `WARN` lines from the same component within 60s BEFORE the error — these
often reveal the trigger (e.g. a capacity warning before `AllocationFailed`, or an
NSG rule-change before a Deny).

## 4. Extract with the helper (for large logs)
Run the parser to get a ranked summary:

    python parse_logs.py <path-to-log>

## 5. Report
Return: the root-cause line, the `AZURE-####` code and its meaning, correlated
warnings, and the single recommended next step. If the Contoso Support MCP server
is connected, confirm live with the matching telemetry tool:
`query_arm_traces` / `query_network_logs` / `query_compute_host_logs` /
`query_compute_guest_logs`. Never state a cause you cannot support with a log line.
