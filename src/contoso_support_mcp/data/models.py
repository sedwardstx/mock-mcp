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
KNOWN_ISSUE_ID_RE = re.compile(r"^KB-[A-Z]+-\d{3}$")

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


class ArmTraceRow(BaseModel):
    """A row in the mock ArmControlPlaneTraces table (Azure Activity Log style)."""

    model_config = _STRICT

    time_generated: datetime
    resource_id: str
    subscription_id: str = ""
    resource_group: str = ""
    correlation_id: str = ""
    operation_name: str = ""
    caller: str = ""
    client_ip: str = ""
    http_status_code: int = 0
    level: str = "Informational"
    activity_status: str = ""
    sub_status: str = ""
    properties: str = ""


class NetworkLogRow(BaseModel):
    """A row in the mock NetworkLogs table (NSG flow log style)."""

    model_config = _STRICT

    time_generated: datetime
    resource_id: str
    subscription_id: str = ""
    flow_direction: str = ""
    source_ip: str = ""
    destination_ip: str = ""
    source_port: int = 0
    destination_port: int = 0
    protocol: str = ""
    action: str = ""
    nsg_rule_name: str = ""
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0


class ComputeHostLogRow(BaseModel):
    """A row in the mock ComputeHostLogs table (platform/host events, VM & VMSS)."""

    model_config = _STRICT

    time_generated: datetime
    resource_id: str
    subscription_id: str = ""
    instance_id: str = ""  # VMSS instance; empty for a plain VM
    host_node: str = ""
    event_name: str = ""
    health_status: str = ""
    maintenance_type: str = "None"
    level: str = "Informational"
    message: str = ""


class ComputeGuestLogRow(BaseModel):
    """A row in the mock ComputeGuestLogs table (in-guest Windows events, VM & VMSS)."""

    model_config = _STRICT

    time_generated: datetime
    resource_id: str
    subscription_id: str = ""
    instance_id: str = ""  # VMSS instance; empty for a plain VM
    computer: str = ""
    channel: str = "System"
    provider_name: str = ""
    event_id: int = 0
    level: str = "Information"
    task: str = ""
    message: str = ""


class Telemetry(BaseModel):
    """Correlated Kusto-style telemetry across the four mock tables. Rows are
    typed (Story 3.1); all lists default empty so `telemetry: {}` stays valid."""

    model_config = _STRICT

    arm_control_plane_traces: list[ArmTraceRow] = Field(default_factory=list)
    network_logs: list[NetworkLogRow] = Field(default_factory=list)
    compute_host_logs: list[ComputeHostLogRow] = Field(default_factory=list)
    compute_guest_logs: list[ComputeGuestLogRow] = Field(default_factory=list)


class Scenario(BaseModel):
    model_config = _STRICT

    scenario_id: str
    difficulty: Difficulty
    ticket: Ticket
    resources: list[AzureResource]
    telemetry: Telemetry = Field(default_factory=Telemetry)
    root_cause: RootCause
    investigation_path: list[InvestigationStep] = Field(default_factory=list)


class KnownIssue(BaseModel):
    """A generic Azure known-issue entry backing the read-only KB tool.

    Deliberately decoupled from `Scenario.root_cause` — this is general remediation
    guidance keyed by product/category/keyword, NOT a per-ticket answer, so it can
    never leak the grading key (docs/scenario-index.md).
    """

    model_config = _STRICT

    id: str
    title: str
    product: str
    category: RootCauseCategory
    symptom: str
    remediation: str
    doc_link: str | None = None

    @field_validator("id")
    @classmethod
    def _valid_kb_id(cls, v: str) -> str:
        if not KNOWN_ISSUE_ID_RE.match(v):
            raise ValueError(f"KB id must match KB-<DOMAIN>-### (e.g. KB-ARM-001), got {v!r}")
        return v
