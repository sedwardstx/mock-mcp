"""Authoring aid: emit the curated seed-batch scenario fixtures (Story 2.5).

Each entry below is hand-curated content (distinct symptom + root cause);
this script only serializes it deterministically to YAML. The committed YAML
files under fixtures/scenarios/ are the source of truth. Telemetry is left empty
here and backfilled in Epic 3.

Run:  uv run python scripts/author_seed_scenarios.py
"""

from __future__ import annotations

from pathlib import Path

import yaml

FIXTURES = Path(__file__).resolve().parents[1] / "src" / "contoso_support_mcp" / "fixtures" / "scenarios"

SUB = {
    "windows_admin": "00000000-0000-0000-0000-000000000001",
    "azure_developer": "00000000-0000-0000-0000-000000000002",
}
LOCATIONS = ["eastus", "westus2", "westeurope", "centralus"]
TOOL = {
    "arm": "query_arm_traces",
    "network": "query_network_logs",
    "compute_host": "query_compute_host_logs",
    "compute_guest": "query_compute_guest_logs",
}
REVEALS = {
    "arm": "Control-plane operation failed with an error status in the ARM traces.",
    "network": "Traffic matching the reported flow shows Action=Deny in the network logs.",
    "compute_host": "A platform host event affecting the resource appears in the host logs.",
    "compute_guest": "A relevant Windows event appears in the in-guest logs.",
}

# (num, persona, product, rtype, category, name, rg, title, symptom, summary, resolution)
CURATED = [
    (4, "windows_admin", "Azure Virtual Machines", "vm", "compute_host", "app-vm-01", "rg-prod",
     "VM rebooted unexpectedly overnight",
     "Customer reports VM 'app-vm-01' rebooted on its own around 02:00 with no user action; the app was briefly offline.",
     "The Azure platform performed a host reboot on the node hosting the VM (platform-initiated).",
     "Confirm the platform reboot in host logs; enable availability zones / an availability set for resilience to host events."),
    (5, "azure_developer", "Azure Virtual Machine Scale Sets", "vmss", "arm", "web-vmss", "rg-web",
     "Scale-out fails to add instances",
     "Developer reports 'web-vmss' will not scale out past its current instance count; new instances never appear.",
     "The scale operation fails with an allocation/quota error for the requested SKU in the region.",
     "Request a quota increase or choose an available SKU/region; retry the scale operation."),
    (6, "windows_admin", "Azure Virtual Machines", "vm", "network", "jump-vm-01", "rg-ops",
     "Cannot RDP to VM",
     "Admin cannot connect via RDP (3389) to 'jump-vm-01'; the connection times out from the corporate network.",
     "An NSG rule denies inbound TCP 3389 from the admin's source range.",
     "Add/adjust an NSG rule to allow inbound 3389 from the trusted admin source; verify rule priority."),
    (7, "azure_developer", "Azure Virtual Machines", "vm", "compute_guest", "batch-vm-02", "rg-batch",
     "Application crashes with out-of-memory",
     "Developer reports their batch app on 'batch-vm-02' crashes intermittently; suspects memory pressure.",
     "The in-guest application is terminated under memory pressure (guest OOM), not an Azure platform fault.",
     "Right-size the VM SKU or fix the app's memory usage; the host is healthy."),
    (8, "windows_admin", "Azure Virtual Machine Scale Sets", "vmss", "compute_host", "data-vmss", "rg-data",
     "Some scale set instances are unhealthy",
     "Admin reports two instances of 'data-vmss' show as unhealthy while others are fine.",
     "A platform host degradation affected specific nodes hosting those instances.",
     "Reimage/redeploy the affected instances; the scale set spreads across healthy nodes."),
    (9, "azure_developer", "Azure Networking", "vm", "network", "lb-app-vm-01", "rg-net",
     "Intermittent 503s behind the load balancer",
     "Developer reports intermittent HTTP 503 responses from a load-balanced app on 'lb-app-vm-01'.",
     "An NSG rule intermittently blocks the load balancer health-probe port, marking the backend unhealthy.",
     "Allow the load balancer probe port in the NSG (AzureLoadBalancer service tag)."),
    (10, "windows_admin", "Azure Virtual Machines", "vm", "arm", "sql-vm-03", "rg-data",
     "VM resize operation keeps failing",
     "Admin cannot resize 'sql-vm-03'; the operation returns a failure each time.",
     "The resize control-plane operation fails due to a conflicting operation / SKU not available on the current host cluster.",
     "Stop (deallocate) the VM before resizing, or choose a SKU available in the region; retry."),
    (11, "azure_developer", "Azure Virtual Machines", "vm", "compute_guest", "ci-vm-04", "rg-ci",
     "Service won't start — disk full",
     "Developer reports a service on 'ci-vm-04' fails to start after a build filled the disk.",
     "The in-guest service fails because the OS/data disk is full (guest disk-space event).",
     "Free space or expand the disk in-guest; not an Azure platform issue."),
    (12, "windows_admin", "Azure Virtual Machines", "vm", "compute_host", "erp-vm-01", "rg-erp",
     "VM briefly unresponsive during the day",
     "Admin reports 'erp-vm-01' froze for about a minute mid-afternoon, then recovered.",
     "A platform live-migration paused the VM briefly while moving it off a degraded host.",
     "Expected platform behavior; use availability zones and app-level retry for resilience."),
    (13, "azure_developer", "Azure Virtual Machine Scale Sets", "vmss", "network", "api-vmss-2", "rg-api2",
     "Backend pool members failing health probe",
     "Developer reports 'api-vmss-2' members fail the load balancer health probe after a network change.",
     "A new NSG deny rule blocks the health-probe port to the instances.",
     "Allow the probe port from the AzureLoadBalancer tag in the NSG."),
    (14, "windows_admin", "Azure Virtual Machines", "vm", "arm", "policy-vm-01", "rg-gov",
     "Deployment update denied by policy",
     "Admin's update to 'policy-vm-01' is rejected immediately with an authorization/deny error.",
     "An Azure Policy assignment denies the requested change (control-plane deny).",
     "Adjust the resource to comply with policy, or update the policy assignment/exemption."),
    (15, "azure_developer", "Azure Virtual Machines", "vm", "compute_guest", "win-app-05", "rg-app",
     "Windows Update reboot loop",
     "Developer reports 'win-app-05' repeatedly restarts after installing updates.",
     "An in-guest Windows Update triggered recurring restarts (guest event 1074/restart).",
     "Roll back the problematic update or pause updates in-guest; the platform is healthy."),
    (16, "windows_admin", "Azure Virtual Machine Scale Sets", "vmss", "arm", "img-vmss", "rg-img",
     "Scale set create fails — image not found",
     "Admin's new scale set 'img-vmss' fails to create referencing a custom image.",
     "The control-plane operation returns a 404 for the referenced image (bad/missing image reference).",
     "Correct the image reference (id/version) and recreate the scale set."),
    (17, "azure_developer", "Azure Networking", "vm", "network", "dns-vm-01", "rg-net2",
     "DNS resolution failing from VM",
     "Developer reports 'dns-vm-01' cannot resolve external hostnames since a recent change.",
     "An NSG rule blocks outbound DNS (UDP/TCP 53) from the VM.",
     "Allow outbound 53 to the DNS resolver in the NSG."),
    (18, "windows_admin", "Azure Virtual Machines", "vm", "compute_host", "fin-vm-02", "rg-fin",
     "Planned maintenance caused unexpected downtime",
     "Admin reports 'fin-vm-02' went down during a maintenance window they didn't expect.",
     "A planned platform maintenance event caused a reboot of the host.",
     "Review scheduled events; use maintenance configurations / availability zones to control impact."),
    (19, "azure_developer", "Azure Virtual Machines", "vm", "compute_guest", "svc-vm-06", "rg-svc",
     "App pool crashing with .NET exception",
     "Developer reports the app pool on 'svc-vm-06' recycles repeatedly due to an unhandled exception.",
     "An in-guest application fault crashes the worker process (guest application event).",
     "Fix the application exception; the Azure host shows no fault."),
    (20, "windows_admin", "Azure Virtual Machines", "vm", "network", "egress-vm-01", "rg-edge",
     "Outbound HTTPS blocked from VM",
     "Admin reports 'egress-vm-01' can no longer reach external HTTPS endpoints after a network change.",
     "An NSG rule denies outbound TCP 443 from the VM.",
     "Allow the required outbound 443 destinations in the NSG."),
]

