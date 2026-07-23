"""Pydantic data models for the mock support-ticketing domain.

A Scenario is the top-level aggregate: one authored fixture linking a ticket,
its Azure resources, correlated telemetry (populated in Epic 3), and the
ground-truth root cause + intended investigation path.
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

TICKET_ID_RE = re.compile(r"^TICKET-\d{8}$")

_STRICT = ConfigDict(extra="forbid")


class Persona(StrEnum):
    windows_admin = "windows_admin"
    azure_developer = "azure_developer"


class Severity(StrEnum):
    sev1 = "Sev1"
    sev2 = "Sev2"
    sev3 = "Sev3"
    sev4 = "Sev4"


class Status(StrEnum):
    new = "New"
    active = "Active"
    pending = "Pending"
    resolved = "Resolved"


class RootCauseCategory(StrEnum):
    arm = "arm"
    network = "network"
    compute_host = "compute_host"
    compute_guest = "compute_guest"


class Difficulty(StrEnum):
    single_round = "single_round"
    multi_round = "multi_round"


class Ticket(BaseModel):
    model_config = _STRICT

    ticket_id: str
    title: str
    symptom: str
    azure_product: str
    persona: Persona
    severity: Severity
    status: Status
    created_at: datetime
    updated_at: datetime
    resource_ids: list[str] = Field(default_factory=list)

    @field_validator("ticket_id")
    @classmethod
    def _valid_ticket_id(cls, v: str) -> str:
        if not TICKET_ID_RE.match(v):
            raise ValueError(f"ticket_id must match TICKET-XXXXXXXX (8 digits), got {v!r}")
        return v


class AzureResource(BaseModel):
    model_config = _STRICT

    resource_id: str
    resource_type: str
    name: str
    resource_group: str
    subscription_id: str
    location: str
    instances: list[str] = Field(default_factory=list)  # VMSS instance ids; empty for a VM


class RootCause(BaseModel):
    model_config = _STRICT

    category: RootCauseCategory
    summary: str
    resolution: str


class InvestigationStep(BaseModel):
    model_config = _STRICT

    order: int
    tool: str
    params: dict = Field(default_factory=dict)
    reveals: str


class Telemetry(BaseModel):
    """Correlated Kusto-style telemetry. Rows stay free-form dicts until Epic 3
    introduces typed row models; the container exists now so scenarios are
    forward-compatible without a schema change."""

    model_config = _STRICT

    arm_control_plane_traces: list[dict] = Field(default_factory=list)
    network_logs: list[dict] = Field(default_factory=list)
    compute_host_logs: list[dict] = Field(default_factory=list)
    compute_guest_logs: list[dict] = Field(default_factory=list)


class Scenario(BaseModel):
    model_config = _STRICT

    scenario_id: str
    difficulty: Difficulty
    ticket: Ticket
    resources: list[AzureResource]
    telemetry: Telemetry = Field(default_factory=Telemetry)
    root_cause: RootCause
    investigation_path: list[InvestigationStep] = Field(default_factory=list)
