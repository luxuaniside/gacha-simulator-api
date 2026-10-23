import logging
import random 

from app.models.iteration_state import IterationState
from app.models.simulation.simulation_settings import SimulationSettings, DebugState
from app.models.simulation.simulation_results import SimulationResults
from app.models.goals_state import Goal
from app.models.banners_state import Banner

from app.services.probability_services import capturing_radiance

logger = logging.getLogger(__name__)

# Item lists necessary for the engine. Missing ones aren't necessary for the backend.
STANDARD_FIVE_STAR_CHARACTER_LIST = [
    "Jean",
    "Diluc",
    "Qiqi",
    "Mona",
    "Keqing",
    "Tighnari",
    "Dehya",
    "Yumemizuki Mizuki"
]

STANDARD_FOUR_STAR_CHARACTER_LIST = [
    "Sucrose",
    "Chongyun",
    "Noelle",
    "Fischl",
    "Bennett",
    "Ningguang",
    "Xingqiu",
    "Beidou",
    "Xiangling",
    "Razor",
    "Barbara",
    "Diona",
    "Xinyan",
    "Rosaria",
    "Yanfei",
    "Sayu",
    "Kujou Sara",
    "Thoma",
    "Gorou",
    "Yun Jin",
    "Kuki Shinobu",
    "Shikanoin Heizou",
    "Collei",
    "Dori",
    "Candace",
    "Layla",
    "Faruzan",
    "Yaoyao",
    "Mika",
    "Kaveh",
    "Kirara",
    "Lynette",
    "Freminet",
    "Charlotte",
    "Chevreuse",
    "Gaming",
    "Sethos",
    "Kachina",
    "Ororon",
    "Lan Yan",
    "Iansan",
    "Ifa",
    "Dahlia",
    "Aino",
    "Jahoda",
    "Illuga",
    "Prune",
    "Alyosha",
    "Valeriy",
]

STANDARD_FIVE_STAR_WEAPON_LIST = [
    "Aquila Favonia",
    "Skyward Blade",
    "Skyward Pride",
    "Wolf's Gravestone",
    "Primordial Jade Winged-Spear",
    "Skyward Atlas",
    "Lost Prayer to the Sacred Winds",
    "Skyward Harp",
    "Amos' Bow"
]

STANDARD_FOUR_STAR_WEAPON_LIST = [
    "Dragon's Bane",
    "Eye of Perception",
    "Favonius Codex",
    "Favonius Greatsword",
    "Favonius Lance",
    "Favonius Sword",
    "Favonius Warbow",
    "Lion's Roar",
    "Rainslasher",
    "Rust",
    "Sacrificial Bow",
    "Sacrificial Fragments",
    "Sacrificial Greatsword",
    "Sacrificial Sword",
    "The Bell",
    "The Flute",
    "The Stringless",
    "The Widsith" 
]


def get_item(iteration_state: IterationState, simulation_settings: SimulationSettings, debug_state: DebugState, goal: Goal, item_rarity: str) -> tuple[str, str]:    
    """Determine which drop to grant based on the item rarity and the simulation goal.

    Args:
        iteration_state (IterationState): Current state of the simulation.
        simulation_settings (SimulationSettings): Settings chosen for the simulation. 
        debug_state (DebugState): Options for debugging and logging.
        goal (Goal): Target item configuration determining the active banner type.
        item_rarity (str): The rarity of the item to drop. Values must be "five" or "four".
            
    Returns:
        tuple[str, str]: A tuple containing two strings:
            - item_dropped: The name of the dropped item.
            - item_type: The category of the item ("character" or "weapon").
    """
    if item_rarity == "five" and goal.item_type == "character":
        item_dropped, item_type, item_drop_method = character_banner_get_five_character(iteration_state, simulation_settings, goal)
        
    if item_rarity == "four" and goal.item_type == "character":
        item_dropped, item_type, item_drop_method = character_banner_get_four_item(iteration_state, simulation_settings, goal)

    if item_rarity == "five" and goal.item_type == "weapon":
        item_dropped, item_type, item_drop_method = weapon_banner_get_five_weapon(iteration_state, simulation_settings, goal)

    if item_rarity == "four" and goal.item_type == "weapon":
        item_dropped, item_type, item_drop_method = weapon_banner_get_four_item(iteration_state, simulation_settings, goal)

    # Debug
    if debug_state.debug_item_pulled_info:
        logger.debug(f"ITERATION {iteration_state.current_iteration} | {item_dropped=} {item_drop_method=}")
    
    return item_dropped, item_type

