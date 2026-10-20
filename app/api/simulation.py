import logging
from threading import Lock
from time import monotonic
from uuid import uuid4

from fastapi import APIRouter
from fastapi import BackgroundTasks, HTTPException
from app.schemas.simulation import SimulationRequest
from app.simulation.simulation_instancing import instance_simulation

logger = logging.getLogger(__name__)
simulation_jobs: dict[str, dict] = {}
simulation_jobs_lock = Lock()
JOB_RETENTION_SECONDS = 60 * 60

router = APIRouter(
    prefix="/simulation",
    tags=["Simulation"]
)

def run_simulation_job(job_id: str, request: SimulationRequest) -> None:
    def report_progress(completed_iterations: int, total_iterations: int) -> None:
        with simulation_jobs_lock:
            job = simulation_jobs.get(job_id)
            if job is not None:
                job["completed_iterations"] = completed_iterations
                job["total_iterations"] = total_iterations
                job["status"] = "running"

    try:
        result = instance_simulation(request, report_progress)
    except Exception as error:
        logger.exception("Simulation job %s failed", job_id)
        with simulation_jobs_lock:
            job = simulation_jobs.get(job_id)
            if job is not None:
                job["status"] = "failed"
                job["error"] = str(error) or "Simulation failed unexpectedly."
                job["completed_at"] = monotonic()
        return

    with simulation_jobs_lock:
        job = simulation_jobs.get(job_id)
        if job is not None:
            job["status"] = "completed"
            job["completed_iterations"] = job["total_iterations"]
            job["result"] = result
            job["completed_at"] = monotonic()


def clean_old_simulation_jobs() -> None:
    expiration_time = monotonic() - JOB_RETENTION_SECONDS
    with simulation_jobs_lock:
        expired_jobs = [
            job_id
            for job_id, job in simulation_jobs.items()
            if (
                job.get("completed_at") is not None
                and job["completed_at"] < expiration_time
            )
        ]
        for job_id in expired_jobs:
            del simulation_jobs[job_id]


@router.post("")
async def simulate(
    request: SimulationRequest,
    background_tasks: BackgroundTasks,
):
    clean_old_simulation_jobs()
    job_id = str(uuid4())
    total_iterations = request.simulation_settings.iteration_count
    with simulation_jobs_lock:
        simulation_jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "completed_iterations": 0,
            "total_iterations": total_iterations,
            "result": None,
            "error": None,
            "created_at": monotonic(),
        }

    background_tasks.add_task(run_simulation_job, job_id, request)
    return {
        "job_id": job_id,
        "status": "queued",
        "completed_iterations": 0,
        "total_iterations": total_iterations,
    }


@router.get("/{job_id}")
async def get_simulation_status(job_id: str):
    with simulation_jobs_lock:
        job = simulation_jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Simulation job not found.")
        return {
            key: value
            for key, value in job.items()
            if key not in {"created_at", "completed_at"}
        }