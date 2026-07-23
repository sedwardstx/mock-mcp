"""Whole-library consistency checks over a loaded Dataset.

Returns a list of human-readable issue strings (empty list == consistent).
Epic 3 extends this with telemetry-evidence-vs-root-cause checks.
"""

from __future__ import annotations

from .loader import Dataset
from .models import Scenario, Telemetry


def _has_root_cause_evidence(category: str, telemetry: Telemetry) -> bool:
    """True if the telemetry contains a row that supports the given root cause."""
    if category == "arm":
        return any(
            r.activity_status == "Failed" or r.http_status_code >= 400
            for r in telemetry.arm_control_plane_traces
        )
    if category == "network":
        return any(r.action == "Deny" for r in telemetry.network_logs)
    if category == "compute_host":
        return any(
            r.health_status in {"Degraded", "Unavailable"} or r.level == "Error"
            for r in telemetry.compute_host_logs
        )
    if category == "compute_guest":
        return any(r.level in {"Error", "Warning"} for r in telemetry.compute_guest_logs)
    return False


def _scenario_issues(scenario: Scenario) -> list[str]:
    sid = scenario.scenario_id
    ticket = scenario.ticket
    issues: list[str] = []

    if sid != ticket.ticket_id:
        issues.append(f"{sid}: scenario_id does not match ticket_id ({ticket.ticket_id})")

    resource_ids = {r.resource_id for r in scenario.resources}
    for rid in ticket.resource_ids:
        if rid not in resource_ids:
            issues.append(f"{sid}: ticket references resource_id not present in resources[]: {rid}")

    if not scenario.root_cause.summary.strip():
        issues.append(f"{sid}: empty root_cause.summary")
    if not scenario.root_cause.resolution.strip():
        issues.append(f"{sid}: empty root_cause.resolution")

    # Telemetry must contain evidence supporting the declared root cause.
    category = str(scenario.root_cause.category)
    if not _has_root_cause_evidence(category, scenario.telemetry):
        issues.append(
            f"{sid}: telemetry has no evidence supporting root_cause category '{category}'"
        )

    # Multi-round scenarios must document a >=2-step investigation path.
    if str(scenario.difficulty) == "multi_round" and len(scenario.investigation_path) < 2:
        issues.append(f"{sid}: multi_round scenario must have a >=2-step investigation_path")

    return issues


def check_dataset(dataset: Dataset) -> list[str]:
    issues: list[str] = []
    for scenario in dataset.scenarios:
        issues.extend(_scenario_issues(scenario))
    return issues
