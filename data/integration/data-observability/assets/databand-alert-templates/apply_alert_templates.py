"""
apply_alert_templates.py
========================
Reads alert_policies.yaml and applies selected templates to a Databand instance
via the Databand REST API v1 (IBM Cloud).

Usage
-----
    # Apply a single policy template
    python apply_alert_templates.py --template null_rate_policy --pipeline my_pipeline

    # Apply all templates for a pipeline
    python apply_alert_templates.py --all --pipeline my_pipeline

    # Dry-run (print payloads without calling Databand)
    python apply_alert_templates.py --all --pipeline my_pipeline --dry-run

Environment
-----------
    DATABAND_URL            https://your-instance.databand.ai
    DATABAND_ACCESS_TOKEN   personal access token from Databand UI
    IBM_API_KEY             IBM Cloud API key (used if no access token)
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import time

import click
import requests
import yaml
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("apply_templates")

TEMPLATES_FILE = os.path.join(os.path.dirname(__file__), "alert_policies.yaml")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def _get_token() -> str:
    static = os.getenv("DATABAND_ACCESS_TOKEN")
    if static:
        return static
    resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": os.environ["IBM_API_KEY"],
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

def _render(template: dict, pipeline_name: str) -> dict:
    """Replace {{ pipeline_name }} placeholders in string values."""
    raw = json.dumps(template)
    rendered = raw.replace("{{ pipeline_name }}", pipeline_name)
    return json.loads(rendered)


# ---------------------------------------------------------------------------
# Databand API call
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _apply_policy(token: str, policy: dict) -> dict:
    base = os.environ["DATABAND_URL"].rstrip("/")
    url = f"{base}/api/v1/alert_defs"
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=policy,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command()
@click.option("--template", default=None, help="Template key from alert_policies.yaml")
@click.option("--all", "apply_all", is_flag=True, help="Apply all templates")
@click.option("--pipeline", required=True, help="Pipeline name to embed in templates")
@click.option("--dry-run", is_flag=True, help="Print rendered payloads without calling Databand")
def cli(template: str | None, apply_all: bool, pipeline: str, dry_run: bool) -> None:
    """Apply Databand alert policy templates to an IBM Databand instance."""
    with open(TEMPLATES_FILE) as fh:
        all_templates = yaml.safe_load(fh)

    if apply_all:
        selected = all_templates
    elif template:
        if template not in all_templates:
            click.echo(f"Template '{template}' not found. Available: {list(all_templates)}")
            sys.exit(1)
        selected = {template: all_templates[template]}
    else:
        click.echo("Specify --template <name> or --all")
        sys.exit(1)

    token = None if dry_run else _get_token()

    for key, tmpl in selected.items():
        payload = _render(tmpl, pipeline)
        if dry_run:
            click.echo(f"\n{'='*60}\nTemplate: {key}")
            click.echo(json.dumps(payload, indent=2))
        else:
            logger.info("Applying template: %s", key)
            result = _apply_policy(token, payload)  # type: ignore[arg-type]
            click.echo(f"[OK] {key} → uid={result.get('uid', 'N/A')}")


if __name__ == "__main__":
    cli()
