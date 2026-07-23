# Azure error / signal reference (excerpt)

Codes match the `AZURE-####` tokens in `samples/logs/*.log` and the
`parse_logs.py` regex.

| Code | Component | Likely cause | First remediation |
|------|-----------|--------------|-------------------|
| AZURE-1001 | ARM control-plane | Allocation/capacity failure (SKU unavailable in zone/region) | Retry in another zone or resize the SKU; request capacity/quota |
| AZURE-2003 | Network (NSG) | Outbound/inbound Deny by an NSG rule | Review the effective NSG rules for the flow; amend/reprioritize |
| AZURE-3005 | Compute host | Unplanned host degradation / platform event | Confirm in host logs; reimage/redeploy; use availability zones |
| AZURE-4008 | Compute guest | In-guest Windows service crash (SCM event 7031) | Inspect the in-guest Event Log and the application; host is healthy |

> On Day 2 the Contoso Support MCP server exposes `search_known_issues` — a live,
> read-only version of this table. Prefer it once MCP is connected.
