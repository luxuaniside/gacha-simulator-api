import copy
from dataclasses import dataclass, field
from app.models.goals_state import Goal
from app.models.banners_state import Banner

@dataclass
class WishState:
    # Resources
    intertwined_fates: int
    masterless_starglitter: int

    # Pity
    five_character_pity: int
    four_character_pity: int
    five_weapon_pity: int
    four_weapon_pity: int

    # Guarantees
    five_character_guarantee: bool
    four_character_guarantee: bool
    five_weapon_guarantee: bool
    four_weapon_guarantee: bool

    # Banner State
    epitomized_path: int
    capturing_radiance: int
    characters: dict[str, dict[str, int]]
    weapons: dict[str, dict]
    goals: list[Goal] 
    banners: list[Banner]
    
    # Iteration
    current_iteration: int = 0
    current_goal_index: int = 0
    wishes_used_for_goal_counter: int = 0
    wishes_spent_in_goal: dict[str, int] = field(default_factory=dict)