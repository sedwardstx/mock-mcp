"""MCP tool: read-only Azure known-issues knowledge base.

Generic remediation guidance (NOT per-ticket RCA). Backed by a curated dataset
decoupled from scenario root causes, so it never reveals the grading answer.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ..data.models import RootCauseCategory
from ..data.repository import Repository


class KnownIssueMatch(BaseModel):
    id: str
    title: str
    product: str
    category: str
    symptom: str
    remediation: str
    doc_link: str | None = None


class KnownIssueSearchResult(BaseModel):
    status: str = Field(description="'ok' | 'invalid_request'")
    total: int
    matches: list[KnownIssueMatch]
    message: str | None = Field(default=None, description="Explanation for non-ok status")


def register_kb_tools(mcp: FastMCP, repo: Repository) -> None:
    @mcp.tool(
        description=(
            "Search the read-only Azure known-issues knowledge base of GENERIC product "
            "issues and remediations. All params optional (AND semantics): query "
            "(keyword matched against title/symptom/remediation), product (exact, e.g. "
            "'Azure Virtual Machines'), category (one of "
            "['arm','network','compute_host','compute_guest']). Returns matching entries "
            "with remediation and an optional doc_link. No matches returns status 'ok' "
            "with an empty list; an invalid category returns 'invalid_request'. This is "
            "general guidance, not a ticket-specific root-cause analysis."
        )
    )
    def search_known_issues(
        query: str | None = None,
        product: str | None = None,
        category: str | None = None,
    ) -> KnownIssueSearchResult:
        allowed = [c.value for c in RootCauseCategory]
        if category is not None and category not in allowed:
            return KnownIssueSearchResult(
                status="invalid_request",
                total=0,
                matches=[],
                message=f"category must be one of {allowed}; got {category!r}",
            )
        found = repo.search_known_issues(query=query, product=product, category=category)
        matches = [KnownIssueMatch(**k.model_dump()) for k in found]
        return KnownIssueSearchResult(status="ok", total=len(matches), matches=matches)
