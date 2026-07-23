"""CLI entry point. Selects a transport and runs the server.

IMPORTANT: All human-readable output goes to stderr via logging. stdout is
reserved for the MCP stdio transport channel and must never be written to.
"""

from __future__ import annotations

import argparse
import logging
import sys

from . import SERVER_NAME, __version__
from .server import build_server


def _configure_logging() -> None:
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="contoso-support-mcp",
        description="Mock Contoso Support Ticketing MCP server for classroom labs.",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="MCP transport to serve on (default: stdio).",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    _configure_logging()
    logging.getLogger(__name__).info(
        "Starting %s v%s over %s transport", SERVER_NAME, __version__, args.transport
    )
    mcp = build_server()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
