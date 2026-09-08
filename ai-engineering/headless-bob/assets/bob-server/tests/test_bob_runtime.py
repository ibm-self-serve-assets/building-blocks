import json
import signal
import subprocess

import pytest

from bobserver.bob_runtime import BobStreamState, build_bob_args, parse_bob_output
from bobserver import tasks


def test_build_bob_args_applies_streaming_budget_and_readonly_tools():
    args = build_bob_args(max_coins=12, safety_profile="readonly")

    assert args[:5] == ["--accept-license", "-o", "stream-json", "--max-coins", "12"]
    assert args.count("--allowed-tools") == 3
    assert "--approval-mode" not in args


def test_build_bob_args_maps_yolo_to_trusted_mode():
    args = build_bob_args(max_coins=5, safety_profile="readonly", yolo=True)

    assert args[-2:] == ["--approval-mode", "yolo"]
    assert "--allowed-tools" not in args


def test_build_bob_args_rejects_unknown_profile():
    with pytest.raises(ValueError, match="Unknown Bob safety profile"):
        build_bob_args(max_coins=5, safety_profile="unsafe")


def test_stream_parser_filters_reasoning_and_extracts_final_answer_and_usage():
    lines = [
        {"type": "init", "session_id": "session-1", "model": "premium"},
        {"type": "message", "role": "assistant", "content": "private reasoning", "delta": True},
        {"type": "tool_use", "tool_name": "Read", "tool_id": "tool-1", "parameters": {}},
        {"type": "tool_result", "tool_id": "tool-1", "status": "success"},
        {"type": "tool_use", "tool_name": "attempt_completion", "parameters": {"result": "SAFE_FINAL"}},
        {
            "type": "result",
            "status": "success",
            "stats": {
                "total_tokens": 1234,
                "tool_calls": 2,
                "duration_ms": 2500,
                "budget_spend": 0.4,
                "max_budget": 10,
            },
        },
    ]

    state = parse_bob_output("\n".join(json.dumps(line) for line in lines))

    assert state.final_text == "SAFE_FINAL"
    assert "private reasoning" not in state.final_text
    assert state.session_id == "session-1"
    assert state.model == "premium"
    assert state.status == "success"
    assert state.usage["totalTokens"] == 1234
    assert state.usage["coinsSpent"] == 0.4


def test_stream_parser_emits_semantic_progress_without_assistant_deltas():
    state = BobStreamState()

    assert state.consume(json.dumps({"type": "message", "role": "assistant", "delta": True, "content": "secret"})) == []
    events = state.consume(json.dumps({"type": "tool_use", "tool_name": "Grep", "parameters": {}}))

    assert events == [("progress", {"phase": "tool_use", "tool": "Grep", "toolCalls": 1})]


def test_terminate_process_stops_entire_process_group(monkeypatch):
    signals = []

    class Process:
        pid = 4321
        returncode = None
        waits = 0

        def poll(self):
            return self.returncode

        def wait(self, timeout):
            self.waits += 1
            if self.waits == 1:
                raise subprocess.TimeoutExpired("bob", timeout)
            self.returncode = -signal.SIGKILL
            return self.returncode

    monkeypatch.setattr(tasks.os, "killpg", lambda pid, sent_signal: signals.append((pid, sent_signal)))
    tasks._terminate_process(Process(), grace_seconds=0)

    assert signals == [(4321, signal.SIGTERM), (4321, signal.SIGKILL)]
