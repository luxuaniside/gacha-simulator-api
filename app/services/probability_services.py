import logging
import random

from app.models.simulation_settings import SimulationSettings
from app.models.simulation_settings import DebugState
from app.models.iteration_state import WishState

logger = logging.getLogger(__name__)

def get_chance(iteration_state: WishState, simulation_settings: SimulationSettings, debug_state: DebugState, item_type: str, item_rarity: str, pity: int) -> float:
    if item_type == "character" and item_rarity == "five":
        chance = simulation_settings.five_characterchance
        softpity = simulation_settings.five_charactersoftpity

    if item_type == "character" and item_rarity == "four":
        chance = simulation_settings.four_characterchance
        softpity = simulation_settings.four_charactersoftpity

    if item_type == "weapon" and item_rarity == "five":
        chance = simulation_settings.five_weapon_chance
        softpity = simulation_settings.five_weapon_softpity

    if item_type == "weapon" and item_rarity == "four":
        chance = simulation_settings.four_weapon_chance
        softpity = simulation_settings.four_weapon_softpity

    if pity >= softpity:
        chance = min(chance + (pity - softpity) * chance * 10, 1)

    if debug_state.debug_get_chance:
        logger.debug(f"ITERATION {iteration_state.current_iteration} | {item_type=} {item_rarity=} {pity=} {chance=:.2%} {softpity=}")
    
    return chance
 
def capturing_radiance(simulation_settings: SimulationSettings, capturing_radiance):
    return random.random() < simulation_settings.capturing_radiance_chances[capturing_radiance]

    
    