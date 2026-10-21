"""
IBM watsonx.data Intelligence – Lineage Impact Analyzer
=========================================================
CLI tool for column-level impact analysis using the Manta lineage graph
exposed through the watsonx.data Intelligence REST API.

Given a source asset, this tool:
  1. Resolves the downstream lineage graph via GET /data_lineage/impact_analysis
  2. Renders a human-readable dependency tree
  3. Generates a machine-readable JSON impact report
  4. Optionally archives the report to IBM COS

Usage
-----
    # Show all downstream dependencies for an asset
    python impact_analyzer.py --asset-id <asset-id>

    # Save JSON report to file
    python impact_analyzer.py --asset-id <asset-id> --output report.json

    # Archive to IBM COS
    python impact_analyzer.py --asset-id <asset-id> --archive-cos

Environment variables: IBM_API_KEY, WXDI_PROJECT_ID, WXDI_REGION (or WXDI_BASE_URL)
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

import click
import ibm_boto3
import requests
from dotenv import load_dotenv
from ibm_botocore.client import Config
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("impact_analyzer")


# ---------------------------------------------------------------------------
# IAM auth
# ---------------------------------------------------------------------------

def _get_token(api_key: str) -> str:
    resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Lineage API calls
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _get_impact(token: str, base_url: str, project_id: str, asset_id: str) -> dict:
    url = f"{base_url}/data_lineage/impact_analysis"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        params={"project_id": project_id, "asset_id": asset_id},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _get_graph(token: str, base_url: str, project_id: str, asset_id: str, depth: int = 5) -> dict:
    url = f"{base_url}/data_lineage/graphs"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        params={"project_id": project_id, "asset_id": asset_id, "direction": "downstream", "depth": depth},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def _render_tree(impact: dict, indent: int = 0) -> str:
    """Recursively render the impact graph as a human-readable tree."""
    lines: list[str] = []
    nodes = impact.get("downstream_assets", impact.get("nodes", []))
    for node in nodes:
        name = node.get("name") or node.get("asset_id", "unknown")
        asset_type = node.get("asset_type", "")
        lines.append("  " * indent + f"└── {name}  [{asset_type}]")
        children = node.get("downstream_assets", node.get("children", []))
        if children:
            lines.append(_render_tree({"downstream_assets": children}, indent + 1))
    return "\n".join(lines)


def _build_report(asset_id: str, impact: dict, graph: dict) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_asset_id": asset_id,
        "impact_summary": impact,
        "lineage_graph": graph,
    }


# ---------------------------------------------------------------------------
# IBM COS archiving
# ---------------------------------------------------------------------------

def _archive_to_cos(report: dict, asset_id: str) -> str:
    client = ibm_boto3.client(
        "s3",
        ibm_api_key_id=os.environ["COS_API_KEY"],
        ibm_service_instance_id=os.environ["COS_INSTANCE_CRN"],
        config=Config(signature_version="oauth"),
        endpoint_url=os.getenv("COS_ENDPOINT", "https://s3.us-south.cloud-object-storage.appdomain.cloud"),
    )
    bucket = os.environ["COS_BUCKET"]
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = f"lineage-reports/{asset_id}/{ts}.json"
    client.put_object(Bucket=bucket, Key=key, Body=json.dumps(report, indent=2), ContentType="application/json")
    logger.info("Impact report archived: s3://%s/%s", bucket, key)
    return key


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command()
@click.option("--asset-id", required=True, help="watsonx.data Intelligence asset ID to analyse")
@click.option("--depth", default=5, show_default=True, help="Lineage graph traversal depth")
@click.option("--output", default=None, help="Save JSON report to file (optional)")
@click.option("--archive-cos", is_flag=True, help="Archive JSON report to IBM COS")
def cli(asset_id: str, depth: int, output: str | None, archive_cos: bool) -> None:
    """IBM watsonx.data Intelligence – downstream impact analysis for a data asset."""
    api_key = os.environ["IBM_API_KEY"]
    project_id = os.environ["WXDI_PROJECT_ID"]
    region = os.getenv("WXDI_REGION", "us-south")
    base_url = os.getenv("WXDI_BASE_URL", f"https://api.{region}.dai.cloud.ibm.com").rstrip("/")

    token = _get_token(api_key)

    click.echo(f"\nAnalysing downstream impact for asset: {asset_id}")
    impact = _get_impact(token, base_url, project_id, asset_id)
    graph = _get_graph(token, base_url, project_id, asset_id, depth)

    click.echo("\n── Downstream Dependencies ──────────────────────────")
    click.echo(_render_tree(impact))

    report = _build_report(asset_id, impact, graph)

    if output:
        with open(output, "w") as fh:
            json.dump(report, fh, indent=2)
        click.echo(f"\nReport saved to: {output}")

    if archive_cos:
        key = _archive_to_cos(report, asset_id)
        click.echo(f"Report archived to COS: {key}")


if __name__ == "__main__":
    cli()
