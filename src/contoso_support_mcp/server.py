"""Builds the FastMCP application and registers the tool/prompt surface."""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from . import SERVER_NAME
from .tools.health import register_health_tools

logger = logging.getLogger(__name__)


def build_server(host: str | None = None, port: int | None = None) -> FastMCP:
    """Construct the FastMCP server with all tools/prompts registered.

    host/port apply only to the network (streamable HTTP) transport; they are
    ignored by stdio. The tool/prompt surface is identical regardless of transport.
    """
    mcp = FastMCP(SERVER_NAME)
    if host is not None:
        mcp.settings.host = host
    if port is not None:
        mcp.settings.port = port
    register_health_tools(mcp)
    logger.info("Registered tool surface for %s", SERVER_NAME)
    return mcp
