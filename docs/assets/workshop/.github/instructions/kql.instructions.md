---
applyTo: "**/*.kql"
---
# KQL / log-analytics guidance

- Always add an explicit time filter (e.g. `where TimeGenerated between (...)`) —
  never run an unbounded scan.
- Scope by resource: filter on `_ResourceId` / the resource id you're investigating.
- `project` only the columns you need; avoid `search *` across a whole table.
- Flag any query that could surface customer PII (caller identities, client IPs)
  for review before sharing the results externally.