SEVERITY_CYCLE = ["Sev2", "Sev3", "Sev2", "Sev3", "Sev4"]


def _resource_id(sub: str, rg: str, rtype: str, name: str) -> str:
    kind = "virtualMachineScaleSets" if rtype == "vmss" else "virtualMachines"
    return (
        f"/subscriptions/{sub}/resourceGroups/{rg}"
        f"/providers/Microsoft.Compute/{kind}/{name}"
    )


def build(entry) -> dict:
    (num, persona, product, rtype, category, name, rg, title, symptom, summary, resolution) = entry
    tid = f"TICKET-{10000000 + num:08d}"
    sub = SUB[persona]
    location = LOCATIONS[num % len(LOCATIONS)]
    rid = _resource_id(sub, rg, rtype, name)
    resource_type = (
        "Microsoft.Compute/virtualMachineScaleSets"
        if rtype == "vmss"
        else "Microsoft.Compute/virtualMachines"
    )
    instances = [f"{name}_0", f"{name}_1"] if rtype == "vmss" else []
    day = (num % 27) + 1
    ts = f"2026-05-{day:02d}T10:00:00Z"
    return {
        "scenario_id": tid,
        "difficulty": "single_round",
        "ticket": {
            "ticket_id": tid,
            "title": title,
            "symptom": symptom,
            "azure_product": product,
            "persona": persona,
            "severity": SEVERITY_CYCLE[num % len(SEVERITY_CYCLE)],
            "status": "Active",
            "created_at": ts,
            "updated_at": ts,
            "resource_ids": [rid],
        },
        "resources": [
            {
                "resource_id": rid,
                "resource_type": resource_type,
                "name": name,
                "resource_group": rg,
                "subscription_id": sub,
                "location": location,
                "instances": instances,
            }
        ],
        "telemetry": {},
        "root_cause": {"category": category, "summary": summary, "resolution": resolution},
        "investigation_path": [
            {
                "order": 1,
                "tool": TOOL[category],
                "params": {"time_range": f"2026-05-{day:02d}T09:00:00Z/2026-05-{day:02d}T11:00:00Z"},
                "reveals": REVEALS[category],
            }
        ],
    }


def main() -> None:
    count = 0
    for entry in CURATED:
        scenario = build(entry)
        path = FIXTURES / f"{scenario['scenario_id']}.yaml"
        path.write_text(yaml.safe_dump(scenario, sort_keys=False, width=100))
        count += 1
    # Note: intentionally not using print() elsewhere in src/, but this is a script.
    import sys

    print(f"Wrote {count} scenario fixtures to {FIXTURES}", file=sys.stderr)


if __name__ == "__main__":
    main()
