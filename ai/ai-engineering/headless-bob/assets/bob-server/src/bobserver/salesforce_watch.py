import json
import logging
from pathlib import Path
import sqlite3
import subprocess
import sys
from threading import Lock, Thread
import time
from typing import Any

from bobserver.config import Settings
from bobserver.slack import (
    _create_slack_warroom,
    _post_slack_message,
    _slack_warroom_user_ids,
    _warroom_channel_name,
)


LOGGER = logging.getLogger(__name__)
_watcher_lock = Lock()
_watcher_started = False


def start_salesforce_case_watcher(settings: Settings) -> None:
    global _watcher_started
    if not settings.salesforce_case_watch_enabled:
        return
    with _watcher_lock:
        if _watcher_started:
            return
        _watcher_started = True
    Thread(target=_watch_loop, args=(settings,), daemon=True).start()
    LOGGER.info("Started Salesforce case watcher.")


def _watch_loop(settings: Settings) -> None:
    _ensure_db(settings)
    interval = max(10, settings.salesforce_case_watch_interval_seconds)
    while True:
        try:
            _poll_salesforce_cases(settings)
        except Exception:
            LOGGER.exception("Salesforce case watcher poll failed.")
        time.sleep(interval)


def _poll_salesforce_cases(settings: Settings) -> None:
    if not settings.slack_bot_token:
        LOGGER.warning("Salesforce case watcher skipped because BOBSERVER_SLACK_BOT_TOKEN is not configured.")
        return

    cases = _fetch_candidate_cases(settings)
    for case in cases:
        case_number = str(case.get("Case Number") or "").strip()
        if not case_number or _is_processed(settings, case_number):
            continue
        case = _fetch_case_details(settings, case_number) or case
        _create_case_warroom(case, settings)


def _fetch_candidate_cases(settings: Settings) -> list[dict[str, Any]]:
    script = Path(settings.salesforce_case_watch_script)
    if not script.exists():
        local_script = Path.cwd() / "scripts" / "salesforce-cases.py"
        script = local_script if local_script.exists() else script

    command = [
        sys.executable,
        str(script),
        "list",
        "--where",
        settings.salesforce_case_watch_query,
        "--limit",
        str(max(1, settings.salesforce_case_watch_limit)),
        "--format",
        "json",
    ]
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=45,
    )
    if completed.returncode != 0:
        LOGGER.warning("Salesforce case watcher query failed: %s", completed.stderr.strip()[:500])
        return []
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        LOGGER.warning("Salesforce case watcher query returned non-JSON output.")
        return []
    return payload if isinstance(payload, list) else []


def _fetch_case_details(settings: Settings, case_number: str) -> dict[str, Any] | None:
    script = Path(settings.salesforce_case_watch_script)
    if not script.exists():
        local_script = Path.cwd() / "scripts" / "salesforce-cases.py"
        script = local_script if local_script.exists() else script

    command = [
        sys.executable,
        str(script),
        "get",
        "--case-number",
        case_number,
        "--format",
        "json",
    ]
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=45,
    )
    if completed.returncode != 0:
        LOGGER.warning("Salesforce case watcher detail query failed for %s: %s", case_number, completed.stderr.strip()[:500])
        return None
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        LOGGER.warning("Salesforce case watcher detail query returned non-JSON output for %s.", case_number)
        return None
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        return payload[0]
    return None


def _create_case_warroom(case: dict[str, Any], settings: Settings) -> None:
    case_number = str(case.get("Case Number") or "").strip()
    channel_name = _warroom_channel_name(case_number)
    _record_case_status(settings, case_number, "creating", channel_name=channel_name)

    prompt = _case_prompt(case)
    result = _create_slack_warroom(channel_name, case_number, prompt, settings)
    if not result.get("ok"):
        error = str(result.get("error") or "unknown_error")
        _record_case_status(settings, case_number, "failed", channel_name=channel_name, error=error)
        LOGGER.warning("Failed to create Slack war room for Salesforce case %s: %s", case_number, error)
        return

    channel = result.get("channel") or {}
    channel_id = str(channel.get("id") or "")
    _record_case_status(settings, case_number, "created", channel_id=channel_id, channel_name=channel_name)
    if channel_id:
        _post_slack_message(channel_id, _case_warroom_intro(case, settings), settings)
    _add_salesforce_warroom_comment(case_number, channel_name, channel_id, settings)
    LOGGER.info("Created Slack war room %s for Salesforce case %s.", channel_name, case_number)


