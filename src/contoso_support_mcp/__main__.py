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
        choices=["stdio", "http"],
        default="stdio",
        help="MCP transport: 'stdio' (offline student mode) or 'http' (instructor-hosted).",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host for http transport (default: 127.0.0.1; use 0.0.0.0 to serve a LAN).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port for http transport (default: 8000).",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    _configure_logging()
    log = logging.getLogger(__name__)
    if args.transport == "stdio":
        log.info("Starting %s v%s over stdio", SERVER_NAME, __version__)
        mcp = build_server()
        mcp.run(transport="stdio")
    else:
        log.info(
            "Starting %s v%s over http at %s:%s", SERVER_NAME, __version__, args.host, args.port
        )
        mcp = build_server(host=args.host, port=args.port)
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
