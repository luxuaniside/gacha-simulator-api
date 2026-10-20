from app.services.inventory_services import get_item
from app.models.iteration_state import IterationState
from app.models.simulation_settings import SimulationSettings, DebugState
from app.models.simulation_results import SimulationResults
from app.models.goals_state import Goal
from app.models.banners_state import Banner
import pytest
from unittest.mock import patch
from dataclasses import replace

# Defining fixtures for pytest
@pytest.fixture
def iteration_state():
    return IterationState(
        intertwined_fates=0,
        masterless_starglitter=0,
        five_character_pity=0,
        four_character_pity=0,
        five_weapon_pity=0,
        four_weapon_pity=0,
        five_character_guarantee=False,
        four_character_guarantee=False,
        five_weapon_guarantee=False,
        four_weapon_guarantee=False,
        epitomized_path=0,
        capturing_radiance=0,
        characters={},
        weapons={},
        goals=[],
        banners=[],
    )

@pytest.fixture
def one_epitomized_path_state(iteration_state):
    return replace(iteration_state, epitomized_path=1)

@pytest.fixture
def zero_epitomized_path_state(iteration_state):
    return replace(iteration_state, epitomized_path=0)

@pytest.fixture
def guaranteed_limited__weapon_state(iteration_state):
    return replace(iteration_state, five_weapon_guarantee=True)

@pytest.fixture
def unguaranteed_limited__weapon_state(iteration_state):
    return replace(iteration_state, five_weapon_guarantee=False)

@pytest.fixture
def simulation_settings() -> SimulationSettings:
    return SimulationSettings(1, False, False, 120)

@pytest.fixture
def simulation_results() -> SimulationResults:
    return SimulationResults()

@pytest.fixture
def debug_state():
    return DebugState()

@pytest.fixture
def banner():
    return Banner(
        banner_name="Version 1",
        banner_five_item_primary="Primary Weapon",
        banner_five_item_secondary="Secondary Weapon",
        banner_four_items=["Four-Star Weapon 1", "Four-Star Weapon 2", "Four-Star Weapon 3", "Four-Star Weapon 4", "Four-Star Weapon 5"],
        item_type="weapon",
    )

@pytest.fixture
def goal(banner):
    return Goal(
        goal_name="Limited Weapon C0",
        item_name="Primary Weapon",
        goal_banner=banner,
        item_type="weapon",
        item_rarity="five",
        item_target_count=1,
        item_high_priority=True,
    )

# Epitomized Path Tests

def test_epitomized_grants_primary_weapon(one_epitomized_path_state, simulation_settings, debug_state, goal):
    state: IterationState = one_epitomized_path_state
    assert state.epitomized_path == 1, "Epitomized Path is selected to one." 

    item_name, _ = get_item(one_epitomized_path_state, simulation_settings, debug_state, goal, "five")
    assert item_name == goal.goal_banner.banner_five_item_primary, "Item Obtained is Primary Weapon"

def test_epitomized_priority_over_guarantee(one_epitomized_path_state, simulation_settings, debug_state, goal):
    state: IterationState = one_epitomized_path_state
    assert state.epitomized_path == 1, "Epitomized Path is selected to one."

    #Force a guarantee, and also change primary weapon chances to be zero.
    state.five_weapon_guarantee = True
    simulation_settings.five_primary_weapon_chance = 0
    

    item_name, _ = get_item(one_epitomized_path_state, simulation_settings, debug_state, goal, "five")
    assert item_name == goal.goal_banner.banner_five_item_primary, "Item Obtained is Primary Weapon"

def test_epitomized_using_removes_point(one_epitomized_path_state, simulation_settings, debug_state, goal):
    state: IterationState = one_epitomized_path_state
    assert state.epitomized_path == 1, "Epitomized Path is selected to one." 

    item_name, _ = get_item(one_epitomized_path_state, simulation_settings, debug_state, goal, "five")
    assert item_name == goal.goal_banner.banner_five_item_primary, "Item Obtained is Primary Weapon"
    assert state.epitomized_path == 0, "Epitomized Path is reset back to zero"