def handle_capturing_radiance_points(iteration_state: IterationState, action: str) -> None:
    """Update Capturing Radiance points based on the wish outcome.

    Capturing Radiance Rules
        - "WON": Winning a 50/50 removes one point.
        - "LOST": Losing a 50/50 grants one point.
        - "RADIANCE": Triggering Radiance resets the counter to one.
        - The counter is capped between 0 and 3.

    Args:
        iteration_state (IterationState): Current state of the simulation.
        action (str): Outcome of the character wish. Accepted values are
            "WON", "LOST", and "RADIANCE".
    Raises:
        ValueError: Happens when action is not "WON", "LOST", "RADIANCE".

    """
    if action == "WON":
        iteration_state.capturing_radiance = max(iteration_state.capturing_radiance - 1, 0)
    elif action == "LOST":
        iteration_state.capturing_radiance = min(iteration_state.capturing_radiance + 1, 3)
    elif action == "RADIANCE": 
        iteration_state.capturing_radiance = 1
    else:
        raise ValueError(f"Invalid Capturing Radiance action: {action}")

def handle_epitomized_path_points(iteration_state: IterationState, action: str) -> None:
    """Update Epitomized Path based on the wish outcome.

    Epitomized Path Rules: 
        - "LOST": Losing to a standard or non "epitomized" (in this program, known as secondary) weapon grants one point.
        - "WON" / "EPITOMIZED": Getting the epitomized (in this program, known as primary) weapon through chance or guarantee sets the point back to 0.
    Args:
        iteration_state (IterationState): Current state of the simulation.
        action (str): Outcome of the weapon wish. Accepted values are
            "WON", "LOST", and "EPITOMIZED".
    Raises:
        ValueError: Happens when action is not "WON", "LOST", "EPITOMIZED"
    """    

    if action == "WON" or action == "EPITOMIZED":
        iteration_state.epitomized_path = 0
    elif action == "LOST":
        iteration_state.epitomized_path = 1
    else:
        raise ValueError(f"Invalid Epitomized Path action: {action}")
    
