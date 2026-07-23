"""Unit tests for CLI argument parsing (1.2-UNIT-001)."""

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
