# Database Schema

There is **no database**. "Schema" here means the shape of (a) the scenario fixture file and (b) the four mock Kusto tables. All are loaded into memory from YAML. Columns approximate real Azure log schemas closely enough to be believable while remaining tractable to author.

## Scenario Fixture File (one per scenario)

```yaml
# fixtures/scenarios/TICKET-10000001.yaml
scenario_id: TICKET-10000001
difficulty: single_round          # or multi_round
ticket:
  ticket_id: TICKET-10000001
  title: "VM deployment fails with allocation error"
  symptom: "Customer cannot start VM 'prod-web-01'; portal shows an allocation failure."
  azure_product: "Azure Virtual Machines"
  persona: windows_admin
  severity: Sev2
  status: Active
  created_at: "2026-05-14T09:12:00Z"
  updated_at: "2026-05-14T09:40:00Z"
  resource_ids:
    - "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-prod/providers/Microsoft.Compute/virtualMachines/prod-web-01"
resources:
  - resource_id: "/subscriptions/.../virtualMachines/prod-web-01"
    resource_type: "Microsoft.Compute/virtualMachines"
    name: "prod-web-01"
    resource_group: "rg-prod"
    subscription_id: "00000000-0000-0000-0000-000000000001"
    location: "eastus"
    instances: []
telemetry:
  arm_control_plane_traces:
    - time_generated: "2026-05-14T09:12:03Z"
      resource_id: "/subscriptions/.../virtualMachines/prod-web-01"
      correlation_id: "b1e2..."
      operation_name: "Microsoft.Compute/virtualMachines/write"
      caller: "admin@contoso.com"
      http_status_code: 409
      level: "Error"
      activity_status: "Failed"
      sub_status: "AllocationFailed"
      resource_group: "rg-prod"
      subscription_id: "00000000-0000-0000-0000-000000000001"
      client_ip: "13.68.x.x"
      properties: "SKU Standard_D4s_v5 not available in zone 1"
  network_logs: []
  compute_host_logs: []
  compute_guest_logs: []
root_cause:
  category: arm
  summary: "Capacity/allocation failure for the requested VM SKU in the target zone."
  resolution: "Retry in another zone or resize to an available SKU; request capacity if persistent."
investigation_path:
  - order: 1
    tool: query_arm_traces
    params: { time_range: "2026-05-14T09:00:00Z/2026-05-14T10:00:00Z" }
    reveals: "409 AllocationFailed on VM write operation."
```

## Table: ArmControlPlaneTraces

Approximates Azure Activity Log / ARM control-plane operations.

| Column | Type | Notes |
|---|---|---|
| time_generated | datetime | Row timestamp (UTC) |
| resource_id | string | ARM resource id |
| subscription_id | string | GUID |
| resource_group | string | |
| correlation_id | string | Correlates related operations |
| operation_name | string | e.g., `Microsoft.Compute/virtualMachines/write` |
| caller | string | User/principal |
| client_ip | string | |
| http_status_code | int | e.g., 200, 409, 503 |
| level | string | Informational / Warning / Error |
| activity_status | string | Started / Succeeded / Failed |
| sub_status | string | e.g., `AllocationFailed`, `Conflict` |
| properties | string | Free-form detail / error message |

## Table: NetworkLogs

Approximates NSG flow logs / Network Watcher.

| Column | Type | Notes |
|---|---|---|
| time_generated | datetime | |
| resource_id | string | NIC/NSG/VM resource id |
| subscription_id | string | |
| flow_direction | string | Inbound / Outbound |
| source_ip | string | |
| destination_ip | string | |
| source_port | int | |
| destination_port | int | |
| protocol | string | TCP / UDP / ICMP |
| action | string | Allow / Deny |
| nsg_rule_name | string | Matched rule |
| bytes_sent | int | |
| bytes_received | int | |
| packets_sent | int | |
| packets_received | int | |

## Table: ComputeHostLogs

Platform/host-layer events for VM and VMSS (Azure-side, not in-guest).

| Column | Type | Notes |
|---|---|---|
| time_generated | datetime | |
| resource_id | string | VM or VMSS resource id |
| subscription_id | string | |
| instance_id | string | VMSS instance (empty for plain VM) |
| host_node | string | Physical host identifier (opaque) |
| event_name | string | e.g., `LiveMigration`, `PlatformReboot`, `PlannedMaintenance`, `AllocationHealth`, `HostDegraded` |
| health_status | string | Healthy / Degraded / Unavailable |
| maintenance_type | string | None / Planned / Unplanned |
| level | string | Informational / Warning / Error |
| message | string | Free-form detail |

## Table: ComputeGuestLogs

In-guest **Windows** logs (Windows Event Log style) for VM and VMSS instances. Windows-only per MVP (PRD NFR7).

| Column | Type | Notes |
|---|---|---|
| time_generated | datetime | |
| resource_id | string | VM or VMSS resource id |
| subscription_id | string | |
| instance_id | string | VMSS instance (empty for plain VM) |
| computer | string | Guest hostname |
| channel | string | System / Application / Security |
| provider_name | string | Event source, e.g., `Service Control Manager` |
| event_id | int | Windows Event ID, e.g., 7031, 41, 1074 |
| level | string | Error / Warning / Information |
| task | string | Category |
| message | string | Event message |