def character_banner_get_five_character(iteration_state: IterationState, simulation_settings: SimulationSettings, goal: Goal) -> tuple[str, str, str]:
    """Determine the five-star character obtained.

    Character Banner five-star drop rules:
        - A guarantee grants a limited five-star character and consumes the guarantee without affecting Capturing Radiance.
        - Winning the 50/50 grants a limited five-star character and removes one Capturing Radiance point, down to a minimum of zero. 
        - Triggering Capturing Radiance grants a limited five-star character and resets Capturing Radiance to one point.
        - Losing the 50/50 grants a standard five-star character, activates the guarantee for the next five-star character, and adds
          one Capturing Radiance point, up to a maximum of three.

    Some values presented above are the default, and can be modified in simulation_settings.

    Args:
        iteration_state (IterationState): Current state of the simulation.
        simulation_settings (SimulationSettings): Settings chosen for the simulation. 
        goal (Goal): Target item configuration determining the active banner type.

    Returns:
        tuple[str, str, str]: A tuple containing three strings:
            - item_dropped: The name of the dropped item.
            - item_type: Category of the item ("character").
            - item_drop_method: Message for logs.
    """

    item_type = "character" #Always a character

    #Case: Limited five star is guaranteed.
    if iteration_state.five_character_guarantee:
        iteration_state.five_character_guarantee = False
        item_dropped = goal.goal_banner.banner_five_item_primary
        item_drop_method = F"GUARANTEE (Now {iteration_state.capturing_radiance} RADIANCE)"
     
    #Case: Capturing Radiance Trigger
    elif capturing_radiance(simulation_settings, iteration_state.capturing_radiance):
        handle_capturing_radiance_points(iteration_state, "RADIANCE")
        item_dropped = goal.goal_banner.banner_five_item_primary
        item_drop_method = f"RADIANCE (At {iteration_state.capturing_radiance})"

    #Case: Won limited character
    elif random.random() < simulation_settings.five_character_limited_chance:
        handle_capturing_radiance_points(iteration_state, "WON")
        item_dropped = goal.goal_banner.banner_five_item_primary
        item_drop_method = f"WON LIMITED ROLL (Now {iteration_state.capturing_radiance} RADIANCE)"
    
    #Case: Lost limited character
    else:
        iteration_state.five_character_guarantee = True
        handle_capturing_radiance_points(iteration_state, "LOST")
        item_dropped = get_off_banner_five_character() 
        item_drop_method = f"LOST LIMITED ROLL (Now {iteration_state.capturing_radiance} RADIANCE)"
   
    return item_dropped, item_type, item_drop_method

def character_banner_get_four_item(iteration_state: IterationState, simulation_settings: SimulationSettings, goal: Goal) -> tuple[str, str, str]:
    """Determine the four-star character or weapon obtained.
    
    * Character Banner four-star drop rules:
        * A guarantee grants a randomly selected limited four-star character from the three on banner and consumes it.
        * Winning the 50/50 grants a randomly selected limited four-star character from the three on banner.
        * Losing the 50/50 has a variety of sub-mechanics:
            - Items within the banner cannot be obtained through the standard items pool.
            - There is an 85% chance the item will be a four-star weapon, otherwise, a four-star character will be selected.
            - Losing the 50/50 grants you a guarantee.
        
    Some values presented above are the default, and can be modified in simulation_settings.
        
    Args:
        iteration_state (IterationState): Current state of the simulation.
        simulation_settings (SimulationSettings): Settings chosen for the simulation. 
        goal (Goal): Target item configuration determining the active banner type.

    Returns:
        tuple[str, str, str]: A tuple containing three strings:
            - item_dropped: The name of the dropped item.
            - item_type: Category of the item ("character" or "weapon").
            - item_drop_method: Message for logs.
    """

    off_banner_character_chance = simulation_settings.character_banner_off_banner_four_star_character_chance
    off_banner_weapon_chance = simulation_settings.character_banner_off_banner_four_star_weapon_chance
    off_banner_roll = random.random()
    item_type = "character"

    #Case: Guaranteed
    if iteration_state.four_character_guarantee:
        iteration_state.four_character_guarantee = False
        item_dropped = random.choice(goal.goal_banner.banner_four_items)
        item_drop_method = f"GUARANTEED"
    
    #Case: Won limited character
    elif random.random() < simulation_settings.four_character_limited_chance:
        item_dropped = random.choice(goal.goal_banner.banner_four_items)
        item_drop_method = f"WON LIMITED ROLL"

    #Case: Lost limited character roll. Got off-banner character. 
    elif off_banner_roll < off_banner_character_chance:
        iteration_state.four_character_guarantee = True
        item_dropped = get_off_banner_four_character(goal.goal_banner)
        item_drop_method = f"LOST LIMITED ROLL, GOT OFF BANNER CHARACTER in CHARACTER BANNER"    

    #Case: Lost limited character roll. Got off-banner weapon. 
    elif off_banner_roll < off_banner_character_chance + off_banner_weapon_chance:
        item_dropped = get_off_banner_four_weapon(goal.goal_banner)
        iteration_state.four_character_guarantee = True
        item_drop_method = f"LOST LIMITED ROLL, GOT OFF BANNER WEAPON in CHARACTER BANNER" 
        item_type = "weapon"
    else:
        raise ValueError("Off-banner 4 Star chances do not add up to 1, did you change their values?")
    
    return item_dropped, item_type, item_drop_method

