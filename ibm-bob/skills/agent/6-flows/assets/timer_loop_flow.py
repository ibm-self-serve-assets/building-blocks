"""
timer_loop_flow.py — Polling loop with a timer node.

Demonstrates:
- aflow.loop() with a Python evaluator expression
- while_loop.timer() for delays between poll attempts
- private_schema to track attempt count
- Combining a one-shot tool node with a polling loop

Flow:  START
         → start_job (tool — kicks off async job, returns job_id)
         → poll_loop [while attempts < 10 and not done]
             → check_status (tool — checks job status)
             → wait_2_sec (timer — 2000 ms delay)
         → END
"""

from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END


# ── Schemas ───────────────────────────────────────────────────────────────────

class JobRequest(BaseModel):
    payload: str = Field(description="Job payload to submit")

class AttemptState(BaseModel):
    attempts: int = Field(default=0, description="Number of poll attempts so far")

class JobStatus(BaseModel):
    done:   bool = Field(default=False, description="Whether the job is complete")
    result: str  = Field(default="",    description="Job result when done")

class JobOutput(BaseModel):
    result: str = Field(description="Final job result")


# ── Tool stubs ────────────────────────────────────────────────────────────────

def start_async_job(payload: str) -> dict:
    """Start an async job and return a job ID."""
    import hashlib
    job_id = hashlib.md5(payload.encode()).hexdigest()[:8]
    print(f"Started job: {job_id}")
    return {"job_id": job_id}

def check_job_status(job_id: str, attempts: int) -> dict:
    """Poll the status of the job. Simulates completion after 3 attempts."""
    done = attempts >= 3
    print(f"Attempt {attempts}: job {job_id} done={done}")
    return {"done": done, "result": f"Result for {job_id}" if done else ""}


# ── Flow ──────────────────────────────────────────────────────────────────────

@flow(
    name="polling_loop_flow",
    display_name="Async Job Polling Flow",
    description="Start an async job then poll until complete, with a 2-second delay between polls.",
    input_schema=JobRequest,
    output_schema=JobOutput
)
def build_polling_loop_flow(aflow: Flow) -> Flow:

    # ── Step 1: Submit the job ────────────────────────────────────────────────
    start_node = aflow.tool(start_async_job, input_schema=JobRequest)

    # ── Step 2: Poll loop — runs while job is not done and under 10 attempts ──
    poll_loop = aflow.loop(
        evaluator=(
            "not flow.nodes['check_status'].output.done "
            "and (parent.input.attempts.attempts or 0) < 10"
        ),
        input_schema=AttemptState,
        output_schema=JobStatus
    )

    check_node = poll_loop.tool(
        check_job_status,
        name="check_status",
        output_schema=JobStatus
    )

    # Timer: wait 2 seconds between poll attempts
    wait_node = poll_loop.timer(
        name="wait_2_sec",
        delay=2000,
        display_name="Wait 2 seconds"
    )

    poll_loop.sequence(START, check_node, wait_node, END)

    # ── Wire main flow ────────────────────────────────────────────────────────
    aflow.sequence(START, start_node, poll_loop, END)

    return aflow
