"""Authoring aid: emit generated scenario fixtures (Stories 2.5 + 3.5).

Owns scenarios TICKET-10000004 .. TICKET-10000060 (curated 4-20 preserved from
Story 2.5; templated 21-60). Emits category-correct **telemetry** (an evidence
row + benign noise) for every scenario, and a handful of **multi-round**
scenarios where the "obvious" table is benign and the real evidence lives in
another table (2-step investigation_path).

Hand-authored TICKET-10000001..003 are NOT touched here.

Deterministic: no clock/random. Run:
    uv run python scripts/author_seed_scenarios.py
"""

from __future__ import annotations

from pathlib import Path

import yaml

FIXTURES = (
    Path(__file__).resolve().parents[1]
    / "src" / "contoso_support_mcp" / "fixtures" / "scenarios"
)

SUB = {
    "windows_admin": "00000000-0000-0000-0000-000000000001",
    "azure_developer": "00000000-0000-0000-0000-000000000002",
}
LOCATIONS = ["eastus", "westus2", "westeurope", "centralus"]
CATEGORIES = ["arm", "network", "compute_host", "compute_guest"]

TABLE_FOR = {
    "arm": "arm_control_plane_traces",
    "network": "network_logs",
    "compute_host": "compute_host_logs",
    "compute_guest": "compute_guest_logs",
}
TOOL_FOR = {
    "arm_control_plane_traces": "query_arm_traces",
    "network_logs": "query_network_logs",
    "compute_host_logs": "query_compute_host_logs",
    "compute_guest_logs": "query_compute_guest_logs",
}
# For a multi-round scenario of category X, the "obvious" (benign) table to look at first.
OBVIOUS_TABLE = {
    "compute_guest": "compute_host_logs",
    "compute_host": "compute_guest_logs",
    "network": "arm_control_plane_traces",
    "arm": "network_logs",
}
CAT_PREFIX = {"arm": "deploy", "network": "net", "compute_host": "host", "compute_guest": "guest"}

