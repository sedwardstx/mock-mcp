---
description: 'Draft a customer-facing reply from an internal Azure diagnosis'
agent: 'agent'
argument-hint: 'the internal diagnosis / notes'
---
Write a concise, empathetic customer reply based on the internal Azure diagnosis below.
- Acknowledge the impact.
- State what we found in plain language — **no internal hostnames** (e.g.
  `HN-EASTUS-9920`), no `host_node`/`caller`/internal IPs, no raw log lines.
- Give the next step and a realistic timeframe.
- Do NOT promise a fix time we cannot commit to. Flag anything needing a human decision.

Return the draft only; a human will review before sending.
