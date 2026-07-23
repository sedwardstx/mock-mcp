"""Health / identity tool so a client can confirm a successful connection."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .. import SERVER_NAME, __version__


class ServerInfo(BaseModel):
    """Identity and health of the server."""

    name: str = Field(description="Server display name")
    version: str = Field(description="Server semantic version")
    status: str = Field(description="Static health status; 'ok' when serving")


def server_info() -> ServerInfo:
    """Pure function returning the server identity (unit-testable)."""
    return ServerInfo(name=SERVER_NAME, version=__version__, status="ok")


def register_health_tools(mcp) -> None:
    """Register health tools on the given FastMCP instance."""

    @mcp.tool(
        description=(
            "Return this MCP server's identity and health status. "
            "Call first to confirm your agent is connected to the Contoso Support server."
        )
    )
    def get_server_info() -> ServerInfo:
        return server_info()
