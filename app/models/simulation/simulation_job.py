from dataclasses import dataclass
from app.models.simulation.simulation_results import SimulationOutput
from app.schemas.simulation import SimulationRequest
from typing import Literal
from uuid import UUID
from time import monotonic
@dataclass
class SimulationJob:
    job_id: UUID
    status: Literal["pending", "running", "completed", "failed"]
    completed_iterations: int
    total_iterations: int
    request: SimulationRequest
    result: SimulationOutput | None = None
    error: str | None = None
    time_of_job_schedule: float = monotonic()