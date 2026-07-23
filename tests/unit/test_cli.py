"""Unit tests for CLI argument parsing (1.2-UNIT-001, 1.3-UNIT-001..003)."""

import pytest

from contoso_support_mcp.__main__ import build_arg_parser


def test_cli_defaults_to_stdio():
    args = build_arg_parser().parse_args([])
    assert args.transport == "stdio"
    assert args.host == "127.0.0.1"
    assert args.port == 8000


def test_cli_http_with_host_and_port():
    args = build_arg_parser().parse_args(
        ["--transport", "http", "--host", "0.0.0.0", "--port", "9001"]
    )
    assert args.transport == "http"
    assert args.host == "0.0.0.0"
    assert args.port == 9001


@pytest.mark.parametrize("bad_port", ["0", "70000", "-1", "abc"])
def test_cli_rejects_invalid_port(bad_port):
    """1.3-UNIT-002: invalid port exits cleanly (code 2), no traceback."""
    with pytest.raises(SystemExit) as exc:
        build_arg_parser().parse_args(["--port", bad_port])
    assert exc.value.code == 2


def test_cli_rejects_invalid_transport():
    """1.3-UNIT-003: invalid transport exits cleanly (code 2)."""
    with pytest.raises(SystemExit) as exc:
        build_arg_parser().parse_args(["--transport", "carrier-pigeon"])
    assert exc.value.code == 2
