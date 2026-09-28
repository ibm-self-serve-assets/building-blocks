from __future__ import annotations

from unittest.mock import patch

import pytest

from real_time_guardrails.cli import build_parser, main


def test_serve_subcommand_parses_args() -> None:
    parser = build_parser()
    args = parser.parse_args(["serve", "--host", "127.0.0.1", "--port", "9000"])
    assert args.command == "serve"
    assert args.host == "127.0.0.1"
    assert args.port == 9000
    assert args.debug is False


def test_mcp_subcommand_parses() -> None:
    parser = build_parser()
    args = parser.parse_args(["mcp"])
    assert args.command == "mcp"


def test_no_subcommand_errors(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([])


def test_missing_credentials_exits_2(clean_env: None, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["serve"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "WATSONX_APIKEY" in err


def test_cli_does_not_require_project_id(
    clean_env: None, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """WXG_PROJECT_ID is optional — only WATSONX_APIKEY and WXG_SERVICE_INSTANCE_ID required at CLI."""
    monkeypatch.setenv("WATSONX_APIKEY", "k")
    monkeypatch.setenv("WXG_SERVICE_INSTANCE_ID", "i")
    with patch("real_time_guardrails.rest.server.create_app") as mock_create:
        rc = main(["serve", "--port", "9000"])
    assert rc == 0
    err = capsys.readouterr().err
    assert "WXG_PROJECT_ID" not in err


def test_serve_invokes_create_app_when_creds_present(filled_env, monkeypatch: pytest.MonkeyPatch) -> None:
    with patch("real_time_guardrails.rest.server.create_app") as mock_create:
        mock_app = mock_create.return_value
        rc = main(["serve", "--port", "9999"])
        assert rc == 0
        mock_create.assert_called_once()
        mock_app.run.assert_called_once_with(host="0.0.0.0", port=9999, debug=False)


def test_mcp_invokes_serve_when_creds_present(filled_env, monkeypatch: pytest.MonkeyPatch) -> None:
    with patch("real_time_guardrails.mcp.server.serve") as mock_serve:
        rc = main(["mcp"])
        assert rc == 0
        mock_serve.assert_called_once()
