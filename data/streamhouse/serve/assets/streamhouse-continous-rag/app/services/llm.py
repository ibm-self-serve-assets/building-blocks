from __future__ import annotations

import logging
import threading
import time

import httpx

from app.config import Settings
from app.models import RagEvidence

LOGGER = logging.getLogger(__name__)


class GroundedGenerator:
    def generate(self, question: str, evidence: list[RagEvidence]) -> tuple[str, str]:
        raise NotImplementedError


class DeterministicGroundedGenerator(GroundedGenerator):
    """No-LLM fallback that still proves retrieval freshness and grounding."""

    def generate(self, question: str, evidence: list[RagEvidence]) -> tuple[str, str]:
        if not evidence:
            return (
                "I do not have enough indexed factory knowledge to answer that yet. "
                "Add or stream a maintenance note, SOP, or service bulletin and try again.",
                "grounded-template",
            )

        strongest = evidence[0]
        supporting = evidence[1:3]
        answer = (
            f"The most relevant current knowledge is **{strongest.title}**. "
            f"{_shorten(strongest.text, 420)}"
        )
        if supporting:
            titles = ", ".join(item.title for item in supporting)
            answer += f" Supporting evidence was also retrieved from {titles}."
        answer += (
            "\n\nThis response is intentionally extractive because LLM_PROVIDER=none. "
            "Configure watsonx.ai to turn the same continuously refreshed evidence into a synthesized answer."
        )
        return answer, "grounded-template"


class WatsonxGenerator(GroundedGenerator):
    def __init__(self, settings: Settings):
        self.settings = settings
        self._token: str | None = None
        self._token_expires_at = 0.0
        self._lock = threading.Lock()

    def _iam_token(self) -> str:
        with self._lock:
            if self._token and time.time() < self._token_expires_at:
                return self._token

            response = httpx.post(
                "https://iam.cloud.ibm.com/identity/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": self.settings.watsonx_api_key,
                },
                timeout=20.0,
            )
            response.raise_for_status()
            payload = response.json()
            self._token = payload["access_token"]
            expires_in = int(payload.get("expires_in", 3600))
            self._token_expires_at = time.time() + max(60, expires_in - 120)
            return self._token

    def generate(self, question: str, evidence: list[RagEvidence]) -> tuple[str, str]:
        if not evidence:
            return "No indexed evidence was retrieved for this question.", "watsonx"

        context = "\n\n".join(
            f"[E{i}] title: {item.title} | source: {item.source} | asset: {item.asset_id or 'n/a'} | freshness: {item.updated_at}\n{item.text}"
            for i, item in enumerate(evidence, 1)
        )
        prompt = (
            "<|begin_of_text|>"
            "<|start_header_id|>system<|end_header_id|>\n"
            "You are a manufacturing reliability assistant for a factory floor running Gear Assembly production on LINE-01. "
            "You help operators and maintenance technicians make fast, accurate decisions about machine condition, quality, and maintenance.\n\n"
            "Rules:\n"
            "- Answer ONLY from the evidence provided. Never invent part numbers, measurements, or procedures.\n"
            "- Cite each piece of evidence inline as [E1], [E2], etc.\n"
            "- If the evidence is insufficient, say so clearly rather than guessing.\n"
            "- Be concise and action-oriented — the reader is on a factory floor, not reading a report.\n"
            "- Lead with the direct answer, then explain the supporting evidence.\n"
            "<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n"
            f"QUESTION: {question}\n\n"
            f"EVIDENCE:\n{context}\n"
            "<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n"
        )

        endpoint = (
            f"{self.settings.watsonx_url.rstrip('/')}/ml/v1/text/generation"
            f"?version={self.settings.watsonx_api_version}"
        )
        response = httpx.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {self._iam_token()}",
                "Content-Type": "application/json",
            },
            json={
                "model_id": self.settings.watsonx_model_id,
                "project_id": self.settings.watsonx_project_id,
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 500,
                    "repetition_penalty": 1.05,
                    "stop_sequences": ["<|eot_id|>", "<|start_header_id|>"],
                },
            },
            timeout=60.0,
        )
        response.raise_for_status()
        payload = response.json()
        text = payload.get("results", [{}])[0].get("generated_text", "").strip()
        # Strip any leaked stop tokens
        for stop in ("<|eot_id|>", "<|start_header_id|>"):
            text = text.split(stop)[0].strip()
        if not text:
            raise RuntimeError("watsonx.ai returned an empty generated_text response")
        return text, f"watsonx · {self.settings.watsonx_model_id}"


def build_generator(settings: Settings) -> GroundedGenerator:
    if settings.watsonx_ready:
        return WatsonxGenerator(settings)
    return DeterministicGroundedGenerator()


def _shorten(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"
