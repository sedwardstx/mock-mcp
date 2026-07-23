"""Shared fixtures for network-transport integration tests."""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator

import pytest
import uvicorn

from contoso_support_mcp.server import build_server


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


@pytest.fixture
def http_server() -> Iterator[str]:
    """Start the streamable-HTTP server on an ephemeral localhost port.

    Yields the MCP endpoint URL and cleanly shuts the server down afterwards.
    """
    port = _free_port()
    mcp = build_server(host="127.0.0.1", port=port)
    app = mcp.streamable_http_app()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait until uvicorn reports started (mitigates startup race).
    for _ in range(200):
        if server.started:
            break
        time.sleep(0.02)
    else:  # pragma: no cover - only on startup failure
        raise RuntimeError("HTTP server did not start in time")

    try:
        yield f"http://127.0.0.1:{port}/mcp"
    finally:
        server.should_exit = True
        thread.join(timeout=5)
