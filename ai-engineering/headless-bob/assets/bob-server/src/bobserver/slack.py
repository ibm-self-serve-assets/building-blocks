from collections import deque
import hashlib
import hmac
import json
import logging
import re
from threading import Lock, Thread
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, Response

from bobserver.config import Settings
from bobserver.tasks import BobPromptRequest, get_bob_prompt_status, start_bob_prompt


MAX_SLACK_TEXT_LENGTH = 12000
LOGGER = logging.getLogger(__name__)
_slack_context_cache: dict[str, deque[dict[str, str]]] = {}
_slack_context_lock = Lock()
_slack_intervention_last_seen: dict[str, float] = {}
_slack_intervention_lock = Lock()
BOB_SCAFFOLDING_PREFIXES = (
    "YOLO mode is enabled",
    "I'll read the context file",
    "I need to understand",
    "Let me start by",
    "Let me explore",
    "Looking at the context",
)
BOB_TOOL_PREFIXES = (
    "[using tool",
    "[tool",
    "<execute_command>",
    "</execute_command>",
    "<command>",
    "</command>",
    "<read_file>",
    "</read_file>",
)
SLACK_PROMPT_PREFIX = """\
You are answering from Bobserver inside Slack.
Read /workspace/bob_context.md first if it exists.
Return only the final answer for the Slack user.
Do not include <thinking>, hidden reasoning, tool calls, command XML, or raw setup logs.
Do not include Node.js deprecation warnings.
Keep the answer concise, preferably under 1200 characters.
If the user asks about open issues, open cases, or Salesforce cases, use the Salesforce case tools available in the workspace and summarize the result.
"""
SLACK_AUTONOMOUS_PROMPT_PREFIX = """\
You are Bobserver watching a Slack incident channel.
Read /workspace/bob_context.md first if it exists.
Return a concise, helpful Slack reply.
Do not execute remediation, write Salesforce comments, attach files, or make changes unless a human explicitly asks.
Focus on likely incident impact, what to check next, and the safest recommended action.
"""


async def handle_slack_command(request: Request, settings: Settings) -> JSONResponse:
    body = await request.body()
    _verify_slack_request(request, body, settings)
    form = _parse_form_body(body)
    command = form.get("command", "/bob").strip() or "/bob"
    prompt = form.get("text", "").strip()
    response_url = form.get("response_url", "")
    channel_id = form.get("channel_id", "")

    if not prompt:
        return JSONResponse(
            {
                "response_type": "ephemeral",
                "text": "Send a prompt after the command, for example: `/bob summarize today orders`.",
            }
        )

    warroom_response = _maybe_handle_warroom_command(prompt, channel_id, response_url, settings)
    if warroom_response:
        return warroom_response

    slack_context = _recent_slack_context(channel_id, settings)
    job = start_bob_prompt(
        BobPromptRequest(prompt=_slack_prompt(prompt, slack_context=slack_context), timeoutSeconds=180, yolo=True, workspaceMode="shared"),
        settings,
    )
    Thread(
        target=_post_slash_command_result,
        args=(job["id"], response_url, channel_id, f"{command} {prompt}", settings),
        daemon=True,
    ).start()

    return JSONResponse(
        {
            "response_type": "ephemeral",
            "text": f"Bob is working on `{job['id']}`. I will post the result back here.",
        }
    )


async def handle_slack_events(request: Request, settings: Settings) -> Response:
    body = await request.body()
    _verify_slack_request(request, body, settings)
    payload = json.loads(body.decode("utf-8") or "{}")

    if payload.get("type") == "url_verification":
        return JSONResponse({"challenge": payload.get("challenge", "")})

    if payload.get("type") != "event_callback":
        return Response(status_code=200)

    event = payload.get("event") or {}
    if event.get("type") == "app_mention" and not event.get("bot_id"):
        Thread(target=_handle_app_mention, args=(event, settings), daemon=True).start()
    elif event.get("type") == "message":
        Thread(target=_handle_message_event, args=(event, settings), daemon=True).start()

    return Response(status_code=200)


async def handle_slack_interactivity(request: Request, settings: Settings) -> JSONResponse:
    body = await request.body()
    _verify_slack_request(request, body, settings)
    form = _parse_form_body(body)
    payload_text = form.get("payload", "{}")
    payload = json.loads(payload_text)
    callback_id = payload.get("callback_id") or payload.get("view", {}).get("callback_id") or "interaction"
    return JSONResponse({"response_type": "ephemeral", "text": f"Received Slack interaction `{callback_id}`."})