# --- Curated single-round entries 4-20 (preserved from Story 2.5) ------------
# (num, persona, product, rtype, category, name, rg, title, symptom, summary, resolution)
CURATED = [
    (4, "windows_admin", "Azure Virtual Machines", "vm", "compute_host", "app-vm-01", "rg-prod",
     "VM rebooted unexpectedly overnight",
     "Customer reports VM 'app-vm-01' rebooted on its own around 02:00 with no user action.",
     "The Azure platform performed a host reboot on the node hosting the VM.",
     "Confirm the platform reboot in host logs; use availability zones for resilience."),
    (5, "azure_developer", "Azure Virtual Machine Scale Sets", "vmss", "arm", "web-vmss", "rg-web",
     "Scale-out fails to add instances",
     "Developer reports 'web-vmss' will not scale out; new instances never appear.",
     "The scale operation fails with an allocation/quota error for the SKU in the region.",
     "Request a quota increase or choose an available SKU/region; retry."),
    (6, "windows_admin", "Azure Virtual Machines", "vm", "network", "jump-vm-01", "rg-ops",
     "Cannot RDP to VM",
     "Admin cannot connect via RDP (3389) to 'jump-vm-01'; the connection times out.",
     "An NSG rule denies inbound TCP 3389 from the admin's source range.",
     "Add/adjust an NSG rule to allow inbound 3389 from the trusted admin source."),
    (7, "azure_developer", "Azure Virtual Machines", "vm", "compute_guest", "batch-vm-02", "rg-batch",
     "Application crashes with out-of-memory",
     "Developer reports their batch app on 'batch-vm-02' crashes intermittently.",
     "The in-guest application is terminated under memory pressure (guest OOM).",
     "Right-size the VM SKU or fix the app's memory usage; the host is healthy."),
    (8, "windows_admin", "Azure Virtual Machine Scale Sets", "vmss", "compute_host", "data-vmss", "rg-data",
     "Some scale set instances are unhealthy",
     "Admin reports two instances of 'data-vmss' show as unhealthy while others are fine.",
     "A platform host degradation affected specific nodes hosting those instances.",
     "Reimage/redeploy the affected instances; the scale set spreads across healthy nodes."),
    (9, "azure_developer", "Azure Networking", "vm", "network", "lb-app-vm-01", "rg-net",
     "Intermittent 503s behind the load balancer",
     "Developer reports intermittent HTTP 503 responses from a load-balanced app.",
     "An NSG rule blocks the load balancer health-probe port, marking the backend unhealthy.",
     "Allow the load balancer probe port in the NSG (AzureLoadBalancer service tag)."),
    (10, "windows_admin", "Azure Virtual Machines", "vm", "arm", "sql-vm-03", "rg-data",
     "VM resize operation keeps failing",
     "Admin cannot resize 'sql-vm-03'; the operation returns a failure each time.",
     "The resize control-plane operation fails due to a conflict / SKU unavailable.",
     "Deallocate before resizing, or choose an available SKU; retry."),
    (11, "azure_developer", "Azure Virtual Machines", "vm", "compute_guest", "ci-vm-04", "rg-ci",
     "Service won't start — disk full",
     "Developer reports a service on 'ci-vm-04' fails to start after a build filled the disk.",
     "The in-guest service fails because the OS/data disk is full.",
     "Free space or expand the disk in-guest; not an Azure platform issue."),
    (12, "windows_admin", "Azure Virtual Machines", "vm", "compute_host", "erp-vm-01", "rg-erp",
     "VM briefly unresponsive during the day",
     "Admin reports 'erp-vm-01' froze for about a minute mid-afternoon, then recovered.",
     "A platform live-migration paused the VM briefly while moving it off a degraded host.",
     "Expected platform behavior; use availability zones and app-level retry."),
    (13, "azure_developer", "Azure Virtual Machine Scale Sets", "vmss", "network", "api-vmss-2", "rg-api2",
     "Backend pool members failing health probe",
     "Developer reports 'api-vmss-2' members fail the load balancer health probe.",
     "A new NSG deny rule blocks the health-probe port to the instances.",
     "Allow the probe port from the AzureLoadBalancer tag in the NSG."),
    (14, "windows_admin", "Azure Virtual Machines", "vm", "arm", "policy-vm-01", "rg-gov",
     "Deployment update denied by policy",
     "Admin's update to 'policy-vm-01' is rejected immediately with a deny error.",
     "An Azure Policy assignment denies the requested change.",
     "Adjust the resource to comply, or update the policy assignment/exemption."),
    (15, "azure_developer", "Azure Virtual Machines", "vm", "compute_guest", "win-app-05", "rg-app",
     "Windows Update reboot loop",
     "Developer reports 'win-app-05' repeatedly restarts after installing updates.",
     "An in-guest Windows Update triggered recurring restarts.",
     "Roll back the update or pause updates in-guest; the platform is healthy."),
    (16, "windows_admin", "Azure Virtual Machine Scale Sets", "vmss", "arm", "img-vmss", "rg-img",
     "Scale set create fails — image not found",
     "Admin's new scale set 'img-vmss' fails to create referencing a custom image.",
     "The control-plane operation returns a 404 for the referenced image.",
     "Correct the image reference (id/version) and recreate the scale set."),
    (17, "azure_developer", "Azure Networking", "vm", "network", "dns-vm-01", "rg-net2",
     "DNS resolution failing from VM",
     "Developer reports 'dns-vm-01' cannot resolve external hostnames.",
     "An NSG rule blocks outbound DNS (port 53) from the VM.",
     "Allow outbound 53 to the DNS resolver in the NSG."),
    (18, "windows_admin", "Azure Virtual Machines", "vm", "compute_host", "fin-vm-02", "rg-fin",
     "Planned maintenance caused unexpected downtime",
     "Admin reports 'fin-vm-02' went down during a maintenance window they didn't expect.",
     "A planned platform maintenance event caused a reboot of the host.",
     "Review scheduled events; use maintenance configurations / availability zones."),
    (19, "azure_developer", "Azure Virtual Machines", "vm", "compute_guest", "svc-vm-06", "rg-svc",
     "App pool crashing with .NET exception",
     "Developer reports the app pool on 'svc-vm-06' recycles repeatedly.",
     "An in-guest application fault crashes the worker process.",
     "Fix the application exception; the Azure host shows no fault."),
    (20, "windows_admin", "Azure Virtual Machines", "vm", "network", "egress-vm-01", "rg-edge",
     "Outbound HTTPS blocked from VM",
     "Admin reports 'egress-vm-01' can no longer reach external HTTPS endpoints.",
     "An NSG rule denies outbound TCP 443 from the VM.",
     "Allow the required outbound 443 destinations in the NSG."),
]

# Templated text per category for generated entries 21-60.
CAT_TEXT = {
    "arm": {
        "product": "Azure Virtual Machines",
        "title": "Control-plane operation failing on {name}",
        "symptom": "Customer reports a management operation on '{name}' fails immediately in the portal.",
        "summary": "The ARM control-plane operation fails (error status) for the resource.",
        "resolution": "Inspect the failed operation in ARM traces; correct the request and retry.",
    },
    "network": {
        "product": "Azure Networking",
        "title": "Connectivity blocked to/from {name}",
        "symptom": "Customer reports '{name}' cannot reach a required endpoint after a network change.",
        "summary": "An NSG rule denies the required traffic for the resource.",
        "resolution": "Amend the NSG rule to allow the required flow.",
    },
    "compute_host": {
        "product": "Azure Virtual Machines",
        "title": "Unexpected platform event on {name}",
        "symptom": "Customer reports '{name}' had an unexpected interruption with no user action.",
        "summary": "A platform host event affected the resource.",
        "resolution": "Confirm the host event in host logs; use availability zones for resilience.",
    },
    "compute_guest": {
        "product": "Azure Virtual Machines",
        "title": "In-guest Windows fault on {name}",
        "symptom": "Customer reports an application/service on '{name}' fails repeatedly.",
        "summary": "An in-guest Windows fault is responsible; the Azure host is healthy.",
        "resolution": "Investigate the in-guest Windows event; this is not an Azure platform fault.",
    },
}

