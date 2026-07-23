"""Builds the FastMCP application and registers the tool/prompt surface."""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from . import SERVER_NAME
from .tools.health import register_health_tools

logger = logging.getLogger(__name__)


def build_server() -> FastMCP:
    """Construct the FastMCP server with all tools/prompts registered."""
    mcp = FastMCP(SERVER_NAME)
    register_health_tools(mcp)
    logger.info("Registered tool surface for %s", SERVER_NAME)
    return mcp
