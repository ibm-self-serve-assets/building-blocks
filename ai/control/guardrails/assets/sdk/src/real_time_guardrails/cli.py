from __future__ import annotations

import argparse
import os
import sys

from real_time_guardrails._version import __version__
from real_time_guardrails.core.config import REQUIRED_ENV_VARS
from real_time_guardrails.core.exceptions import ConfigError


def _check_credentials() -> None:
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        raise ConfigError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ". Set them before starting the server."
        )


def _serve(args: argparse.Namespace) -> int:
    _check_credentials()
    from real_time_guardrails.rest.server import create_app

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


def _mcp(_: argparse.Namespace) -> int:
    _check_credentials()
    from real_time_guardrails.mcp.server import serve as mcp_serve

    mcp_serve()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="real-time-guardrails",
        description="Real-time AI guardrails over IBM watsonx.governance.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="{serve,mcp}")

    p_serve = sub.add_parser("serve", help="Start the REST API (Flask).")
    p_serve.add_argument(
        "--host", default=os.environ.get("SERVICE_HOST", "0.0.0.0"), help="Bind host (default: 0.0.0.0)"
    )
    p_serve.add_argument(
        "--port", type=int, default=int(os.environ.get("SERVICE_PORT", "8090")),
        help="Bind port (default: 8090)",
    )
    p_serve.add_argument(
        "--debug", action="store_true",
        default=os.environ.get("DEBUG_MODE", "false").lower() == "true",
        help="Enable Flask debug mode",
    )
    p_serve.set_defaults(func=_serve)

    p_mcp = sub.add_parser("mcp", help="Start the MCP server (stdio transport).")
    p_mcp.set_defaults(func=_mcp)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
