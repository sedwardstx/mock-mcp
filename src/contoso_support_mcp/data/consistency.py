"""Whole-library consistency checks over a loaded Dataset.

Returns a list of human-readable issue strings (empty list == consistent).
Epic 3 extends this with telemetry-evidence-vs-root-cause checks.
"""

from __future__ import annotations

from .loader import Dataset


def check_dataset(dataset: Dataset) -> list[str]:
    issues: list[str] = []
    for scenario in dataset.scenarios:
        sid = scenario.scenario_id
        ticket = scenario.ticket

        if sid != ticket.ticket_id:
            issues.append(f"{sid}: scenario_id does not match ticket_id ({ticket.ticket_id})")

        resource_ids = {r.resource_id for r in scenario.resources}
        for rid in ticket.resource_ids:
            if rid not in resource_ids:
                issues.append(
                    f"{sid}: ticket references resource_id not present in resources[]: {rid}"
                )

        if not scenario.root_cause.summary.strip():
            issues.append(f"{sid}: empty root_cause.summary")
        if not scenario.root_cause.resolution.strip():
            issues.append(f"{sid}: empty root_cause.resolution")

    return issues