def weapon_banner_get_five_weapon(iteration_state: IterationState, simulation_settings: SimulationSettings, goal: Goal) -> tuple[str, str, str]: 
    """Determine the five-star weapon obtained.

    Weapon Banner five-star drop rules:
        - A five-star weapon drop can be the Primary (Epitomized) weapon, the Secondary Weapon, or a random off-banner five-star weapon.
        - Getting a five-star weapon that is not the chosen one grants an Epitomized Path Point.
        - Having one Epitomized Path Point guarantees the next five-star weapon will be the Primary Weapon, and sets the point back to zero.
        - A guarantee grants a randomly selected limited five-star weapon, which can be either Primary or Secondary.
        - Winning the 75/25 grants a randomly selected limited five-star weapon, which can be either Primary or Secondary.
        - Losing the 75/25 grants you a randomly selected off-banner five-star weapon, and guarantees the next one will be limited.

    Some values presented above are the default, and can be modified in simulation_settings.

    Args:
        iteration_state (IterationState): Current state of the simulation.
        simulation_settings (SimulationSettings): Settings chosen for the simulation. 
        goal (Goal): Target item configuration determining the active banner type.

    Returns:
        tuple[str, str, str]: A tuple containing three strings:
            - item_dropped: The name of the dropped item.
            - item_type: Category of the item ("weapon").
            - item_drop_method: Message for logs.
    """

    item_type = "weapon" # Always a weapon
    #Case: Epitomized Path
    if iteration_state.epitomized_path >= 1:
        iteration_state.five_weapon_guarantee = False
        item_dropped = goal.goal_banner.banner_five_item_primary
        item_drop_method = f"EPITOMIZED PATH TRIGGERED"
        handle_epitomized_path_points(iteration_state, "EPITOMIZED")

    #Guarantee Cases
    elif iteration_state.five_weapon_guarantee:
        iteration_state.five_weapon_guarantee = False

        #Won primary weapon
        if random.random() < simulation_settings.five_primary_weapon_chance:
            item_dropped = goal.goal_banner.banner_five_item_primary
            item_drop_method = f"GUARANTEED, WON PRIMARY WEAPON"
            handle_epitomized_path_points(iteration_state, "WON")

        #Lost to secondary weapon
        else:
            item_dropped = goal.goal_banner.banner_five_item_secondary
            item_drop_method = f"GUARANTEED, LOST TO SECONDARY WEAPON"
            handle_epitomized_path_points(iteration_state, "LOST")

    #Won Unguaranteed Limited Rolls
    elif random.random() < simulation_settings.five_weapon_limited_chance:

        #Won primary weapon
        if random.random() < simulation_settings.five_primary_weapon_chance:
            item_dropped = goal.goal_banner.banner_five_item_primary
            item_drop_method = f"WON LIMITED ROLL, WON PRIMARY WEAPON"
            handle_epitomized_path_points(iteration_state, "WON")

        #Lost to secondary weapon
        else:
            item_dropped = goal.goal_banner.banner_five_item_secondary
            item_drop_method = f"WON LIMITED ROLL, LOST TO SECONDARY WEAPON"
            handle_epitomized_path_points(iteration_state, "LOST")

    #Lost to standard
    else:
        item_dropped = get_off_banner_five_weapon(goal.goal_banner)
        item_drop_method = "LOST TO STANDARD WEAPON"
        handle_epitomized_path_points(iteration_state, "LOST")
        iteration_state.five_weapon_guarantee = True

    return item_dropped, item_type, item_drop_method