# Multi-round selection (templated range): a scenario is multi-round when
# `num % 3 == 2`, giving ~26% of the library. Chosen so TICKET-10000026 stays
# multi-round (used by the multi-round e2e test). True category is the entry's
# category; the "obvious" table is benign, real evidence in the category table.
def _is_multi_round(num: int) -> bool:
    return num % 3 == 2

SEVERITY_CYCLE = ["Sev2", "Sev3", "Sev2", "Sev3", "Sev4"]


def _resource_id(sub, rg, rtype, name):
    kind = "virtualMachineScaleSets" if rtype == "vmss" else "virtualMachines"
    return f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/{kind}/{name}"


def _ts(day, hour, minute=0):
    return f"2026-05-{day:02d}T{hour:02d}:{minute:02d}:00Z"


# --- Telemetry row builders (evidence=True adds the root-cause evidence) ------
def arm_rows(rid, sub, rg, instances, day, evidence):
    rows = [{
        "time_generated": _ts(day, 9, 5), "resource_id": rid, "subscription_id": sub,
        "resource_group": rg, "correlation_id": f"corr-{day}-a", "operation_name":
        "Microsoft.Compute/virtualMachines/read", "caller": "user@contoso.com",
        "client_ip": "13.68.0.1", "http_status_code": 200, "level": "Informational",
        "activity_status": "Succeeded", "sub_status": "OK", "properties": "Routine read.",
    }]
    if evidence:
        rows.append({
            "time_generated": _ts(day, 9, 12), "resource_id": rid, "subscription_id": sub,
            "resource_group": rg, "correlation_id": f"corr-{day}-b", "operation_name":
            "Microsoft.Compute/virtualMachines/write", "caller": "user@contoso.com",
            "client_ip": "13.68.0.1", "http_status_code": 409, "level": "Error",
            "activity_status": "Failed", "sub_status": "OperationFailed",
            "properties": "Control-plane operation failed.",
        })
    return rows


def network_rows(rid, sub, rg, instances, day, evidence):
    rows = [{
        "time_generated": _ts(day, 14, 31), "resource_id": rid, "subscription_id": sub,
        "flow_direction": "Outbound", "source_ip": "10.0.0.4", "destination_ip": "10.0.1.10",
        "source_port": 51544, "destination_port": 443, "protocol": "TCP", "action": "Allow",
        "nsg_rule_name": "AllowHttpsOutbound", "bytes_sent": 4096, "bytes_received": 8192,
        "packets_sent": 12, "packets_received": 14,
    }]
    if evidence:
        rows.append({
            "time_generated": _ts(day, 14, 33), "resource_id": rid, "subscription_id": sub,
            "flow_direction": "Outbound", "source_ip": "10.0.0.4", "destination_ip": "10.0.2.20",
            "source_port": 51602, "destination_port": 1433, "protocol": "TCP", "action": "Deny",
            "nsg_rule_name": "DenyOutbound", "bytes_sent": 0, "bytes_received": 0,
            "packets_sent": 3, "packets_received": 0,
        })
    return rows


def host_rows(rid, sub, rg, instances, day, evidence):
    healthy_instance = instances[1] if len(instances) > 1 else ""
    degraded_instance = instances[0] if instances else ""
    rows = [{
        "time_generated": _ts(day, 10, 5), "resource_id": rid, "subscription_id": sub,
        "instance_id": healthy_instance, "host_node": "HN-EASTUS-4471", "event_name": "HealthCheck",
        "health_status": "Healthy", "maintenance_type": "None", "level": "Informational",
        "message": "Routine health check passed.",
    }]
    if evidence:
        rows.append({
            "time_generated": _ts(day, 10, 7), "resource_id": rid, "subscription_id": sub,
            "instance_id": degraded_instance, "host_node": "HN-EASTUS-9920",
            "event_name": "HostDegraded", "health_status": "Degraded", "maintenance_type":
            "Unplanned", "level": "Error", "message": "Host node reported a degraded state.",
        })
    return rows


