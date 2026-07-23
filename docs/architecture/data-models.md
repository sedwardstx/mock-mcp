# Data Models

The domain centers on a **Scenario** aggregate: a self-contained unit linking a ticket, its Azure resources, correlated telemetry, and the ground-truth root cause. One scenario = one authored YAML file.

## Scenario

**Purpose:** The top-level aggregate binding a support incident to its resources, telemetry evidence, and ground-truth root cause + investigation path. Enables end-to-end RCA and grading.

**Key Attributes:**
- scenario_id: str — Stable id (mirrors the ticket id, e.g., `TICKET-10000001`)
- difficulty: enum(`single_round`, `multi_round`) — Investigation depth classification
- root_cause: RootCause — Ground-truth cause + resolution/next-step
- investigation_path: list[InvestigationStep] — Intended query sequence (for multi-round scenarios; supports grading)

**Relationships:**
- Has one Ticket
- Has one or more AzureResource
- Has many TelemetryRecord (across the four tables), each tied to a resource

## Ticket

**Purpose:** The customer-reported incident an agent starts from.

**Key Attributes:**
- ticket_id: str — Format `TICKET-XXXXXXXX` (8 digits), unique
- title: str — Short summary
- symptom: str — Customer-reported problem statement
- azure_product: str — e.g., "Azure Virtual Machines", "Azure Virtual Machine Scale Sets", "Azure Networking"
- persona: enum(`windows_admin`, `azure_developer`) — Reporter type
- severity: enum(`Sev1`, `Sev2`, `Sev3`, `Sev4`)
- status: enum(`New`, `Active`, `Pending`, `Resolved`) — Read-only in MVP
- created_at / updated_at: datetime (ISO 8601)
- resource_ids: list[str] — References to affected resources

**Relationships:**
- Belongs to one Scenario
- References one or more AzureResource

## AzureResource

**Purpose:** The Azure resource whose telemetry the agent investigates; the pivot target from a ticket.

**Key Attributes:**
- resource_id: str — ARM resource id (`/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{name}`)
- resource_type: enum(`Microsoft.Compute/virtualMachines`, `Microsoft.Compute/virtualMachineScaleSets`, ...)
- name / resource_group / subscription_id: str
- location: str — e.g., "eastus"
- instances: list[str] — VMSS instance ids (empty for a plain VM)

**Relationships:**
- Belongs to one Scenario
- Referenced by a Ticket
- Has many TelemetryRecord

## TelemetryRecord (base) → ARM / Network / ComputeHost / ComputeGuest

**Purpose:** A single row in one of the mock Kusto tables, correlated to a resource (and, where relevant, a VMSS instance) and carrying the evidence for the scenario's root cause (plus realistic noise).

**Key Attributes (common):**
- table: enum(`ArmControlPlaneTraces`, `NetworkLogs`, `ComputeHostLogs`, `ComputeGuestLogs`)
- time_generated: datetime — Row timestamp (drives time-range scoping)
- resource_id: str — Owning resource
- (table-specific columns — see Database Schema)

**Relationships:**
- Belongs to one Scenario and one AzureResource

## RootCause & InvestigationStep

**Purpose:** Ground truth for grading. RootCause holds the cause category, explanation, and resolution/next-step. InvestigationStep documents which tool call + filters reveal which evidence, forming the intended path for multi-round scenarios.

**Key Attributes:**
- RootCause: category: enum(`arm`, `network`, `compute_host`, `compute_guest`), summary: str, resolution: str
- InvestigationStep: order: int, tool: str, params: dict, reveals: str
