import logging
import random

from app.models.simulation_settings import SimulationSettings
from app.models.simulation_settings import DebugState
from app.models.iteration_state import IterationState

logger = logging.getLogger(__name__)

def get_chance(iteration_state: IterationState, simulation_settings: SimulationSettings, debug_state: DebugState, item_type: str, item_rarity: str, pity: int) -> float:   
    """
    Calculate the drop probability for an item based on its type, rarity, and current pity.

    The probability is determined by the item's base drop rate and the corresponding soft pity settings. 
    Once the soft pity threshold is exceeded, the probability  increases with each subsequent wish until it reaches 100%.

    The probability increase per wish defaults to 10 times the item's base drop rate. 
    All pity thresholds and probability settings can be customized through simulation_settings.

    Default pity thresholds:
    - Five-star character: soft pity at 73, hard pity at 90.
    - Four-star character: soft pity at 8, hard pity at 10.
    - Five-star weapon: soft pity at 62, hard pity at 77.
    - Four-star weapon: soft pity at 7, hard pity at 9.

    ## IMPORTANT!
    These thresholds describe the simulator's default implementation and may differ from the values advertised by HoYoverse. 
    These are the values studied by the community.
    Args:
        iteration_state (IterationState): Current state of the simulation.
        simulation_settings (SimulationSettings): Pity thresholds and probability settings used for the simulation.
        debug_state (DebugState): Debugging and logging configuration.
        item_type (Literal["character", "weapon"]): Item category. Must be "character" or "weapon".
        item_rarity (str): Item rarity. Must be "five" or "four".
        pity (int): Number of consecutive wishes without obtaining an item of the specified rarity.

    Returns:
        chance (float): Probability of obtaining an item of the specified type and rarity, expressed as a value between 0.0 and 1.0.
    """
    if item_type == "character" and item_rarity == "five":
        chance = simulation_settings.five_character_chance
        softpity_threshold = simulation_settings.five_character_softpity

    if item_type == "character" and item_rarity == "four":
        chance = simulation_settings.four_character_chance
        softpity_threshold = simulation_settings.four_character_softpity

    if item_type == "weapon" and item_rarity == "five":
        chance = simulation_settings.five_weapon_chance
        softpity_threshold = simulation_settings.five_weapon_softpity

    if item_type == "weapon" and item_rarity == "four":
        chance = simulation_settings.four_weapon_chance
        softpity_threshold = simulation_settings.four_weapon_softpity

    if pity >= softpity_threshold:
        pity_past_threshold = (pity - softpity_threshold)
        softpity_increment = pity_past_threshold * chance * simulation_settings.softpity_increment
        chance = min(chance + softpity_increment, 1) # Hard Pity at 1

    if debug_state.debug_get_chance:
        logger.debug(f"ITERATION {iteration_state.current_iteration} | {item_type=} {item_rarity=} {pity=} {chance=:.2%} {softpity_threshold=}")
    
    return chance
 
def capturing_radiance(simulation_settings: SimulationSettings, capturing_radiance: int) -> bool:
    """Attempts to trigger Capturing Radiance.
    There is no fully agreed upon or officially advertised way of how Capturing Radiance works. 
    This model simply attempts to simulate the advertised 5% on average increase Hoyoverse says. 

    Args:
        simulation_settings (SimulationSettings): Capturing Radiance settings.
        capturing_radiance (int): Capturing Radiance stacks.

    Returns:
        bool: Capturing radiance was triggered or not.
    """
    return random.random() < simulation_settings.capturing_radiance_chances[capturing_radiance]

    
    