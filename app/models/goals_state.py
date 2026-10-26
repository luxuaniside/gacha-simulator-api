from dataclasses import dataclass, field
from typing import Literal
import uuid
from app.models.banners_state import Banner

@dataclass
class Goal:
    """Represents a simulation goal for obtaining a specific item.

    Attributes:
        goal_name (str): Name assigned to the goal.
        item_name (str): Name of the character or weapon to obtain.
        goal_banner (Banner): Banner associated with the goal.
        item_type (Literal["character", "weapon"]): Type of item to obtain.
        item_rarity (Literal["five", "four"]): Rarity of the target item.
        item_target_count (int): Number of copies to obtain to complete the goal.
        item_high_priority (bool): Whether the goal has high priority during
            simulation.
        goal_uuid (uuid.UUID): Unique identifier generated automatically
            when the goal is created.
    """

    goal_name: str
    item_name: str
    goal_banner: Banner
    item_type: Literal["character", "weapon"]
    item_rarity: Literal["five", "four"]
    item_target_count: int
    item_high_priority: bool
    goal_uuid: uuid.UUID = field(default_factory=uuid.uuid4)