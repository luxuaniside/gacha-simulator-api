from app.services.inventory_services import process_items

from app.models.iteration_state import IterationState
from app.models.simulation_settings import SimulationSettings, DebugState
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
                "Mona" : 1,
                "Diluc" : 6,
                },
            "four" : {}
        },
        weapons={
            "five" : {
                "Aquila Favonia" : 1,
                "Wolf's Gravestone" : 2,
                "Song of Broken Pines" : 5,
            },
            "four" : {}
        },
        
        )

@pytest.fixture
def simulation_settings() -> SimulationSettings:
    return SimulationSettings(1, False, False, 120)

@pytest.fixture
def debug_state():
    return DebugState()

@pytest.mark.parametrize(
    "item_name, item_type, item_rarity, expected_value",
    [   
        ("Amber", "character", "four", 0), # Unowned Becomes Owned
        ("Yumemizuki Mizuki", "character", "five", 0),
        ("Jean", "character", "five", 1), 
        ("Mona", "character", "five", 2),
        ("Diluc", "character", "five", 7),
        ("Favonius Sword", "weapon", "four", 1), # Unowned Becomes Owned
        ("Aquila Favonia", "weapon", "five", 2),
        ("Wolf's Gravestone", "weapon", "five", 3),
        ("Song of Broken Pines", "weapon", "five", 6)
    ],
)
def test_process_items(items_to_process_state, debug_state, item_name, item_type, item_rarity, expected_value):
    state: IterationState = items_to_process_state
    process_items(items_to_process_state, debug_state, item_name, item_type, item_rarity)
    if item_type == "character" and item_rarity == "five":
        assert state.characters["five"][item_name] == expected_value
    if item_type == "character" and item_rarity == "four":
        assert state.characters["four"][item_name] == expected_value
    if item_type == "weapon" and item_rarity == "five":
        assert state.weapons["five"][item_name] == expected_value
    if item_type == "weapon" and item_rarity == "four":
        assert state.weapons["four"][item_name] == expected_value