from dataclasses import dataclass, field
from app.models.goals_state import Goal
from app.models.banners_state import Banner

@dataclass
class IterationState:
    """Stores the mutable state of a single simulation iteration.

    Tracks available resources, pity counters, guarantee states, owned items,
    banner mechanics, and goal progress throughout the simulation.

    Attributes:
        intertwined_fates (int): Number of Intertwined Fates available.
        masterless_starglitter (int): Amount of Masterless Starglitter available.

        five_character_pity (int): Consecutive character banner wishes since
            the last 5-star character.
        four_character_pity (int): Consecutive character banner wishes since
            the last 4-star item.
        five_weapon_pity (int): Consecutive weapon banner wishes since
            the last 5-star weapon.
        four_weapon_pity (int): Consecutive weapon banner wishes since
            the last 4-star item.

        five_character_guarantee (bool): Whether the next 5-star character
            banner item is guaranteed to be a featured item.
        four_character_guarantee (bool): Whether the next 4-star character
            banner item is guaranteed to be a featured item.
        five_weapon_guarantee (bool): Whether the next 5-star weapon banner
            item is guaranteed to be a featured item.
        four_weapon_guarantee (bool): Whether the next 4-star weapon banner
            item is guaranteed to be a featured item.

        epitomized_path (int): Current Epitomized Path progress.
        capturing_radiance (int): Current Capturing Radiance state.
        characters (dict[str, dict[str, int]]): Character ownership and
            duplicate-related data tracked by the simulation.
        weapons (dict[str, dict[str, int]]): Weapon ownership and
            duplicate-related data tracked by the simulation.
        goals (list[Goal]): Goals being pursued in this iteration.
        banners (list[Banner]): Banner configurations available in this iteration.

        current_iteration (int): Index or number of the current iteration.
        current_goal_index (int): Index of the goal currently being pursued.
        wishes_used_for_goal_counter (int): Wishes spent toward the current goal.
        wishes_spent_in_goal (dict[str, int]): Total wishes spent per completed
            or previously pursued goal, keyed by goal name.
    """
    
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

    # Special Banner Mechanics
    epitomized_path: int
    capturing_radiance: int

    # Inventory, goals and banners
    characters: dict[str, dict[str, int]]
    weapons: dict[str, dict[str, int]]
    goals: list[Goal] 
    banners: list[Banner]
    
    # Iteration
    current_iteration: int = 0
    current_goal_index: int = 0
    wishes_used_for_goal_counter: int = 0
    wishes_spent_in_goal: dict[str, int] = field(default_factory=dict)