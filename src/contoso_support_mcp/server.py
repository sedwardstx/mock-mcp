"""Builds the FastMCP application and registers the tool/prompt surface."""

from __future__ import annotations

import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import SERVER_NAME
from .config import DEFAULT_FIXTURES_PATH
from .data.loader import load_scenarios
from .data.repository import Repository
from .tools.health import register_health_tools
from .tools.resources import register_resource_tools
from .tools.tickets import register_ticket_tools

logger = logging.getLogger(__name__)


def build_server(
    host: str | None = None,
    port: int | None = None,
    fixtures_path: Path | None = None,
) -> FastMCP:
    """Construct the FastMCP server with all tools/prompts registered.

    Loads the scenario dataset once at startup (fail-fast on malformed fixtures).
    host/port apply only to the network transport; the tool surface is identical
    across transports.
    """
    mcp = FastMCP(SERVER_NAME)
    if host is not None:
        mcp.settings.host = host
    if port is not None:
        mcp.settings.port = port

    dataset = load_scenarios(fixtures_path or DEFAULT_FIXTURES_PATH)
    repo = Repository(dataset)

    register_health_tools(mcp)
    register_ticket_tools(mcp, repo)
    register_resource_tools(mcp, repo)

    logger.info("Registered tool surface for %s (%d scenarios)", SERVER_NAME, len(dataset))
    return mcp
