from dataclasses import dataclass

@dataclass
class SimulationResults:
    total_wishes_used: int = 0
    total_masterless_fortuna_earned: int = 0
    total_stardust_earned: int = 0
    total_starglitter_earned: int = 0

    total_limited_characterfrom_guarantee: int = 0
    total_limited_characterfrom_5050_won: int = 0
    total_limited_characterfrom_radiance: int = 0

    primary_weapon_from_50_50_won: int = 0
    secondary_weapon_from_50_50_won: int = 0
    primary_weapon_from_50_50_lost: int = 0
    secondary_weapon_from_50_50_lost: int = 0 

@dataclass
class SimulationOutput:
    finished_goals: dict
    simulation_time: float
    average_wishes_used: float
    average_masterless_starglitter_earned: float
    average_masterless_starglitter_refund: float
    average_masterless_fortuna_earned: float
    average_masterless_stardust_earned: float
    starting_wishes: int
    average_wishes_per_goal: dict[str, float]