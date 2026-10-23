from dataclasses import dataclass
from typing import ClassVar

@dataclass
class SimulationSettings:
    # runtime / control
    iterations: int
    starglitter_refund: bool
    continue_after_goals_are_finished: bool 
    simulation_timeout_seconds: int = 120 #Unused

    # probabilities of dropping an item
    five_character_chance: float = 0.006
    four_character_chance: float = 0.051
    five_weapon_chance: float = 0.007
    four_weapon_chance: float = 0.06

    # probabilities of said items being limited
    five_character_limited_chance: float = 0.5
    four_character_limited_chance: float = 0.5
    five_weapon_limited_chance: float = 0.75
    four_weapon_limited_chance: float = 0.75
    five_primary_weapon_chance: float = 0.5

    #chances of off-banner item being character or wpn dependent on the banner
    character_banner_off_banner_four_star_character_chance: float = 0.15
    character_banner_off_banner_four_star_weapon_chance: float = 0.85
    weapon_banner_off_banner_four_star_character_chance: float = 0.925
    weapon_banner_off_banner_four_star_weapon_chance: float = 0.075
    
    #radiance chances
    capturing_radiance_chances: ClassVar[dict[int, float]] = {
        0: 0,
        1: 0,
        2: 0.1,
        3: 1,
    }
    
    # soft pity
    five_character_softpity: int = 73
    four_character_softpity: int = 8
    five_weapon_softpity: int = 62
    four_weapon_softpity: int = 7
    softpity_increment: int = 10

    # economy
    five_character_unmax_starglitter: int = 10
    four_character_unmax_starglitter: int = 2    
    five_character_max_starglitter: int = 25
    four_character_max_starglitter: int = 5
    five_weapon_starglitter: int = 10
    four_weapon_starglitter: int = 2
    five_character_max_fortuna: int = 1
    three_weapon_stardust: int = 15
    starglitter_to_wish_cost: int = 5
    primogem_to_wish_cost: int = 160    

@dataclass
class DebugState:
    log_level: str = "DEBUG"
    debug_current_goal: bool = False
    debug_get_chance: bool = False
    debug_starglitter_refund: bool = False
    debug_starglitter_income_info: bool = False
    debug_item_pulled_info: bool = False
    debug_alert_all_goals_are_finished: bool = False
    debug_process_item: bool = False
    