def _handle_app_mention(event: dict[str, Any], settings: Settings) -> None:
    channel = event.get("channel", "")
    thread_ts = event.get("thread_ts") or event.get("ts")
    text = _strip_bot_mentions(event.get("text", "")).strip()
    if not channel or not text:
        return

    job = start_bob_prompt(BobPromptRequest(prompt=_slack_prompt(text), timeoutSeconds=180, yolo=True, workspaceMode="shared"), settings)
    _post_slack_message(channel, f"Bob is working on `{job['id']}`.", settings, thread_ts=thread_ts)
    result = _wait_for_job(job["id"])
    _post_slack_message(channel, _format_job_result(result, text), settings, thread_ts=thread_ts)


def _handle_message_event(event: dict[str, Any], settings: Settings) -> None:
    if _is_ignorable_message_event(event):
        return
    channel = str(event.get("channel") or "")
    text = _normalize_slack_context_text(str(event.get("text") or ""))
    if not channel or not text:
        return

    _record_slack_message(channel, event, settings)
    if not _should_auto_intervene(channel, text, settings):
        return

    Thread(target=_auto_intervene_on_message, args=(channel, event, text, settings), daemon=True).start()


def _auto_intervene_on_message(channel: str, event: dict[str, Any], text: str, settings: Settings) -> None:
    thread_ts = str(event.get("thread_ts") or event.get("ts") or "")
    context = _cached_slack_context(channel, settings)
    prompt = (
        f"{SLACK_AUTONOMOUS_PROMPT_PREFIX}\n"
        f"Recent Slack context:\n{context}\n\n"
        f"Trigger message: {text}\n\n"
        "Offer a short incident triage suggestion. If Agentforce, Instana, or Salesforce Cases are mentioned, "
        "connect the symptoms to likely next actions."
    )
    job = start_bob_prompt(BobPromptRequest(prompt=prompt, timeoutSeconds=180, yolo=True, workspaceMode="shared"), settings)
    _post_slack_message(channel, f"I noticed a possible incident signal and am checking context in `{job['id']}`.", settings, thread_ts=thread_ts)
    result = _wait_for_job(job["id"])
    _post_slack_message(channel, _format_job_result(result, f"Auto-triage: {text}"), settings, thread_ts=thread_ts)


def _maybe_handle_warroom_command(
    prompt: str,
    source_channel: str,
    response_url: str,
    settings: Settings,
) -> JSONResponse | None:
    if not _is_warroom_request(prompt):
        return None

    case_number = _extract_case_number(prompt)
    if not case_number:
        return JSONResponse(
            {
                "response_type": "ephemeral",
                "text": "Tell me which Salesforce case to use, for example: `/bobsf create a Slack war room for Salesforce case 00001030`.",
            }
        )
    if not settings.slack_bot_token:
        return JSONResponse(
            {
                "response_type": "ephemeral",
                "text": "I need `BOBSERVER_SLACK_BOT_TOKEN` before I can create a Slack war room.",
            }
        )

    channel_name = _warroom_channel_name(case_number)
    result = _create_slack_warroom(channel_name, case_number, prompt, settings)
    if result.get("ok"):
        channel_id = str(result["channel"]["id"])
        channel_label = f"<#{channel_id}|{channel_name}>"
        users = _slack_warroom_user_ids(settings)
        invite_text = f" and invited {len(users)} configured responder(s)" if users else ""
        message = f"Created Slack war room {channel_label}{invite_text} for Salesforce case `{case_number}`."
        _post_slack_message(
            channel_id,
            _warroom_intro_message(case_number, prompt),
            settings,
        )
        if response_url:
            _post_json(response_url, {"response_type": "in_channel", "text": message, "mrkdwn": True})
        elif source_channel:
            _post_slack_message(source_channel, message, settings)
        return JSONResponse({"response_type": "ephemeral", "text": message})

    error = result.get("error") or "unknown_error"
    help_text = "I could not create the Slack war room."
    if error == "missing_scope":
        help_text += " Add `channels:manage` and reinstall the Slack app."
    elif error == "name_taken":
        help_text += f" Channel `#{channel_name}` already exists."
    else:
        help_text += f" Slack returned `{error}`."
    return JSONResponse({"response_type": "ephemeral", "text": help_text})


def _is_warroom_request(prompt: str) -> bool:
    lowered = prompt.lower()
    return ("war room" in lowered or "warroom" in lowered) and ("create" in lowered or "open" in lowered)


