---
description: 'Summarize an Azure support ticket into problem, impact, and next steps'
agent: 'agent'
argument-hint: 'paste ticket text or reference a ticket file (e.g. samples/tickets/TICKET-10000001.md)'
---
Summarize the Azure support ticket below into:
1. **Problem** — one sentence.
2. **Customer impact** — severity and which Azure resource / who is affected.
3. **What we know** — key facts: Azure product, `resource_id`, the telemetry signal
   (e.g. ARM `sub_status`, NSG rule, `event_name`/`event_id`), region, timestamps.
4. **Recommended next step** — the single best diagnostic action, naming the
   telemetry tool to use (`query_arm_traces` / `query_network_logs` /
   `query_compute_host_logs` / `query_compute_guest_logs`).

Keep it under 150 words. Do not invent details that are not present. No customer PII.
