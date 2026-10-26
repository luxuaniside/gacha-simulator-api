from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID, uuid4
from app.models.banners_state import Banner
from app.models.goals_state import Goal
class CreateGoal(BaseModel):
    """Schema for creating a simulation goal."""

    goal_name: str = Field(
        description="Name identifying the goal."
    )
    item_name: str = Field(
        min_length=1,
        description="Name of the character or weapon to obtain."
    )
    goal_banner: Banner = Field(
        description="Banner associated with the goa"
    )
    item_type: Literal["character", "weapon"] = Field(
        description="Type of item the goal targets."
    )
    item_rarity: Literal["five", "four"] = Field(
        description="Rarity of the target item: five-star or four-star."
    )
    item_target_count: int = Field(
        description="Number of copies of the target item to obtain."
    )
    item_high_priority: bool = Field(
        description="Whether or not the item is attempted to pull for, or simply tracked."
    )
    goal_uuid: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier automatically generated for the goal."
    )


class GoalValidationRequest(BaseModel):
    """Request schema for validating a new goal against existing goals."""

    existing_goals: list[Goal] = Field(
        description="Goals already present in the simulation, "
                    "used to validate the new goal."
    )
    new_goal: CreateGoal = Field(
        description="Goal to validate against the existing goals."
    )

