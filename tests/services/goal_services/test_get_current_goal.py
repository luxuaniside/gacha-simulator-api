from app.services.goal_services import get_current_goal

from app.models.iteration_state import IterationState
from app.models.simulation.simulation_settings import SimulationSettings, DebugState
from app.models.simulation.simulation_results import SimulationResults
from app.models.goals_state import Goal
from app.models.banners_state import Banner
import pytest
from dataclasses import replace

# Defining fixtures for pytest

@pytest.fixture
def character_banner():
    return Banner(
        banner_name="Version 1",
        banner_five_item_primary="Limited Character",
        banner_five_item_secondary=None,
        banner_four_items=["Four-Star Character 1", "Four-Star Character 2", "Four-Star Character 3"],
        item_type="character",
    )

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
        characters={"five" : {"Raiden Shogun" : 1, "Kokomi" : 1},"four" : {"Bennett" : 1}},
        weapons={},
        goals=[],
        banners=[character_banner]
    )
        

@pytest.fixture
def two_out_of_three_goals_are_completed_state(iteration_state):
    return replace(iteration_state, banners=[character_banner], goals=[
    Goal(
        goal_name="C1 Raiden Shogun",
        item_name="Raiden Shogun",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="five",
        item_target_count=1,
        item_high_priority=True,
    ),
    Goal(
        goal_name="C1 Bennett",
        item_name="Bennett",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="four",
        item_target_count=1,
        item_high_priority=True,
    ),
    Goal(
        goal_name="C2 Bennett",
        item_name="Bennett",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="four",
        item_target_count=2,
        item_high_priority=True,
    ),
    ])
    
@pytest.fixture
def three_out_of_three_goals_are_completed_state(iteration_state):
    return replace(iteration_state, banners=[character_banner], goals=[
    Goal(
        goal_name="C1 Raiden Shogun",
        item_name="Raiden Shogun",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="five",
        item_target_count=1,
        item_high_priority=True,
    ),
    Goal(
        goal_name="C1 Bennett",
        item_name="Bennett",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="four",
        item_target_count=1,
        item_high_priority=True,
    ),
    Goal(
        goal_name="C1 Kokomi",
        item_name="Kokomi",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="five",
        item_target_count=1,
        item_high_priority=True,
    ),
    ])
    
@pytest.fixture
def low_priority_goal_in_between_state(iteration_state):
    return replace(iteration_state, banners=[character_banner], goals=[
    Goal(
        goal_name="C1 Raiden Shogun",
        item_name="Raiden Shogun",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="five",
        item_target_count=1,
        item_high_priority=True,
    ),
    Goal(
        goal_name="C6 Bennett",
        item_name="Bennett",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="four",
        item_target_count=6,
        item_high_priority=False,
    ),
    Goal(
        goal_name="C6 Kokomi",
        item_name="Kokomi",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="five",
        item_target_count=6,
        item_high_priority=True,
    ),
    ])
    
@pytest.fixture
def all_high_priority_goals(iteration_state):
    return replace(iteration_state, banners=[character_banner], goals=[
    Goal(
        goal_name="C1 Raiden Shogun",
        item_name="Raiden Shogun",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="five",
        item_target_count=1,
        item_high_priority=True,
    ),
    Goal(
        goal_name="C6 Bennett",
        item_name="Bennett",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="four",
        item_target_count=6,
        item_high_priority=True,
    ),
    Goal(
        goal_name="C6 Kokomi",
        item_name="Kokomi",
        goal_banner=character_banner,
        item_type="character",
        item_rarity="five",
        item_target_count=6,
        item_high_priority=True,
    ),
    ])

@pytest.fixture
def debug_state():
    return DebugState()

def test_goal_changes_to_next_goal(two_out_of_three_goals_are_completed_state, debug_state):
    goal: Goal
    goal, _ = get_current_goal(two_out_of_three_goals_are_completed_state, debug_state)
    assert goal.goal_name == "C2 Bennett", "All other goals should be finished, while C2 bennett is not owned."

def test_goal_correctly_flag_goals_arent_finished(two_out_of_three_goals_are_completed_state, debug_state):
    _, all_goals_finished = get_current_goal(two_out_of_three_goals_are_completed_state, debug_state)
    assert all_goals_finished == False, "C2 Bennett is not owned"

def test_goal_state_with_finished_goals_returns_last_goal(three_out_of_three_goals_are_completed_state, debug_state):
    goal: Goal
    goal, all_goals_finished = get_current_goal(three_out_of_three_goals_are_completed_state, debug_state)
    assert goal.goal_name == "C1 Kokomi", "C1 Kokomi is the last goal in the list."
    assert all_goals_finished == True, "All goals have been finished"

def test_goal_correctly_flag_goals_are_finished(three_out_of_three_goals_are_completed_state, debug_state):
    _, all_goals_finished = get_current_goal(three_out_of_three_goals_are_completed_state, debug_state)
    assert all_goals_finished == True, "All goals have been finished."
    
def test_low_priority_is_skipped(low_priority_goal_in_between_state, debug_state):
    goal: Goal
    goal, _ = get_current_goal(low_priority_goal_in_between_state, debug_state)
    assert goal.goal_name == "C6 Kokomi", "C6 Bennett was skipped"
    
def test_high_priority_is_not_skipped(all_high_priority_goals, debug_state):
    goal: Goal
    goal, _ = get_current_goal(all_high_priority_goals, debug_state)
    assert goal.goal_name == "C6 Bennett", "C6 Bennett was not skipped"