def test_epitomized_non_primary_grants_point(zero_epitomized_path_state, simulation_settings, debug_state, goal):
    state: IterationState = zero_epitomized_path_state
    assert state.epitomized_path == 0, "Epitomized Path is selected to zero."

    #Change chances to force a lose 
    simulation_settings.five_primary_weapon_chance = 0

    item_name, _ = get_item(zero_epitomized_path_state, simulation_settings, debug_state, goal, "five")
    assert item_name != goal.goal_banner.banner_five_item_primary, "Item Obtained is not Primary Weapon"
    assert state.epitomized_path == 1, "Granted an Epitomized Path point"
    
# Guarantee Tests

def test_guarantee_grants_limited_weapon(guaranteed_limited__weapon_state, simulation_settings, debug_state, goal):
    state: IterationState = guaranteed_limited__weapon_state
    assert state.five_weapon_guarantee is True, "Limited weapon is guaranteed"

    item_name, _ = get_item(guaranteed_limited__weapon_state, simulation_settings, debug_state, goal, "five")

    limited_weapons = [goal.goal_banner.banner_five_item_primary, goal.goal_banner.banner_five_item_secondary]
    assert item_name in limited_weapons, "Weapon is limited"

def test_guarantee_is_removed_post_use(guaranteed_limited__weapon_state, simulation_settings, debug_state, goal):
    state: IterationState = guaranteed_limited__weapon_state
    assert state.five_weapon_guarantee is True, "Limited weapon is guaranteed"

    item_name, _ = get_item(guaranteed_limited__weapon_state, simulation_settings, debug_state, goal, "five")

    limited_weapons = [goal.goal_banner.banner_five_item_primary, goal.goal_banner.banner_five_item_secondary]
    assert item_name in limited_weapons, "Weapon is limited"
    assert state.five_weapon_guarantee is False, "Guarantee is removed"

def test_guarantee_is_activated_post_losing_75_25(unguaranteed_limited__weapon_state, simulation_settings, debug_state, goal):
    state: IterationState = unguaranteed_limited__weapon_state
    assert state.five_weapon_guarantee is False, "Limited weapon is not guaranteed"

    #Force a lose
    simulation_settings.five_weapon_limited_chance = 0
    item_name, _ = get_item(unguaranteed_limited__weapon_state, simulation_settings, debug_state, goal, "five")

    limited_weapons = [goal.goal_banner.banner_five_item_primary, goal.goal_banner.banner_five_item_secondary]
    assert item_name not in limited_weapons, "Weapon is standard"
    assert state.five_weapon_guarantee is True, "Guarantee is granted"


# 75/25
def test_75_25_winning_grants_limited(unguaranteed_limited__weapon_state, simulation_settings, debug_state, goal):
    state: IterationState = unguaranteed_limited__weapon_state
    assert state.five_weapon_guarantee is False, "Limited weapon is not guaranteed"

    #Force a win
    simulation_settings.five_weapon_limited_chance = 1
    item_name, _ = get_item(unguaranteed_limited__weapon_state, simulation_settings, debug_state, goal, "five")

    limited_weapons = [goal.goal_banner.banner_five_item_primary, goal.goal_banner.banner_five_item_secondary]
    assert item_name in limited_weapons, "Weapon is limited"

def test_75_25_losing_grants_standard(unguaranteed_limited__weapon_state, simulation_settings, debug_state, goal):
    state: IterationState = unguaranteed_limited__weapon_state
    assert state.five_weapon_guarantee is False, "Limited weapon is not guaranteed"

    #Force a lose
    simulation_settings.five_weapon_limited_chance = 0
    item_name, _ = get_item(unguaranteed_limited__weapon_state, simulation_settings, debug_state, goal, "five")

    limited_weapons = [goal.goal_banner.banner_five_item_primary, goal.goal_banner.banner_five_item_secondary]
    assert item_name not in limited_weapons, "Weapon is standard"


"""
A five-star weapon drop can be the Primary (Epitomized) weapon, the Secondary Weapon, or a random off-banner five-star weapon.
Getting a five-star weapon that is not the chosen one grants an Epitomized Path Point.
Having one Epitomized Path Point guarantees the next five-star weapon will be the Primary Weapon, and sets the point back to zero.
A guarantee grants a randomly selected limited five-star weapon, which can be either Primary or Secondary.
Winning the 75/25 grants a randomly selected limited five-star weapon, which can be either Primary or Secondary.
Losing the 75/25 grants you a randomly selected off-banner five-star weapon, and guarantees the next one will be limited.

"""