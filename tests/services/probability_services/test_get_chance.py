from app.services.probability_services import get_chance
from app.models.iteration_state import IterationState
from app.models.simulation_settings import SimulationSettings, DebugState
import pytest

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
def simulation_settings() -> SimulationSettings:
    return SimulationSettings(1, False, False, 120)


@pytest.fixture
def debug_state():
    return DebugState()

@pytest.mark.parametrize(
    "item_type, rarity, pity, expected_chance",
    [
        ("character", "four", 1, 0.051),
        ("character", "four", 8, 0.051),  # Edge of soft pity
        ("character", "four", 9, 0.051+0.051*10),  # Soft pity onset
        ("character", "four", 10, 1.0),  # Hard pity

        ("character", "five", 1, 0.006),
        ("character", "five", 73, 0.006),  # Edge of soft pity
        ("character", "five", 74, 0.006+0.006*10),  # Soft pity onset
        ("character", "five", 90, 1.0),  # Hard pity

        ("weapon", "four", 1, 0.06),
        ("weapon", "four", 7, 0.06),  # Edge of soft pity
        ("weapon", "four", 8, 0.06+0.06*10),  # Soft pity onset
        ("weapon", "four", 9, 1.0),  # Hard pity
        ("weapon", "four", 10, 1.0),  # Hard pity, but the advertised value!
        

        ("weapon", "five", 1, 0.007),
        ("weapon", "five", 62, 0.007),  # Edge of soft pity
        ("weapon", "five", 63, 0.007+0.007*10),  # Edge of soft pity
        ("weapon", "five", 77, 1.0),  # Hard pity
        ("weapon", "five", 80, 1.0),  # Hard pity, but the advertised value! 
    ],
)
def test_get_chance(
    iteration_state,
    simulation_settings,
    debug_state,
    item_type,
    rarity,
    pity,
    expected_chance,
):
    chance = get_chance(
        iteration_state, simulation_settings, debug_state, item_type, rarity, pity
    )
    assert chance == pytest.approx(expected_chance)