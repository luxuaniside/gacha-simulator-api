from dataclasses import dataclass, field
from typing import Literal
import uuid
from app.models.banners_state import Banner

@dataclass
class Goal:
    goal_name: str
    item_name: str
    goal_banner: Banner
    item_type: Literal["character", "weapon"]
    item_rarity: Literal["five", "four"]
    item_target_count: int
    item_high_priority: bool
    goal_uuid: uuid.UUID = field(default_factory=uuid.uuid4)