def weapon_banner_get_four_item(iteration_state: IterationState, simulation_settings: SimulationSettings, goal: Goal) -> tuple[str, str, str]:
    """Determine the four-star weapon or character obtained.

    Weapon Banner four-star drop rules:
        - A guarantee grants a randomly selected limited four-star weapon from the five on banner and consumes it.
        - Winning the 75/25 grants a randomly selected limited four-star weapon from the five on banner.
        - Losing the 75/25 has a variety of sub-mechanics:
            - Items within the banner cannot be obtained through the standard items pool.
            - There is an 92.5% chance the item will be a four-star character, otherwise, a four-star weapon will be selected.
            - Losing the 75/25 grants you a guarantee.

    Some values presented above are the default, and can be modified in simulation_settings.
    Args:
        iteration_state (IterationState): Current state of the simulation.
        simulation_settings (SimulationSettings): Settings chosen for the simulation. 
        goal (Goal): Target item configuration determining the active banner type.

    Returns:
        tuple[str, str, str]: A tuple containing three strings:
            - item_dropped: The name of the dropped item.
            - item_type: Category of the item ("character" or "weapon").
            - item_drop_method: Message for logs.
    """

    
    off_banner_character_chance = simulation_settings.weapon_banner_off_banner_four_star_character_chance
    off_banner_weapon_chance = simulation_settings.weapon_banner_off_banner_four_star_weapon_chance
    off_banner_roll = random.random()
    item_type = "weapon"

    # Guaranteed
    if iteration_state.four_weapon_guarantee:
        iteration_state.four_weapon_guarantee = False
        item_dropped = random.choice(goal.goal_banner.banner_four_items)
        item_drop_method = f"GUARANTEED"
    
    #Case: Won limited 
    elif random.random() < simulation_settings.four_weapon_limited_chance:
        item_dropped = random.choice(goal.goal_banner.banner_four_items)
        item_drop_method = f"WON LIMITED"

    #Case: Lost limited weapon roll. Got off-banner weapon. 
    elif off_banner_roll < off_banner_weapon_chance:
        iteration_state.four_weapon_guarantee = True
        item_dropped = get_off_banner_four_weapon(goal.goal_banner)
        item_drop_method = f"LOST LIMITED ROLL, GOT OFF BANNER WEAPON in WPN BANNER "

    #Case: Lost limited weapon roll. Got off-banner character. 
    elif off_banner_roll < off_banner_character_chance + off_banner_weapon_chance:
        item_dropped = get_off_banner_four_character(goal.goal_banner)
        iteration_state.four_weapon_guarantee = True
        item_drop_method = f"LOST LIMITED ROLL,, GOT OFF BANNER CHARACTER in WPN BANNER" 
        item_type = "character"
    else:
        raise ValueError("Off-banner 4 Star chances do not add up to 1, did you change their values?")
    
    return item_dropped, item_type, item_drop_method

def get_off_banner_five_character() -> str:
    """Return a random standard five-star character.

    Returns:
        str: Name of the randomly selected standard five-star character.
    """
    return random.choice(STANDARD_FIVE_STAR_CHARACTER_LIST)

def get_off_banner_five_weapon(banner: Banner) -> str:
    """Return a random standard five-star weapon.
    
    Removes items featured within the limited list from the standard list.
    
    Args:
        banner (Banner): Required to remove the present items from the standard list.
    
    Returns:
        str: Name of the randomly selected standard five-star weapon.
    """
    #Takes the weapons within the banner out of the possible drop list, as that's not possible!
    banner_item_list = [banner.banner_five_item_primary, banner.banner_five_item_secondary]
    off_banner_list = set(STANDARD_FIVE_STAR_WEAPON_LIST) #Uses the standard list

    off_banner_list = [
        weapon for weapon in off_banner_list
        if weapon not in banner_item_list
    ]

    return random.choice(off_banner_list)

