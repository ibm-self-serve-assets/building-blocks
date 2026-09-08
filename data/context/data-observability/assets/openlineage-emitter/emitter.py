"""
IBM Databand OpenLineage Emitter
=================================
Emits OpenLineage run events to IBM Databand's Marquez-compatible HTTP transport.

IBM Databand (acquired by IBM in 2021) natively consumes the OpenLineage spec
(https://openlineage.io) via its /api/v1/lineage endpoint, allowing any pipeline
instrumented with OpenLineage to have its lineage tracked automatically.

Supported pipeline types in this emitter:
  - Python-based ETL scripts
  - IBM DataStage (via custom facets)
  - Apache Spark jobs
  - dbt runs (via dbt-ol integration)

Usage
-----
    python emitter.py \\
        --pipeline my_pipeline \\
        --job      transform_customers \\
        --inputs   "cos://bucket/raw/customers.parquet" \\
        --outputs  "cos://bucket/curated/customers.parquet" \\
        --run-id   $(python -c "import uuid; print(uuid.uuid4())")
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

import click
import requests
from dotenv import load_dotenv
from openlineage.client import OpenLineageClient
from openlineage.client.event_v2 import (
    Dataset,
    Job,
    Run,
    RunEvent,
    RunState,
)
from openlineage.client.facet_v2 import (
    job_type_job,
    parent_run,
    schema_dataset,
    source_code_location_job,
)
from openlineage.client.transport.http import HttpConfig, HttpTransport
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("openlineage_emitter")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _iam_bearer_token(api_key: str) -> str:
    """Exchange an IBM Cloud API key for a short-lived IAM bearer token."""
    resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _build_client() -> OpenLineageClient:
    """Build an OpenLineageClient pointing at IBM Databand's HTTP transport."""
    databand_url = os.environ["DATABAND_URL"].rstrip("/")
    static_token = os.getenv("DATABAND_ACCESS_TOKEN")

    if static_token:
        token = static_token
    else:
        token = _iam_bearer_token(os.environ["IBM_API_KEY"])

    transport = HttpTransport(
        HttpConfig(
            url=f"{databand_url}/api/v1/lineage",
            auth={"type": "bearer", "token": token},
            verify=True,
            timeout=30,
        )
    )
    return OpenLineageClient(transport=transport)


def _make_dataset(uri: str, fields: list[dict] | None = None) -> Dataset:
    """
    Construct an OpenLineage Dataset from a URI.
    URIs follow the convention used in IBM watsonx.data / COS:
      cos://<bucket>/<path>   → namespace=cos://<bucket>  name=<path>
      db2://<host>/<db>.<tbl> → namespace=db2://<host>    name=<db>.<tbl>
      iceberg://<catalog>/<schema>.<table>
    """
    if "://" in uri:
        scheme_rest = uri.split("://", 1)
        parts = scheme_rest[1].split("/", 1)
        namespace = f"{scheme_rest[0]}://{parts[0]}"
        name = parts[1] if len(parts) > 1 else ""
    else:
        namespace = "unknown"
        name = uri

    facets: dict[str, Any] = {}
    if fields:
        facets["schema"] = schema_dataset.SchemaDatasetFacet(
            fields=[
                schema_dataset.SchemaDatasetFacetFields(name=f["name"], type=f.get("type", "string"))
                for f in fields
            ]
        )

    return Dataset(namespace=namespace, name=name, facets=facets)


