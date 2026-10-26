import logging
from uuid import UUID
from app.models.simulation.simulation_job import SimulationJob
from app.services.simulation_services import create_simulation_job, get_simulation_job

from fastapi import APIRouter
from fastapi import HTTPException
from app.schemas.simulation import SimulationRequest, SimulationJobResponse

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/simulation",
    tags=["Simulation"]
)

@router.post("", response_model=SimulationJobResponse, status_code=202)
def create_simulation(request: SimulationRequest) -> SimulationJob:
    return create_simulation_job(request)
    
@router.get("/{job_id}", response_model=SimulationJobResponse)
def get_simulation(job_id: UUID) -> SimulationJob:
    job = get_simulation_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail="Simulation job not found")
    
    return job

