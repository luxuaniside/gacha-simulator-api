import logging
import random 
import json

from app.models.iteration_state import WishState
from app.models.simulation_settings import SimulationSettings, DebugState
from app.models.simulation_results import SimulationResults
from app.models.goals_state import Goal

from app.services.probability_services import capturing_radiance

logger = logging.getLogger(__name__)


LIMITED_FOUR_STAR_CHARACTER_LIST = [
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
    "Amber",
    "Kaeya",
    "Lisa"
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



def get_item(iteration_state: WishState, simualation_settings: SimulationSettings, simulation_results: SimulationResults, debug_state: DebugState, goal: Goal, dropped_item_rarity):
    item_dropped = "Nothing"
    
    if dropped_item_rarity == "five" and goal.item_type == "character":
        item_dropped, item_drop_method = get_five_character(iteration_state, simualation_settings, goal)
        item_type = "character"
        
    if dropped_item_rarity == "four" and goal.item_type == "character":
        item_dropped, item_type, item_drop_method = get_four_character(iteration_state, simualation_settings, goal)

    if dropped_item_rarity == "five" and goal.item_type == "weapon":
        item_dropped, item_drop_method = get_five_weapon(iteration_state, simualation_settings, goal)
        item_type = "weapon"

    if dropped_item_rarity == "four" and goal.item_type == "weapon":
        item_dropped, item_type, item_drop_method = get_four_weapon(iteration_state, simualation_settings, goal)

    if debug_state.debug_item_pulled_info:
        logger.debug(f"ITERATION {iteration_state.current_iteration} | {item_dropped=} {item_drop_method=}")
    
    return item_dropped, item_type
    
def get_five_character(iteration_state: WishState, simulation_settings: SimulationSettings, goal: Goal):
    #Rules of five characters:
    #If guaranteed, get char
    #If 50/50 won, get char
    #If 50/50 loss but capturing radiance won, get char
    #If 50/50 loss and no capturing radiance, get_standard_five_char():
    #Case: Limited five star is guaranteed.

    #Case: Guaranteed
    if iteration_state.five_character_guarantee:
        iteration_state.five_character_guarantee = False
        item_dropped = goal.goal_banner.banner_five_item_primary
        item_drop_method = F"GUARANTEE (Now {iteration_state.capturing_radiance} RADIANCE)"
     
    #Case: Lost 50/50, capturing_radiance() saves
    elif capturing_radiance(simulation_settings, iteration_state.capturing_radiance):
        item_drop_method = f"RADIANCE (At {iteration_state.capturing_radiance})"
        iteration_state.capturing_radiance = 1
        item_dropped = goal.goal_banner.banner_five_item_primary

    #Case: Won 50/50
    elif random.random() < simulation_settings.five_characterlimited_chance:
        #Capturing radiance goes down whenever you win 50/50, min being 0.
        if iteration_state.capturing_radiance > 0:
            iteration_state.capturing_radiance -= 1
        
        item_dropped = goal.goal_banner.banner_five_item_primary
        item_drop_method = f"50/50 WON (Now {iteration_state.capturing_radiance} RADIANCE)"
    
    #Case: Lost 50/50, capturing_radiance() does not save
    else:
        iteration_state.five_character_guarantee = True
        #Capturing radiance goes up whenever you lose 50/50, max being 3.
        if iteration_state.capturing_radiance < 3:
            iteration_state.capturing_radiance += 1

        item_dropped = get_offbanner_five_char() 
        item_drop_method = f"50/50 LOSS (Now {iteration_state.capturing_radiance} RADIANCE)"
   
    return item_dropped, item_drop_method

def get_four_character(iteration_state: WishState, simulation_settings: SimulationSettings, goal: Goal):
    #Rules of four characters:
    #If guaranteed get one of the three limited
    #If 50/50 won get one of three limited
    #If 50/50 loss get either char or wpn 
    #Chars have the limited ones removed from the possibility
    
    #Case: Guaranteed

    off_banner_characterchance = simulation_settings.character_banner_off_banner_four_star_characterchance
    off_banner_weapon_chance = simulation_settings.character_banner_off_banner_four_star_weapon_chance
    off_banner_roll = random.random()
    item_type = "character"

    if iteration_state.four_character_guarantee:
        iteration_state.four_character_guarantee = False
        item_dropped = random.choice(goal.goal_banner.banner_four_items)
        item_drop_method = f"GUARANTEED"
    
    #Case: Won 50/50
    elif random.random() < simulation_settings.four_characterlimited_chance:
        item_dropped = random.choice(goal.goal_banner.banner_four_items)
        item_drop_method = f"WON 50/50"

    #Case: Lost 50/50, got off banner weapon    
    elif off_banner_roll < off_banner_characterchance:
        iteration_state.four_character_guarantee = True
        item_dropped = get_offbanner_four_char(goal)
        item_drop_method = f"LOST 50/50, GOT OFF BANNER CHAR in CHAR BANNER"    

    #Case: Lost 50/50, got off banner weapon    
    elif off_banner_roll < off_banner_characterchance + off_banner_weapon_chance:
        item_dropped = get_offbanner_four_weapon(goal)
        iteration_state.four_character_guarantee = True
        item_drop_method = f"LOST 50/50, GOT OFF BANNER WEAPON in CHAR BANNER" 
        item_type = "weapon"
    else:
        raise ValueError("Off-banner 4 Star chances do not add up to 1, did you change their values?")
    
    return item_dropped, item_type, item_drop_method

def get_five_weapon(iteration_state: WishState, simulation_settings: SimulationSettings, goal: Goal):
    #Rules of five star weapon
    #1 epitomized, got primary weapon 
    #0 epitomized, guaranteed, got primary weapon
    #0 epitomized, guaranteed, got secondary weapon
    #0 epitomized 75/25 won, got primary weapon
    #0 epitomized, 75/25 won, got secondary weapon
    #0 epitomized, 75/25 lost, got standard weapon
    
    #Case: Epitomized Path
    if iteration_state.epitomized_path >= 1:
        iteration_state.epitomized_path = 0
        iteration_state.five_weapon_guarantee = False
        item_dropped = goal.goal_banner.banner_five_item_primary
        item_drop_method = f"EPITOMIZED PATH TRIGGERED"

    #Guarantee Cases
    elif iteration_state.five_weapon_guarantee:
        iteration_state.five_weapon_guarantee = False

        #Won 50/50
        if random.random() < simulation_settings.five_primary_weapon_chance:
            item_dropped = goal.goal_banner.banner_five_item_primary
            item_drop_method = f"GUARANTEED, WON 50/50"

        #Lost 50/50
        else:
            item_dropped = goal.goal_banner.banner_five_item_secondary
            item_drop_method = f"GUARANTEED, LOST 50/50"
            iteration_state.epitomized_path = 1

    #75/25 Cases
    elif random.random() < simulation_settings.five_weapon_limited_chance:

        #Won 50/50
        if random.random() < simulation_settings.five_primary_weapon_chance:
            item_dropped = goal.goal_banner.banner_five_item_primary
            item_drop_method = f"WON 75/25, WON 50/50"

        #Lost 50/50
        else:
            item_dropped = goal.goal_banner.banner_five_item_secondary
            item_drop_method = f"WON 75/25, LOST 50/50"
            iteration_state.epitomized_path = 1

    #Lost 75/25 Case
    else:
        item_dropped = get_offbanner_five_weapon(goal)
        item_drop_method = "LOST 75/25"
        iteration_state.epitomized_path = 1
        iteration_state.five_weapon_guarantee = True

    return item_dropped, item_drop_method

def get_four_weapon(iteration_state: WishState, simulation_settings: SimulationSettings, goal: Goal):
    #Rules of four weapons:
    #If guaranteed get one of the three limited
    #If 50/50 won get one of three limited
    #If 50/50 loss get either char or wpn 
    #Chars have the limited ones removed from the possibility
    
    #Case: Guaranteed

    off_banner_characterchance = simulation_settings.character_banner_off_banner_four_star_characterchance
    off_banner_weapon_chance = simulation_settings.character_banner_off_banner_four_star_weapon_chance
    off_banner_roll = random.random()
    item_type = "weapon"

    if iteration_state.four_weapon_guarantee:
        iteration_state.four_weapon_guarantee = False
        item_dropped = random.choice(goal.goal_banner.banner_four_items)
        item_drop_method = f"GUARANTEED"
    
    #Case: Won 50/50
    elif random.random() < simulation_settings.four_weapon_limited_chance:
        item_dropped = random.choice(goal.goal_banner.banner_four_items)
        item_drop_method = f"WON 50/50"

    #Case: Lost 50/50, got off banner weapon    
    elif off_banner_roll < off_banner_weapon_chance:
        iteration_state.four_weapon_guarantee = True
        item_dropped = get_offbanner_four_weapon(goal)
        item_drop_method = f"LOST 50/50, GOT OFF BANNER WEAPON in WPN BANNER "

    #Case: Lost 50/50, got off banner char
    elif off_banner_roll < off_banner_characterchance + off_banner_weapon_chance:
        item_dropped = get_offbanner_four_char(goal)
        iteration_state.four_weapon_guarantee = True
        item_drop_method = f"LOST 50/50, GOT OFF BANNER CHARACTER in WPN BANNER" 
        item_type = "character"
    else:
        raise ValueError("Off-banner 4 Star chances do not add up to 1, did you change their values?")
    
    return item_dropped, item_type, item_drop_method

def get_offbanner_five_char():
    return random.choice(STANDARD_FIVE_STAR_CHARACTER_LIST)

def get_offbanner_five_weapon(goal: Goal):
    #Takes the weapons within the banner out of the possible drop list, as that's not possible!
    banner_item_list = [goal.goal_banner.banner_five_item_primary, goal.goal_banner.banner_five_item_secondary]
    off_banner_list = set(STANDARD_FIVE_STAR_WEAPON_LIST) #Uses the standard list

    off_banner_list = [
        char for char in off_banner_list
        if char not in banner_item_list
    ]

    return random.choice(off_banner_list)

def get_offbanner_four_char(goal: Goal):
    #Takes the characters within the banner out of the possible drop list, as that's not possible!
    banner_item_list = goal.goal_banner.banner_four_items
    off_banner_list = set(LIMITED_FOUR_STAR_CHARACTER_LIST) #Uses the limited list

    off_banner_list = [
        char for char in off_banner_list
        if char not in banner_item_list
    ]

    return random.choice(off_banner_list)

def get_offbanner_four_weapon(goal: Goal):
        #Takes the weapons within the banner out of the possible drop list, as that's not possible!
    banner_item_list = goal.goal_banner.banner_four_items
    off_banner_list = set(STANDARD_FOUR_STAR_WEAPON_LIST) #Uses the standard list

    off_banner_list = [
        char for char in off_banner_list
        if char not in banner_item_list
    ]
    
    return random.choice(off_banner_list)
  
def get_owned_weapons():
    weapons_owned = {
        "five": {

        },
        "four" : {

        }
    }

    return weapons_owned

def process_items(iteration_state: WishState, debug_state: DebugState, item_name, item_type, item_rarity):
    if item_type == "character":
        current_copy_count = iteration_state.characters[item_rarity].get(item_name, -1)
        
        if current_copy_count == -1:
            iteration_state.characters[item_rarity][item_name] = 0

        else: 
            iteration_state.characters[item_rarity][item_name] = current_copy_count + 1

    if item_type == "weapon":
        current_copy_count = iteration_state.weapons[item_rarity].get(item_name, -1)
        
        if current_copy_count == -1:
            iteration_state.weapons[item_rarity][item_name] = 1

        else: 
            iteration_state.weapons[item_rarity][item_name] = current_copy_count + 1

    if debug_state.debug_process_item: 
        if current_copy_count == -1:
            current_copy_count = "UNOWNED"
        if item_type == "character":
            logger.debug(f"{item_rarity=} {item_name, item_type} {current_copy_count} -> {iteration_state.characters[item_rarity][item_name]}")
        if item_type == "weapon":
            logger.debug(f"{item_rarity=} {item_name, item_type} {current_copy_count} -> {iteration_state.weapons[item_rarity][item_name]}")

def process_starglitter(iteration_state: WishState, simulation_results: SimulationResults, simulation_settings: SimulationSettings, debug_state: DebugState, item_name, item_type, item_rarity):
    starglitter_refund = 0

    if item_type == "character":
        current_copy_count = iteration_state.characters[item_rarity].get(item_name, -1)
        
        if item_rarity == "five":
            if current_copy_count > 0 and current_copy_count < 7: #C0-C6
                starglitter_refund = simulation_settings.five_characterunmax_starglitter
            if current_copy_count > 6: #>C6
                starglitter_refund = simulation_settings.five_charactermax_starglitter
                simulation_results.total_masterless_fortuna_earned += 1

        if item_rarity == "four":
            if current_copy_count > 0 and current_copy_count < 7: #C0-C6
                starglitter_refund = simulation_settings.four_characterunmax_starglitter
            if current_copy_count > 6: #>C6
                starglitter_refund = simulation_settings.four_charactermax_starglitter

    if item_type == "weapon":
        if item_rarity == "five":
            starglitter_refund = simulation_settings.five_weapon_starglitter
        if item_rarity == "four":
            starglitter_refund = simulation_settings.four_weapon_starglitter

    iteration_state.masterless_starglitter += starglitter_refund
    simulation_results.total_starglitter_earned += starglitter_refund

    if debug_state.debug_starglitter_income_info:
        if item_type == "character":
            logger.debug(f"Got C{current_copy_count} {item_name=} ({item_rarity} star {item_type}) +{starglitter_refund} Starglitter ({iteration_state.masterless_starglitter})")
        if item_type == "weapon":
            logger.debug(f"Got {item_name=} ({item_rarity} star {item_type}) +{starglitter_refund} Starglitter ({iteration_state.masterless_starglitter})")

def calculate_initial_wishes(intertwined_fates, primogems, genesis_crystals, masterless_starglitter):
    simulation_settings = SimulationSettings(0, True, True)
    intertwined_fates += int(genesis_crystals/simulation_settings.primogem_to_wish_cost)
    intertwined_fates += int(primogems/simulation_settings.primogem_to_wish_cost)
    intertwined_fates += int(masterless_starglitter/simulation_settings.starglitter_to_wish_cost)
    masterless_starglitter %= simulation_settings.starglitter_to_wish_cost

    return intertwined_fates, masterless_starglitter