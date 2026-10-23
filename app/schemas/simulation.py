from pydantic import BaseModel, Field
from app.models.banners_state import Banner
from app.models.goals_state import Goal
from app.schemas.inventory import Characters, Pity, Resources
from typing import Literal
from uuid import UUID
from app.models.simulation.simulation_results import SimulationOutput

class SimulationSettings(BaseModel):
    iteration_count: int = Field(ge=1, le=50000)
    starglitter_refund: bool
    continue_after_goals_are_finished: bool

class SimulationRequest(BaseModel):
    resources: Resources
    pity: Pity
    goals: list[Goal] = Field(min_length=1)
    banners: list[Banner] = Field(min_length=1)
    simulation_settings: SimulationSettings
    characters: Characters
    
class SimulationJobResponse(BaseModel):
    job_id: UUID
    status: Literal["pending", "running", "completed", "failed"]
    completed_iterations: int
    total_iterations: int
    result: SimulationOutput | None = None
    error: str | None = None