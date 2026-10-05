from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from app.schemas.simulation import SimulationRequest
from app.services.simulation_services import instance_simulation


router = APIRouter(
    prefix="/simulation",
    tags=["Simulation"]
)

@router.post("")
async def simulate(request: SimulationRequest):
    result = await run_in_threadpool(
        instance_simulation,
        request
    )

    return result