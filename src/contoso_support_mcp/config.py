"""Runtime configuration for the Contoso Support MCP server."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

DEFAULT_FIXTURES_PATH = Path(__file__).parent / "fixtures" / "scenarios"


class Settings(BaseModel):
    """Server settings. Transport selection expands in later stories."""

    transport: str = Field(default="stdio", description="MCP transport: 'stdio' (offline).")
    fixtures_path: Path = Field(
        default=DEFAULT_FIXTURES_PATH,
        description="Directory containing scenario fixture files.",
    )