def _extract_case_number(prompt: str) -> str:
    match = re.search(r"\b(?:case\s*)?(\d{6,10})\b", prompt, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def _warroom_channel_name(case_number: str) -> str:
    return _normalize_slack_channel_name(f"warroom-case-{case_number}")


def _normalize_slack_channel_name(name: str) -> str:
    normalized = name.lower()
    normalized = re.sub(r"[^a-z0-9_-]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-_")
    return normalized[:80] or "warroom-case"


def _slack_warroom_user_ids(settings: Settings) -> list[str]:
    seen = set()
    users = []
    for user_id in settings.slack_warroom_users.split(","):
        user_id = user_id.strip()
        if user_id and user_id not in seen:
            users.append(user_id)
            seen.add(user_id)
    return users


def _create_slack_warroom(
    channel_name: str,
    case_number: str,
    prompt: str,
    settings: Settings,
) -> dict[str, Any]:
    create = _slack_api_post(
        "conversations.create",
        {"name": channel_name, "is_private": False},
        settings,
    )
    if not create.get("ok"):
        return create

    channel = create.get("channel") or {}
    channel_id = str(channel.get("id") or "")
    if not channel_id:
        return {"ok": False, "error": "missing_channel_id"}

    users = _slack_warroom_user_ids(settings)
    if users:
        invite = _slack_api_post(
            "conversations.invite",
            {"channel": channel_id, "users": ",".join(users)},
            settings,
        )
        if not invite.get("ok"):
            LOGGER.warning("Slack conversations.invite returned error for case %s: %s", case_number, invite.get("error", invite))

    return create


def _warroom_intro_message(case_number: str, prompt: str) -> str:
    return (
        f"*War room for Salesforce case `{case_number}`*\n"
        f"*Trigger:* `{_escape_slack_inline_code(_truncate_inline(prompt, 500))}`\n"
        "*Suggested first checks:*\n"
        "- Confirm current Instana error rate and affected service.\n"
        "- Check Agentforce return-request failures and customer impact.\n"
        "- Decide whether to proceed with remediation or attach findings back to Salesforce."
    )


def _slack_api_post(method: str, payload: dict[str, Any], settings: Settings) -> dict[str, Any]:
    request = UrlRequest(
        f"https://slack.com/api/{method}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.slack_bot_token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError):
        LOGGER.exception("Slack %s request failed.", method)
        return {"ok": False, "error": "request_failed"}
    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError:
        LOGGER.warning("Slack %s returned non-JSON response: %s", method, response_body[:200])
        return {"ok": False, "error": "non_json_response"}
    if not payload.get("ok"):
        LOGGER.warning("Slack %s returned error: %s", method, payload.get("error", payload))
    return payload


def _post_slash_command_result(
    job_id: str,
    response_url: str,
    channel_id: str,
    original_request: str,
    settings: Settings,
) -> None:
    result = _wait_for_job(job_id)
    message = _format_job_result(result, original_request)
    if response_url:
        try:
            _post_json(response_url, {"response_type": "in_channel", "text": message, "mrkdwn": True})
            LOGGER.info("Posted Slack slash command result for %s with response_url.", job_id)
            return
        except Exception:
            LOGGER.exception("Failed to post Slack slash command result for %s with response_url.", job_id)
    if channel_id:
        _post_slack_message(channel_id, message, settings)
        LOGGER.info("Posted Slack slash command result for %s with chat.postMessage fallback.", job_id)
        return
    LOGGER.warning("No Slack response_url or channel_id was available for slash command result %s.", job_id)


def _wait_for_job(job_id: str) -> dict[str, Any]:
    for _ in range(600):
        result = get_bob_prompt_status(job_id)
        if result["state"] in {"completed", "failed", "cancelled"}:
            return result
        time.sleep(1)
    return {
        "id": job_id,
        "state": "running",
        "output": "",
        "error": "Still running after 10 minutes. Check Bobserver task status for details.",
    }


def _format_job_result(result: dict[str, Any], original_request: str = "") -> str:
    output = _clean_bob_output(result.get("output") or "")
    error = (result.get("error") or "").strip()
    status_line = f"Bob `{result.get('id')}` finished with state `{result.get('state')}`."
    detail = output or error or "No output returned."
    if error and output:
        detail = f"{output}\n\nError: {error}"
    detail = _markdown_to_slack_mrkdwn(detail)
    request_line = ""
    if original_request.strip():
        request_line = f"*Request:* `{_escape_slack_inline_code(_truncate_inline(original_request.strip()))}`\n"
    return f"{request_line}*Status:* {status_line}\n*Answer:*\n{_truncate(detail)}"


def _post_slack_message(channel: str, text: str, settings: Settings, thread_ts: str | None = None) -> None:
    if not settings.slack_bot_token:
        LOGGER.warning("BOBSERVER_SLACK_BOT_TOKEN is not configured; cannot post Slack chat message.")
        return
    payload: dict[str, Any] = {"channel": channel, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    request = UrlRequest(
        "https://slack.com/api/chat.postMessage",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.slack_bot_token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8")
    except (HTTPError, URLError):
        LOGGER.exception("Slack chat.postMessage request failed.")
        return
    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError:
        LOGGER.warning("Slack chat.postMessage returned non-JSON response: %s", response_body[:200])
        return
    if not payload.get("ok"):
        LOGGER.warning("Slack chat.postMessage returned error: %s", payload.get("error", payload))


def _post_json(url: str, payload: dict[str, Any]) -> None:
    request = UrlRequest(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        response.read()


def _verify_slack_request(request: Request, body: bytes, settings: Settings) -> None:
    if not settings.slack_signing_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BOBSERVER_SLACK_SIGNING_SECRET is not configured.",
        )

    timestamp = request.headers.get("x-slack-request-timestamp", "")
    signature = request.headers.get("x-slack-signature", "")
    try:
        request_time = int(timestamp)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Slack timestamp.") from exc

    if abs(time.time() - request_time) > 60 * 5:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Stale Slack request.")

    base = b"v0:" + timestamp.encode("utf-8") + b":" + body
    expected = "v0=" + hmac.new(settings.slack_signing_secret.encode("utf-8"), base, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Slack signature.")


def _parse_form_body(body: bytes) -> dict[str, str]:
    parsed = parse_qs(body.decode("utf-8"), keep_blank_values=True)
    return {key: values[-1] for key, values in parsed.items()}


def _strip_bot_mentions(text: str) -> str:
    words = [word for word in text.split() if not (word.startswith("<@") and word.endswith(">"))]
    return " ".join(words)


def _slack_prompt(prompt: str, *, slack_context: str = "") -> str:
    context_block = f"\nRecent Slack context before the request:\n{slack_context.strip()}\n" if slack_context.strip() else ""
    return f"{SLACK_PROMPT_PREFIX}{context_block}\nUser request: {prompt.strip()}"


def _recent_slack_context(channel_id: str, settings: Settings) -> str:
    cached = _cached_slack_context(channel_id, settings)
    if cached:
        return cached
    return _fetch_slack_history_context(channel_id, settings)


def _record_slack_message(channel_id: str, event: dict[str, Any], settings: Settings) -> None:
    limit = max(settings.slack_context_cache_limit, settings.slack_history_limit, 1)
    text = _normalize_slack_context_text(str(event.get("text") or ""))
    if not text:
        return
    message = {
        "ts": str(event.get("ts") or ""),
        "sender": str(event.get("user") or event.get("username") or "unknown"),
        "text": text,
    }
    with _slack_context_lock:
        messages = _slack_context_cache.setdefault(channel_id, deque(maxlen=limit))
        messages.append(message)


def _cached_slack_context(channel_id: str, settings: Settings) -> str:
    limit = max(0, min(settings.slack_history_limit, 20))
    if not channel_id or limit == 0:
        return ""
    with _slack_context_lock:
        messages = list(_slack_context_cache.get(channel_id, ()))
    lines = []
    for message in messages[-limit:]:
        text = message.get("text", "")
        sender = message.get("sender", "unknown")
        if text:
            lines.append(f"- {sender}: {_truncate_inline(text, 500)}")
    return "\n".join(lines)


def _is_ignorable_message_event(event: dict[str, Any]) -> bool:
    if event.get("bot_id") or event.get("app_id"):
        return True
    subtype = event.get("subtype")
    if subtype and subtype not in {"file_share"}:
        return True
    if str(event.get("text") or "").startswith("/"):
        return True
    return False


def _should_auto_intervene(channel_id: str, text: str, settings: Settings) -> bool:
    if not settings.slack_auto_intervene_enabled:
        return False
    lowered = text.lower()
    keywords = [keyword.strip().lower() for keyword in settings.slack_auto_intervene_keywords.split(",") if keyword.strip()]
    if not keywords or not any(keyword in lowered for keyword in keywords):
        return False
    now = time.time()
    cooldown = max(0, settings.slack_auto_intervene_cooldown_seconds)
    with _slack_intervention_lock:
        last_seen = _slack_intervention_last_seen.get(channel_id, 0)
        if now - last_seen < cooldown:
            return False
        _slack_intervention_last_seen[channel_id] = now
    return True


def _fetch_slack_history_context(channel_id: str, settings: Settings) -> str:
    limit = max(0, min(settings.slack_history_limit, 20))
    if not channel_id or not settings.slack_bot_token or limit == 0:
        return ""

    query = urlencode({"channel": channel_id, "limit": limit, "inclusive": "false"})
    request = UrlRequest(
        f"https://slack.com/api/conversations.history?{query}",
        headers={
            "Authorization": f"Bearer {settings.slack_bot_token}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError):
        LOGGER.exception("Slack conversations.history request failed.")
        return ""
    except json.JSONDecodeError:
        LOGGER.warning("Slack conversations.history returned non-JSON.")
        return ""

    if not payload.get("ok"):
        LOGGER.warning("Slack conversations.history returned error: %s", payload.get("error", payload))
        return ""

    messages = payload.get("messages") or []
    lines = []
    for message in reversed(messages):
        text = _normalize_slack_context_text(str(message.get("text") or ""))
        if not text:
            continue
        sender = str(message.get("user") or message.get("username") or "unknown")
        lines.append(f"- {sender}: {_truncate_inline(text, 500)}")
    return "\n".join(lines)


def _normalize_slack_context_text(text: str) -> str:
    text = re.sub(r"<@([A-Z0-9]+)>", r"@\1", text)
    text = re.sub(r"<(https?://[^|>]+)\|([^>]+)>", r"\2 (\1)", text)
    text = re.sub(r"<(https?://[^>]+)>", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _clean_bob_output(output: str) -> str:
    text = _strip_ansi(output)
    text = _extract_result_tag(text)
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = _extract_output_block(text)
    cleaned_lines = []
    skip_next_node_hint = False
    in_output_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append(line)
            continue
        if stripped in {"---output---", "---output---```", "```---output---"}:
            in_output_block = not in_output_block
            continue
        if _is_scaffolding_line(stripped):
            continue
        if stripped == "```" and in_output_block:
            continue
        if stripped.startswith("(node:") and "[DEP" in stripped:
            skip_next_node_hint = True
            continue
        if skip_next_node_hint and stripped.startswith("(Use `node"):
            skip_next_node_hint = False
            continue
        skip_next_node_hint = False
        if _is_tool_marker(stripped):
            continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)
    text = _remove_empty_code_fences(text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


def _extract_result_tag(text: str) -> str:
    matches = re.findall(r"<result>\s*(.*?)\s*</result>", text, flags=re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1]
    return text


def _extract_output_block(text: str) -> str:
    normalized = text.replace("```---output---", "---output---").replace("---output---```", "---output---")
    parts = normalized.split("---output---")
    if len(parts) >= 3:
        return parts[-2]
    if len(parts) == 2 and _looks_like_scaffold(parts[0]):
        return parts[1]
    return normalized


def _looks_like_scaffold(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "yolo mode is enabled",
            "<thinking>",
            "[using tool",
            "i'll read the context file",
        )
    )


def _is_scaffolding_line(stripped: str) -> bool:
    return any(stripped.startswith(prefix) for prefix in BOB_SCAFFOLDING_PREFIXES)


def _is_tool_marker(stripped: str) -> bool:
    return any(stripped.startswith(prefix) for prefix in BOB_TOOL_PREFIXES)


def _remove_empty_code_fences(text: str) -> str:
    return re.sub(r"```\s*```", "", text, flags=re.DOTALL)


def _markdown_to_slack_mrkdwn(text: str) -> str:
    chunks = re.split(r"(```[\s\S]*?```)", text)
    return "".join(
        chunk if chunk.startswith("```") and chunk.endswith("```") else _convert_markdown_prose_to_slack(chunk)
        for chunk in chunks
    ).strip()


def _convert_markdown_prose_to_slack(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            lines.append(f"*{_convert_markdown_inline_to_slack(heading.group(2).strip())}*")
            continue
        lines.append(_convert_markdown_inline_to_slack(line))
    return "\n".join(lines)


def _convert_markdown_inline_to_slack(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r"<\2|\1>", text)
    text = re.sub(r"\*\*([^*\n][^*\n]*?)\*\*", r"*\1*", text)
    text = re.sub(r"__([^_\n][^_\n]*?)__", r"*\1*", text)
    text = re.sub(r"~~([^~\n]+?)~~", r"~\1~", text)
    return text


def _escape_slack_inline_code(text: str) -> str:
    return text.replace("`", "'")


def _truncate_inline(text: str, limit: int = 240) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 16].rstrip() + " ... truncated"


def _truncate(text: str) -> str:
    if len(text) <= MAX_SLACK_TEXT_LENGTH:
        return text
    return text[: MAX_SLACK_TEXT_LENGTH - 20].rstrip() + "\n... truncated ..."