def get_off_banner_four_character(banner: Banner) -> str:
    """Return a random standard four-star character.
    
    Removes items featured within the limited list from the standard list.
    
    Args:
        banner (Banner): Required to remove the present items from the standard list.
    
    Returns:
        str: Name of the randomly selected standard four-star character.
    """
    #Takes the characters within the banner out of the possible drop list, as that's not possible!
    banner_item_list = banner.banner_four_items
    off_banner_list = set(STANDARD_FOUR_STAR_CHARACTER_LIST) #Uses the limited list

    off_banner_list = [
        character for character in off_banner_list
        if character not in banner_item_list
    ]

    return random.choice(off_banner_list)

def get_off_banner_four_weapon(banner: Banner) -> str:
    """Return a random standard four-star weapon.
    
    Removes items featured within the limited list from the standard list.
    
    Args:
        banner (Banner): Required to remove the present items from the standard list.
    
    Returns:
        str: Name of the randomly selected standard four-star weapon.
    """
    #Takes the weapons within the banner out of the possible drop list, as that's not possible!
    banner_item_list = banner.banner_four_items
    off_banner_list = set(STANDARD_FOUR_STAR_WEAPON_LIST) #Uses the standard list

    off_banner_list = [
        weapon for weapon in off_banner_list
        if weapon not in banner_item_list
    ]
    
    return random.choice(off_banner_list)

def process_items(iteration_state: IterationState, debug_state: DebugState, item_name: str, item_type: str, item_rarity: str) -> None:
    """
    Processes item copy counts within the iteration state after being obtained.
    Attempts to find it from iteration_state and grab its value, otherwise, sets it to None, which it processes as follows:
    
    * Character: Base value in Genshin Impact for baseline copies is C0, so None gets set to 0.
    * weapon: Base value in Genshin Impact for baseline copies is R1, so None gets set to 1.

    If a value is found, it means it's already owned, so it adds +1 to the copy.

    Args:
        iteration_state (IterationState): Current state of the simulation.
        debug_state (DebugState): Options for debugging and logging.
        item_name (str): The name of the item to process. 
        item_type (str): The type of the item to drop. Expected values are "character" or "weapon".
        item_rarity (str): The rarity of the item to drop. Expected values are "five" or "four".
    """
    
    if item_type == "character":
        current_copy_count = iteration_state.characters[item_rarity].get(item_name, None)
        
        if current_copy_count is None:
            iteration_state.characters[item_rarity][item_name] = 0

        else: 
            iteration_state.characters[item_rarity][item_name] = current_copy_count + 1

    if item_type == "weapon":
        current_copy_count = iteration_state.weapons[item_rarity].get(item_name, None)
        
        if current_copy_count is None:
            iteration_state.weapons[item_rarity][item_name] = 1

        else: 
            iteration_state.weapons[item_rarity][item_name] = current_copy_count + 1

    #Logging
    if debug_state.debug_process_item: 
        if current_copy_count == -1:
            current_copy_count = "UNOWNED"
        if item_type == "character":
            logger.debug(f"{item_rarity=} {item_name, item_type} {current_copy_count} -> {iteration_state.characters[item_rarity][item_name]}")
        if item_type == "weapon":
            logger.debug(f"{item_rarity=} {item_name, item_type} {current_copy_count} -> {iteration_state.weapons[item_rarity][item_name]}")