def _case_prompt(case: dict[str, Any]) -> str:
    description = _truncate(str(case.get("Description") or ""), 300)
    return (
        f"Salesforce case {case.get('Case Number')} triggered an incident war room. "
        f"Subject: {case.get('Subject')}. Priority: {case.get('Priority')}. "
        f"Origin: {case.get('Case Origin')}. Owner: {case.get('Case Owner')}. "
        f"Description: {description}"
    )


def _case_warroom_intro(case: dict[str, Any], settings: Settings) -> str:
    responders = len(_slack_warroom_user_ids(settings))
    description = _truncate(str(case.get("Description") or ""), 500)
    description_line = f"*Description:* {description}\n" if description else ""
    return (
        f"*War room for Salesforce case `{case.get('Case Number')}`*\n"
        f"*Subject:* {case.get('Subject') or '(blank)'}\n"
        f"{description_line}"
        f"*Priority:* {case.get('Priority') or '(blank)'} | *Origin:* {case.get('Case Origin') or '(blank)'} | "
        f"*Owner:* {case.get('Case Owner') or '(blank)'}\n"
        f"*Responders invited:* {responders}\n"
        "*Suggested first checks:*\n"
        f"{_suggested_first_checks(case)}"
    )


def _suggested_first_checks(case: dict[str, Any]) -> str:
    text = " ".join(str(case.get(key) or "") for key in ("Subject", "Description")).lower()
    if any(term in text for term in ("certificate", "tls", "ssl", "expiry", "expires", "expire")):
        return (
            "- Check `/cert-info` for current certificate expiry and rotationRequired status.\n"
            "- Check `/health` for current service status before remediation.\n"
            "- Review the approved Ansible certificate-rotation playbook and request human approval before execution."
        )
    return (
        "- Confirm current Instana error rate and affected service.\n"
        "- Check Agentforce return-request failures and customer impact.\n"
        "- Decide whether to proceed with remediation or attach findings back to Salesforce."
    )


def _truncate(value: str, limit: int) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def _add_salesforce_warroom_comment(case_number: str, channel_name: str, channel_id: str, settings: Settings) -> None:
    script = Path(settings.salesforce_case_watch_script)
    if not script.exists():
        local_script = Path.cwd() / "scripts" / "salesforce-cases.py"
        script = local_script if local_script.exists() else script
    channel_ref = f"#{channel_name}" if not channel_id else f"#{channel_name} ({channel_id})"
    comment = f"Bob created Slack war room {channel_ref} for incident collaboration."
    command = [
        sys.executable,
        str(script),
        "add-comment",
        "--case-number",
        case_number,
        "--comment",
        comment,
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=45)
    if completed.returncode != 0:
        LOGGER.warning("Failed to add Salesforce war-room comment for case %s: %s", case_number, completed.stderr.strip()[:500])


def _ensure_db(settings: Settings) -> None:
    db_path = Path(settings.salesforce_case_watch_db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            create table if not exists salesforce_case_warrooms (
                case_number text primary key,
                status text not null,
                channel_id text,
                channel_name text,
                last_error text,
                created_at real not null,
                updated_at real not null
            )
            """
        )


def _is_processed(settings: Settings, case_number: str) -> bool:
    db_path = Path(settings.salesforce_case_watch_db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "select status from salesforce_case_warrooms where case_number = ?",
            (case_number,),
        ).fetchone()
    return bool(row and row[0] in {"creating", "created"})


def _record_case_status(
    settings: Settings,
    case_number: str,
    status: str,
    *,
    channel_id: str = "",
    channel_name: str = "",
    error: str = "",
) -> None:
    now = time.time()
    db_path = Path(settings.salesforce_case_watch_db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            insert into salesforce_case_warrooms (
                case_number, status, channel_id, channel_name, last_error, created_at, updated_at
            )
            values (?, ?, ?, ?, ?, ?, ?)
            on conflict(case_number) do update set
                status = excluded.status,
                channel_id = excluded.channel_id,
                channel_name = excluded.channel_name,
                last_error = excluded.last_error,
                updated_at = excluded.updated_at
            """,
            (case_number, status, channel_id, channel_name, error, now, now),
        )
