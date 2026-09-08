#!/usr/bin/env python3
"""
UDI Ingest — Part 2 of 2

Reads the config file produced by setup.py and triggers a new run of the
already-created UDI flow. Polls until the run reaches a terminal state and
prints execution logs on failure. Run as many times as needed — once per
ingestion cycle, on a schedule, or whenever new documents are added to COS.

Prerequisite:
  Run setup.py first to produce udi_config.json.

Usage:
  Linux / macOS:
      export IBM_CLOUD_API_KEY="<key>"
      python3 scripts/ingest.py

  Windows cmd:
      set IBM_CLOUD_API_KEY=<key>
      python scripts\\ingest.py

Optional env vars:
  UDI_CONFIG        Path to the config file written by setup.py  (default: udi_config.json)
  WATSONX_ENV       UDI environment override                     (default: value from config)
  POLL_INTERVAL     Seconds between status polls                 (default: 20)
  POLL_TIMEOUT      Max seconds to wait for completion           (default: 1800)
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging — force UTF-8 so checkmark chars don't crash on Windows cp1252
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    handlers=[
        logging.StreamHandler(open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)),
        logging.FileHandler("udi_ingest.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        log.error(f"Required environment variable not set: {name}")
        sys.exit(1)
    return val


API_KEY       = _require_env("IBM_CLOUD_API_KEY")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "20"))
POLL_TIMEOUT  = int(os.environ.get("POLL_TIMEOUT",  "1800"))
# Default: read udi_config.json from the scripts/ directory (where setup.py wrote it)
CONFIG_FILE = os.environ.get("UDI_CONFIG", str(Path(__file__).parent / "udi_config.json"))


def load_config() -> dict:
    """Load udi_config.json written by setup.py."""
    path = Path(CONFIG_FILE)
    if not path.exists():
        log.error(f"Config file not found: {CONFIG_FILE}")
        log.error("Run setup.py first to create the config file.")
        sys.exit(1)
    config = json.loads(path.read_text(encoding="utf-8"))
    required_keys = ["project_id", "flow_id", "job_id", "watsonx_url", "watsonx_env"]
    missing = [k for k in required_keys if not config.get(k)]
    if missing:
        log.error(f"Config file is missing required keys: {missing}")
        log.error("Re-run setup.py to regenerate a valid config file.")
        sys.exit(1)
    return config


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    log.info("=" * 70)
    log.info("UDI Ingest — Part 2 of 2")
    log.info("=" * 70)

    config = load_config()

    project_id  = config["project_id"]
    flow_id     = config["flow_id"]
    job_id      = config["job_id"]
    watsonx_url = config["watsonx_url"]
    watsonx_env = os.environ.get("WATSONX_ENV", config["watsonx_env"]).strip()

    log.info(f"  Config file  : {CONFIG_FILE}")
    log.info(f"  Project ID   : {project_id}")
    log.info(f"  Flow ID      : {flow_id}")
    log.info(f"  Job ID       : {job_id}")
    log.info(f"  Environment  : {watsonx_env}")
    log.info(f"  Base URL     : {watsonx_url}")
    log.info(f"  Poll interval: {POLL_INTERVAL}s  |  Timeout: {POLL_TIMEOUT}s")
    log.info("")

    try:
        from udi import UDIClient
        from udi.flows import Flow
        from udi.constants import JobStatusConstants
    except ImportError:
        log.error("ibm-udi package not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    try:
        log.info("[1/3] Initializing UDI client...")
        uc = UDIClient(config={
            "base_url":   watsonx_url,
            "project_id": project_id,
            "api_key":    API_KEY,
            "env":        watsonx_env,
        })
        log.info("✓ UDI client initialized")

        log.info("[2/3] Starting flow run...")
        flow = Flow(uc)
        flow.flow_id = flow_id
        flow.job_id  = job_id
        flow.run()
        run_id = flow.job_run_id
        log.info(f"✓ Flow run started — run_id: {run_id}")

        # Record run start in config
        run_record = {
            "run_id":    run_id,
            "timestamp": datetime.now().isoformat(),
            "status":    "started",
        }
        config.setdefault("runs", []).append(run_record)
        Path(CONFIG_FILE).write_text(json.dumps(config, indent=2), encoding="utf-8")

        log.info(f"[3/3] Polling run status (interval={POLL_INTERVAL}s, timeout={POLL_TIMEOUT}s)...")
        try:
            final_status = flow.poll_flow_status(
                flow_id=flow_id,
                job_run_id=run_id,
                interval=POLL_INTERVAL,
                timeout=POLL_TIMEOUT,
            )
        except TimeoutError:
            log.error(f"✗ Polling timed out after {POLL_TIMEOUT}s — run is still in progress")
            log.error(f"  Check the watsonx console: https://dataplatform.cloud.ibm.com/projects/{project_id}/assets")
            # Update the run record with timeout status
            run_record["status"] = "timeout"
            Path(CONFIG_FILE).write_text(json.dumps(config, indent=2), encoding="utf-8")
            return 1

        # Update run record with final status
        run_record["status"] = final_status
        run_record["completed_at"] = datetime.now().isoformat()
        Path(CONFIG_FILE).write_text(json.dumps(config, indent=2), encoding="utf-8")

        # Determine success / failure
        success_states = {
            JobStatusConstants.COMPLETED,
            JobStatusConstants.COMPLETED_WITH_WARNINGS,
            JobStatusConstants.COMPLETED_WITH_ERRORS,
        }
        failed_states = {
            JobStatusConstants.FAILED,
            JobStatusConstants.CANCELED,
        }

        log.info("")
        log.info("=" * 70)

        if final_status == JobStatusConstants.COMPLETED:
            log.info(f"✓ Ingestion run COMPLETED successfully")
            log.info("=" * 70)
            log.info(f"  Run ID : {run_id}")
            log.info("=" * 70)
            return 0

        elif final_status in success_states:
            # CompletedWithWarnings or CompletedWithErrors — fetch logs so we can diagnose
            log.warning(f"⚠ Ingestion run finished with status: {final_status} — fetching logs...")
            log.info("=" * 70)
            try:
                logs = flow.logs(job_id=job_id, job_run_id=run_id)
                log.warning("--- Execution Logs ---")
                log.warning(json.dumps(logs, indent=2))
                log.warning("--- End Logs ---")
            except Exception as log_err:
                log.warning(f"Could not retrieve logs: {log_err}")
            log.warning(f"  Run ID : {run_id}")
            log.info("=" * 70)
            # CompletedWithErrors still means data was partially written — treat as success for now
            return 0

        elif final_status in failed_states:
            log.error(f"✗ Ingestion run {final_status.upper()} — fetching execution logs...")
            log.info("=" * 70)
            try:
                logs = flow.logs(job_id=job_id, job_run_id=run_id)
                log.error("--- Execution Logs ---")
                log.error(json.dumps(logs, indent=2))
                log.error("--- End Logs ---")
            except Exception as log_err:
                log.warning(f"Could not retrieve logs: {log_err}")
            return 1

        else:
            log.warning(f"Run ended with unexpected status: {final_status}")
            return 1

    except Exception as e:
        log.error(f"Ingestion failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
