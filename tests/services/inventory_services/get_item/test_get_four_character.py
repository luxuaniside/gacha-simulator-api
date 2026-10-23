from app.services.inventory_services import get_item
from app.models.iteration_state import IterationState
from app.models.simulation.simulation_settings import SimulationSettings, DebugState
from app.models.simulation.simulation_results import SimulationResults
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
def limited_character_guaranteed_iteration_state(iteration_state):
    return replace(iteration_state, four_character_guarantee=True)

@pytest.fixture
def limited_character_unguaranteed_iteration_state(iteration_state):
    return replace(iteration_state, four_character_guarantee=False)


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
        banner_five_item_primary="Limited Character",
        banner_five_item_secondary=None,
        banner_four_items=["Four-Star Character 1", "Four-Star Character 2", "Four-Star Character 3"],
        item_type="character",
    )

@pytest.fixture
def goal(banner):
    return Goal(
        goal_name="Limited Character C0",
        item_name="Limited Character",
        goal_banner=banner,
        item_type="character",
        item_rarity="five",
        item_target_count=0,
        item_high_priority=True,
    )

# Guarantee
def test_guarantee_grants_limited_character(limited_character_guaranteed_iteration_state, simulation_settings, debug_state, goal):
    state: IterationState = limited_character_guaranteed_iteration_state
    assert state.four_character_guarantee is True, "The Character is Guaranteed"
    
    item_name, item_type = get_item(
        limited_character_guaranteed_iteration_state,
        simulation_settings,
        debug_state,
        goal,
        "four",
    )
    
    assert item_name in goal.goal_banner.banner_four_items, "The character is a limited four-star"

def test_guarantee_is_removed_post_use(limited_character_guaranteed_iteration_state, simulation_settings, debug_state, goal):
    state: IterationState = limited_character_guaranteed_iteration_state
    assert state.four_character_guarantee is True, "Character is guaranteed."
    
    get_item(state, simulation_settings, debug_state, goal, "four")
    assert state.four_character_guarantee is False, "Character Guaranteed is removed post-use."

def test_guarantee_is_activated_post_losing_50_50(limited_character_unguaranteed_iteration_state, simulation_settings, debug_state, goal):
    state: IterationState = limited_character_unguaranteed_iteration_state   
    assert state.four_character_guarantee is False, "Guarantee starts off as False"

    with patch("app.services.inventory_services.random.random", return_value = simulation_settings.four_character_limited_chance):
        get_item(state, simulation_settings, debug_state, goal, "four")
        assert state.four_character_guarantee is True, "Guarantee is granted post losing 50/50"

# 50/50
def test_50_50_losing_grants_standard(limited_character_unguaranteed_iteration_state, simulation_settings, debug_state, goal):
    state: IterationState = limited_character_unguaranteed_iteration_state
    assert state.four_character_guarantee is False, "Is not guaranteed"

    with patch("app.services.inventory_services.random.random", return_value = simulation_settings.four_character_limited_chance):
        item_name, item_type = get_item(state, simulation_settings, debug_state, goal, "four")
        assert item_name not in goal.goal_banner.banner_four_items

def test_50_50_winning_grants_limited(limited_character_unguaranteed_iteration_state, simulation_settings, debug_state, goal):
    state: IterationState = limited_character_unguaranteed_iteration_state
    assert state.four_character_guarantee is False, "Is not guaranteed"

    with patch("app.services.inventory_services.random.random", return_value = 0):
        item_name, item_type = get_item(state, simulation_settings, debug_state, goal, "four")
        assert item_name in goal.goal_banner.banner_four_items
