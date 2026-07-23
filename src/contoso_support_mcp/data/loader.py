"""Deterministic fixture loader.

Discovers scenario YAML files, validates them into `Scenario` models, enforces
unique ticket ids, and returns an immutable, deterministically-ordered dataset.
Fails fast with a clear error naming the offending file/field.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from .models import KnownIssue, Scenario


class FixtureValidationError(Exception):
    """Raised when a fixture file is malformed or violates dataset invariants."""


class Dataset:
    """Immutable, in-memory collection of loaded scenarios with lookup indices."""

    def __init__(self, scenarios: list[Scenario]) -> None:
        # Deterministic order: sort by scenario_id.
        self._scenarios: list[Scenario] = sorted(scenarios, key=lambda s: s.scenario_id)
        self._by_ticket: dict[str, Scenario] = {
            s.ticket.ticket_id: s for s in self._scenarios
        }

    @property
    def scenarios(self) -> list[Scenario]:
        return list(self._scenarios)

    def get_by_ticket(self, ticket_id: str) -> Scenario | None:
        return self._by_ticket.get(ticket_id)

    def __len__(self) -> int:
        return len(self._scenarios)


def load_scenarios(path: Path) -> Dataset:
    """Load and validate all `*.yaml` scenario fixtures under `path`.

    Deterministic: files are read in sorted order and the dataset is sorted by
    scenario_id. Raises FixtureValidationError on any malformed fixture or a
    duplicate ticket id.
    """
    scenarios: list[Scenario] = []
    seen_ticket_ids: dict[str, str] = {}

    for file in sorted(path.glob("*.yaml")):
        try:
            raw = yaml.safe_load(file.read_text())
        except yaml.YAMLError as exc:
            raise FixtureValidationError(f"Invalid YAML in fixture {file.name}: {exc}") from exc

        try:
            scenario = Scenario.model_validate(raw)
        except ValidationError as exc:
            raise FixtureValidationError(
                f"Invalid scenario in fixture {file.name}: {exc}"
            ) from exc

        ticket_id = scenario.ticket.ticket_id
        if ticket_id in seen_ticket_ids:
            raise FixtureValidationError(
                f"Duplicate ticket id {ticket_id} in {file.name} "
                f"(already defined in {seen_ticket_ids[ticket_id]})"
            )
        seen_ticket_ids[ticket_id] = file.name
        scenarios.append(scenario)

    return Dataset(scenarios)


def load_known_issues(path: Path) -> list[KnownIssue]:
    """Load and validate the curated known-issues KB file.

    Deterministic: returns entries sorted by id. Fails fast (FixtureValidationError)
    on malformed YAML/schema or a duplicate id.
    """
    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise FixtureValidationError(f"Invalid YAML in KB file {path.name}: {exc}") from exc

    entries = (raw or {}).get("known_issues", [])
    issues: list[KnownIssue] = []
    seen_ids: set[str] = set()
    for entry in entries:
        try:
            issue = KnownIssue.model_validate(entry)
        except ValidationError as exc:
            raise FixtureValidationError(
                f"Invalid known-issue entry in {path.name}: {exc}"
            ) from exc
        if issue.id in seen_ids:
            raise FixtureValidationError(f"Duplicate known-issue id {issue.id} in {path.name}")
        seen_ids.add(issue.id)
        issues.append(issue)

    return sorted(issues, key=lambda k: k.id)