def process_starglitter(iteration_state: IterationState, simulation_results: SimulationResults, simulation_settings: SimulationSettings, debug_state: DebugState, item_name: str, item_type: str, item_rarity: str) -> None:
    """
    Processes starglitter earned from item copies. Whenever used, it will grant starglitter based on the **current** copy found on iteration_state.
    Also updates the iteration's Starglitter balance and the simulation's total Starglitter and Masterless Stella Fortuna earned.

    Rules of Starglitter Refund:
        * Characters: 
            * Getting a copy of a five-star character gives 10, until it reaches C6, where it gives 25.
            * Getting a copy of a four-star character gives 2, until it reaches C6, where it gives 5.
            * The first instance of a character does not provide any starglitter.
            * Getting a copy of a five-star character post C6 grants a Masterless Stella Fortuna.

        * Weapons:
            * Getting a five-star weapon gives 10.
            * Getting a four-star weapon gives 2.
            * These values are constant accross any possible copy count.

        The values presented above are the default, and can be modified in simulation_settings.

    Args:
        iteration_state (IterationState): Current state of the simulation.
        simulation_results (SimulationResults): Utilized to count total starglitter across the simulation.
        simulation_settings (SimulationSettings): Utilized to determine the starglitter refund values.
        debug_state (DebugState): Options for debugging and logging.
        item_name (str): The name of the item to process. 
        item_type (str): The type of the item to process. Expected values are "character" or "weapon".
        item_rarity (str): The rarity of the item to process. Expected values are "five" or "four".
    """
    
    starglitter_refund = 0

    if item_type == "character":
        current_copy_count = iteration_state.characters[item_rarity].get(item_name, -1)

        if item_rarity == "five":
            if current_copy_count > 0 and current_copy_count < 7: #C0-C6
                starglitter_refund = simulation_settings.five_character_unmax_starglitter
            if current_copy_count > 6: #>C6
                starglitter_refund = simulation_settings.five_character_max_starglitter
                simulation_results.total_masterless_fortuna_earned += 1

        if item_rarity == "four":
            if current_copy_count > 0 and current_copy_count < 7: #C0-C6
                starglitter_refund = simulation_settings.four_character_unmax_starglitter
            if current_copy_count > 6: #>C6
                starglitter_refund = simulation_settings.four_character_max_starglitter

    if item_type == "weapon":
        if item_rarity == "five":
            starglitter_refund = simulation_settings.five_weapon_starglitter
        if item_rarity == "four":
            starglitter_refund = simulation_settings.four_weapon_starglitter

    iteration_state.masterless_starglitter += starglitter_refund
    simulation_results.total_starglitter_earned += starglitter_refund

    # Logging
    if debug_state.debug_starglitter_income_info:
        if item_type == "character":
            logger.debug(f"Got C{current_copy_count} {item_name=} ({item_rarity} star {item_type}) +{starglitter_refund} Starglitter ({iteration_state.masterless_starglitter})")
        if item_type == "weapon":
            logger.debug(f"Got {item_name=} ({item_rarity} star {item_type}) +{starglitter_refund} Starglitter ({iteration_state.masterless_starglitter})")

def calculate_initial_wishes(simulation_settings: SimulationSettings, intertwined_fates: int, primogems: int, genesis_crystals: int, masterless_starglitter: int, ) -> tuple[int, int]:
    """Calculate initial wishes and remaining Masterless Starglitter.

    Converts Genesis Crystals, Primogems, and Masterless Starglitter into Intertwined Fates using the configured conversion costs. 

    Args:
        simulation_settings (SimulationSettings): Settings containing the Primogem-to-wish and Starglitter-to-wish conversion costs. 
        intertwined_fates (int): Initial number of Intertwined Fates owned.
        primogems (int): Number of Primogems owned.
        genesis_crystals (int): Number of Genesis Crystals owned.
        masterless_starglitter (int): Amount of Masterless Starglitter owned.

    Returns:
        A tuple containing the total Intertwined Fates available and
        the remaining Masterless Starglitter after conversion.

    Raises:
        ValueError: If either conversion cost is zero or negative.
    """
    if simulation_settings.primogem_to_wish_cost <= 0:
        raise ValueError("Primogem-to-wish cost must be greater than zero.")

    if simulation_settings.starglitter_to_wish_cost <= 0:
        raise ValueError("Starglitter-to-wish cost must be greater than zero.")

    intertwined_fates += genesis_crystals // simulation_settings.primogem_to_wish_cost
    intertwined_fates += primogems // simulation_settings.primogem_to_wish_cost
    intertwined_fates += masterless_starglitter // simulation_settings.starglitter_to_wish_cost

    masterless_starglitter %= simulation_settings.starglitter_to_wish_cost

    return intertwined_fates, masterless_starglitter