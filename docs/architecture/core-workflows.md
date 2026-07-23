# Core Workflows

## Single-round RCA (e.g., ARM control-plane failure)

```mermaid
sequenceDiagram
    participant A as AI Agent
    participant M as MCP Surface
    participant R as Repository
    A->>M: get_ticket("TICKET-10000001")
    M->>R: get_ticket(id)
    R-->>M: ticket (symptom, product, resource_ids)
    M-->>A: ticket
    A->>M: get_ticket_resources("TICKET-10000001")
    M->>R: get_resources(id)
    R-->>M: [VM resource]
    M-->>A: resources
    A->>M: query_arm_traces(resource_id, time_range)
    M->>R: query_telemetry(ARM, resource, range)
    R-->>M: traces (deploy failure evidence + noise)
    M-->>A: rows
    A-->>A: Form RCA (control-plane root cause + resolution)
```

## Multi-round RCA (evidence distributed across tables)

```mermaid
sequenceDiagram
    participant A as AI Agent
    participant M as MCP Surface
    participant R as Repository
    A->>M: get_ticket + get_ticket_resources
    M-->>A: VMSS resource (instances)
    A->>M: query_compute_host_logs(resource, range)
    M-->>A: host logs (inconclusive: healthy host)
    A-->>A: Hypothesis: issue is in-guest, not host
    A->>M: query_compute_guest_logs(resource, instance_id, range)
    M-->>A: guest Windows events (service crash evidence)
    A-->>A: Refine RCA; confirm via narrowed query if needed
```