# ---------------------------------------------------------------------------
# Core emit functions
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def emit_start(
    client: OpenLineageClient,
    pipeline_name: str,
    job_name: str,
    run_id: str,
    inputs: list[str],
    outputs: list[str],
    parent_run_id: str | None = None,
) -> None:
    """Emit a START event to Databand."""
    run_facets: dict[str, Any] = {}
    if parent_run_id:
        run_facets["parent"] = parent_run.ParentRunFacet(
            run=parent_run.Run(runId=parent_run_id),
            job=parent_run.Job(namespace=pipeline_name, name=pipeline_name),
        )

    event = RunEvent(
        eventType=RunState.START,
        eventTime=datetime.now(timezone.utc).isoformat(),
        run=Run(runId=run_id, facets=run_facets),
        job=Job(
            namespace=pipeline_name,
            name=job_name,
            facets={
                "jobType": job_type_job.JobTypeJobFacet(
                    processingType="BATCH",
                    integration="PYTHON",
                    jobType="JOB",
                ),
            },
        ),
        inputs=[_make_dataset(uri) for uri in inputs],
        outputs=[_make_dataset(uri) for uri in outputs],
        producer=f"https://github.com/IBM/building-blocks/data/integration/data-observability",
    )
    client.emit(event)
    logger.info("START event emitted: pipeline=%s job=%s run=%s", pipeline_name, job_name, run_id)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def emit_complete(
    client: OpenLineageClient,
    pipeline_name: str,
    job_name: str,
    run_id: str,
    inputs: list[str],
    outputs: list[str],
    output_schema: list[dict] | None = None,
) -> None:
    """Emit a COMPLETE event to Databand."""
    event = RunEvent(
        eventType=RunState.COMPLETE,
        eventTime=datetime.now(timezone.utc).isoformat(),
        run=Run(runId=run_id),
        job=Job(namespace=pipeline_name, name=job_name),
        inputs=[_make_dataset(uri) for uri in inputs],
        outputs=[_make_dataset(uri, fields=output_schema) for uri in outputs],
        producer=f"https://github.com/IBM/building-blocks/data/integration/data-observability",
    )
    client.emit(event)
    logger.info("COMPLETE event emitted: pipeline=%s job=%s run=%s", pipeline_name, job_name, run_id)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def emit_fail(
    client: OpenLineageClient,
    pipeline_name: str,
    job_name: str,
    run_id: str,
    error_message: str,
) -> None:
    """Emit a FAIL event to Databand."""
    event = RunEvent(
        eventType=RunState.FAIL,
        eventTime=datetime.now(timezone.utc).isoformat(),
        run=Run(
            runId=run_id,
            facets={
                "errorMessage": {
                    "_producer": "openlineage-emitter",
                    "_schemaURL": "https://openlineage.io/spec/facets/1-0-0/ErrorMessageRunFacet.json",
                    "message": error_message,
                    "programmingLanguage": "PYTHON",
                }
            },
        ),
        job=Job(namespace=pipeline_name, name=job_name),
        inputs=[],
        outputs=[],
        producer="openlineage-emitter",
    )
    client.emit(event)
    logger.info("FAIL event emitted: pipeline=%s job=%s run=%s", pipeline_name, job_name, run_id)


# ---------------------------------------------------------------------------
# Context manager for convenient pipeline instrumentation
# ---------------------------------------------------------------------------

class PipelineRun:
    """
    Context manager that wraps a code block with OpenLineage START/COMPLETE/FAIL events.

    Example::

        with PipelineRun("etl_pipeline", "transform_orders",
                         inputs=["cos://raw-bucket/orders.csv"],
                         outputs=["cos://curated-bucket/orders.parquet"]) as run:
            # ... your ETL code here ...
            pass
    """

    def __init__(
        self,
        pipeline_name: str,
        job_name: str,
        inputs: list[str],
        outputs: list[str],
        output_schema: list[dict] | None = None,
        run_id: str | None = None,
        parent_run_id: str | None = None,
    ) -> None:
        self.pipeline_name = pipeline_name
        self.job_name = job_name
        self.inputs = inputs
        self.outputs = outputs
        self.output_schema = output_schema
        self.run_id = run_id or str(uuid.uuid4())
        self.parent_run_id = parent_run_id
        self._client = _build_client()

    def __enter__(self) -> "PipelineRun":
        emit_start(
            self._client,
            self.pipeline_name,
            self.job_name,
            self.run_id,
            self.inputs,
            self.outputs,
            self.parent_run_id,
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if exc_type is None:
            emit_complete(
                self._client,
                self.pipeline_name,
                self.job_name,
                self.run_id,
                self.inputs,
                self.outputs,
                self.output_schema,
            )
        else:
            emit_fail(
                self._client,
                self.pipeline_name,
                self.job_name,
                self.run_id,
                str(exc_val),
            )
        return False  # do not suppress exceptions


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------

@click.command()
@click.option("--pipeline", required=True, help="Pipeline / namespace name")
@click.option("--job", "job_name", required=True, help="Job name within the pipeline")
@click.option("--run-id", default=None, help="UUID for the run (auto-generated if omitted)")
@click.option("--inputs", multiple=True, help="Input dataset URIs (repeatable)")
@click.option("--outputs", multiple=True, help="Output dataset URIs (repeatable)")
@click.option(
    "--event-type",
    type=click.Choice(["START", "COMPLETE", "FAIL"], case_sensitive=False),
    default="COMPLETE",
    show_default=True,
    help="OpenLineage event type to emit",
)
@click.option("--error", default="", help="Error message (only for FAIL events)")
def cli(
    pipeline: str,
    job_name: str,
    run_id: str | None,
    inputs: tuple[str, ...],
    outputs: tuple[str, ...],
    event_type: str,
    error: str,
) -> None:
    """Emit an OpenLineage event to IBM Databand."""
    rid = run_id or str(uuid.uuid4())
    client = _build_client()

    if event_type.upper() == "START":
        emit_start(client, pipeline, job_name, rid, list(inputs), list(outputs))
    elif event_type.upper() == "COMPLETE":
        emit_complete(client, pipeline, job_name, rid, list(inputs), list(outputs))
    elif event_type.upper() == "FAIL":
        emit_fail(client, pipeline, job_name, rid, error or "Unknown error")

    click.echo(f"Event {event_type.upper()} emitted | run_id={rid}")


if __name__ == "__main__":
    cli()
