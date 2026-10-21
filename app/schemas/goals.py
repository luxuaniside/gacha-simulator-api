from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID, uuid4
from app.models.banners_state import Banner
from app.models.goals_state import Goal

class CreateGoal(BaseModel):
    goal_name: str
    item_name: str = Field(min_length=1)
    goal_banner: Banner | None = None
    item_type: Literal["character", "weapon"]
    item_rarity: Literal["five", "four"]
    item_target_count: int
    item_high_priority: bool
    goal_uuid: UUID = Field(default_factory=uuid4)

class GoalValidationRequest(BaseModel):
    existing_goals: list[Goal] 
    new_goal: CreateGoal
    