def guest_rows(rid, sub, rg, instances, day, evidence):
    instance = instances[0] if instances else ""
    rows = [{
        "time_generated": _ts(day, 8, 31), "resource_id": rid, "subscription_id": sub,
        "instance_id": instance, "computer": "GUESTVM", "channel": "Application",
        "provider_name": "Application", "event_id": 1000, "level": "Information",
        "task": "None", "message": "Routine informational event.",
    }]
    if evidence:
        rows.append({
            "time_generated": _ts(day, 8, 42), "resource_id": rid, "subscription_id": sub,
            "instance_id": instance, "computer": "GUESTVM", "channel": "System",
            "provider_name": "Service Control Manager", "event_id": 7031, "level": "Error",
            "task": "None", "message": "A service terminated unexpectedly.",
        })
    return rows


ROW_BUILDERS = {
    "arm_control_plane_traces": arm_rows,
    "network_logs": network_rows,
    "compute_host_logs": host_rows,
    "compute_guest_logs": guest_rows,
}


def build_telemetry_and_path(category, multi, rid, sub, rg, instances, day):
    cat_table = TABLE_FOR[category]
    telemetry = {cat_table: ROW_BUILDERS[cat_table](rid, sub, rg, instances, day, evidence=True)}
    if multi:
        obvious = OBVIOUS_TABLE[category]
        telemetry[obvious] = ROW_BUILDERS[obvious](rid, sub, rg, instances, day, evidence=False)
        path = [
            {"order": 1, "tool": TOOL_FOR[obvious],
             "params": {"time_range": f"{_ts(day, 8)}/{_ts(day, 15)}"},
             "reveals": "Only benign rows here — inconclusive; form a new hypothesis."},
            {"order": 2, "tool": TOOL_FOR[cat_table],
             "params": {"time_range": f"{_ts(day, 8)}/{_ts(day, 15)}"},
             "reveals": "The evidence supporting the root cause appears in this table."},
        ]
    else:
        path = [
            {"order": 1, "tool": TOOL_FOR[cat_table],
             "params": {"time_range": f"{_ts(day, 8)}/{_ts(day, 15)}"},
             "reveals": "The evidence supporting the root cause appears in this table."},
        ]
    return telemetry, path


def build_scenario(num, persona, product, rtype, category, name, rg,
                   title, symptom, summary, resolution, multi):
    tid = f"TICKET-{10000000 + num:08d}"
    sub = SUB[persona]
    rid = _resource_id(sub, rg, rtype, name)
    resource_type = (
        "Microsoft.Compute/virtualMachineScaleSets" if rtype == "vmss"
        else "Microsoft.Compute/virtualMachines"
    )
    instances = [f"{name}_0", f"{name}_1"] if rtype == "vmss" else []
    day = (num % 27) + 1
    telemetry, path = build_telemetry_and_path(category, multi, rid, sub, rg, instances, day)
    return {
        "scenario_id": tid,
        "difficulty": "multi_round" if multi else "single_round",
        "ticket": {
            "ticket_id": tid, "title": title, "symptom": symptom, "azure_product": product,
            "persona": persona, "severity": SEVERITY_CYCLE[num % len(SEVERITY_CYCLE)],
            "status": "Active", "created_at": _ts(day, 10), "updated_at": _ts(day, 10),
            "resource_ids": [rid],
        },
        "resources": [{
            "resource_id": rid, "resource_type": resource_type, "name": name,
            "resource_group": rg, "subscription_id": sub,
            "location": LOCATIONS[num % len(LOCATIONS)], "instances": instances,
        }],
        "telemetry": telemetry,
        "root_cause": {"category": category, "summary": summary, "resolution": resolution},
        "investigation_path": path,
    }


def _specs():
    for entry in CURATED:
        yield (*entry, False)  # curated 4-20 are single-round
    for num in range(21, 104):
        persona = "windows_admin" if num % 2 else "azure_developer"
        category = CATEGORIES[num % 4]
        rtype = "vmss" if num % 6 == 0 else "vm"
        text = CAT_TEXT[category]
        name = f"{CAT_PREFIX[category]}-{num:02d}"
        rg = f"rg-{'ops' if persona == 'windows_admin' else 'dev'}-{num % 5}"
        product = "Azure Virtual Machine Scale Sets" if rtype == "vmss" else text["product"]
        multi = _is_multi_round(num)
        yield (
            num, persona, product, rtype, category, name, rg,
            text["title"].format(name=name), text["symptom"].format(name=name),
            text["summary"], text["resolution"], multi,
        )


def main() -> None:
    import sys

    count = 0
    for spec in _specs():
        scenario = build_scenario(*spec)
        path = FIXTURES / f"{scenario['scenario_id']}.yaml"
        path.write_text(yaml.safe_dump(scenario, sort_keys=False, width=100))
        count += 1
    print(f"Wrote {count} generated scenario fixtures to {FIXTURES}", file=sys.stderr)


if __name__ == "__main__":
    main()
