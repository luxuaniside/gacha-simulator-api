from app.services.inventory_services import process_starglitter, process_items

from app.models.iteration_state import IterationState
from app.models.simulation_settings import SimulationSettings, DebugState
from app.models.simulation_results import SimulationResults
from app.models.goals_state import Goal
from app.models.banners_state import Banner
import pytest
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
def items_to_process_state(iteration_state):
    return replace(
        iteration_state,
        characters={
            "five" : {
                "Jean" : 0,
                "Diluc" : 1,
                "Mona" : 6,
                },
            "four" : {
                "Amber" : 0,
                "Kaeya" : 1,
                "Lisa" : 6
            }
        },
        weapons={
            "five" : {}, "four" : {},
        }
      
        )

@pytest.fixture
def simulation_settings() -> SimulationSettings:
    return SimulationSettings(1, False, False, 120)

@pytest.fixture
def simulation_results() -> SimulationResults:
    return SimulationResults()

@pytest.fixture
def debug_state():
    return DebugState()

@pytest.mark.parametrize(
    "item_name, item_type, item_rarity",
    [   
        ("Unowned to C0 Five Star Unit", "character", "five"),
        ("Unowned to C0 Four Star Unit", "character", "four"),
    ],
)
def test_starglitter_refund_unowned_characters(items_to_process_state, simulation_results, simulation_settings, debug_state, item_name, item_type, item_rarity):
    state: IterationState = items_to_process_state
    starglitter_owned = state.masterless_starglitter 
    assert starglitter_owned == 0, "Starglitter starts at 0"

    
    process_items(items_to_process_state, debug_state, item_name, item_type, item_rarity)
    process_starglitter(items_to_process_state, simulation_results, simulation_settings, debug_state, item_name, item_type, item_rarity)
    assert state.masterless_starglitter == starglitter_owned, "No starglitter was added."

@pytest.mark.parametrize(
    "item_name, item_type, item_rarity",
    [   
        ("Jean", "character", "five"),
        ("Amber", "character", "four"),
        ("Diluc", "character", "five"),
        ("Kaeya", "character", "four"),
    ],
)
def test_starglitter_refund_unmax_characters(items_to_process_state, simulation_results, simulation_settings, debug_state, item_name, item_type, item_rarity):
    state: IterationState = items_to_process_state
    starglitter_owned = state.masterless_starglitter 
    assert starglitter_owned == 0, "Starglitter starts at 0"
    
    process_items(items_to_process_state, debug_state, item_name, item_type, item_rarity)
    process_starglitter(items_to_process_state, simulation_results, simulation_settings, debug_state, item_name, item_type, item_rarity)
    if item_rarity == "five":
        assert state.masterless_starglitter == starglitter_owned + simulation_settings.five_character_unmax_starglitter
    elif item_rarity == "four":
        assert state.masterless_starglitter == starglitter_owned + simulation_settings.four_character_unmax_starglitter

@pytest.mark.parametrize(
    "item_name, item_type, item_rarity",
    [   
        ("Mona", "character", "five"),
        ("Lisa", "character", "four"),
    ],
)
def test_starglitter_refund_max_characters(items_to_process_state, simulation_results, simulation_settings, debug_state, item_name, item_type, item_rarity):
    state: IterationState = items_to_process_state
    starglitter_owned = state.masterless_starglitter 
    assert starglitter_owned == 0, "Starglitter starts at 0"

    process_items(items_to_process_state, debug_state, item_name, item_type, item_rarity)
    process_starglitter(items_to_process_state, simulation_results, simulation_settings, debug_state, item_name, item_type, item_rarity)
    if item_rarity == "five":
        assert state.masterless_starglitter == starglitter_owned + simulation_settings.five_character_max_starglitter
    elif item_rarity == "four":
        assert state.masterless_starglitter == starglitter_owned + simulation_settings.four_character_max_starglitter

@pytest.mark.parametrize(
    "item_name, item_type, item_rarity",
    [   
        ("Primordial Jade Winged Spear", "weapon", "five"),
        ("Favonius Sword", "weapon", "four"),
    ],
)
def test_starglitter_refund_weapons(items_to_process_state, simulation_results, simulation_settings, debug_state, item_name, item_type, item_rarity):
    state: IterationState = items_to_process_state
    starglitter_owned = state.masterless_starglitter 
    assert starglitter_owned == 0, "Starglitter starts at 0"

    process_items(items_to_process_state, debug_state, item_name, item_type, item_rarity)
    process_starglitter(items_to_process_state, simulation_results, simulation_settings, debug_state, item_name, item_type, item_rarity)
    if item_rarity == "five":
        assert state.masterless_starglitter == starglitter_owned + simulation_settings.five_weapon_starglitter
    elif item_rarity == "four":
        assert state.masterless_starglitter == starglitter_owned + simulation_settings.four_weapon_starglitter

@pytest.mark.parametrize(
    "item_name, item_type, item_rarity",
    [
        ("Mona", "character", "five"),
    ],
)
def test_masterless_fortuna_post_c6(items_to_process_state, simulation_results, simulation_settings, debug_state, item_name, item_type, item_rarity):
    masterless_fortuna_owned = simulation_results.total_masterless_fortuna_earned
    state: IterationState = items_to_process_state
    assert simulation_results.total_masterless_fortuna_earned== 0, "Masterless Fortuna starts at 0"
    assert state.characters["five"]["Mona"] == 6, "Character is C6 already!"

    process_items(items_to_process_state, debug_state, item_name, item_type, item_rarity)
    process_starglitter(items_to_process_state, simulation_results, simulation_settings, debug_state, item_name, item_type, item_rarity)

    assert simulation_results.total_masterless_fortuna_earned == masterless_fortuna_owned + simulation_settings.five_character_max_fortuna