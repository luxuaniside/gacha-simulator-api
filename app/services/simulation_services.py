from app.models.iteration_state import WishState
from app.models.simulation_settings import SimulationSettings, DebugState
from app.models.simulation_results import SimulationResults
from app.api.simulation import SimulationRequest
from app.simulation.engine import run_simulation
from app.services.inventory_services import calculate_initial_wishes

def instance_simulation(request: SimulationRequest):
    starting_wishes, masterless_starglitter = calculate_initial_wishes(
        request.resources.intertwined_fates,
        request.resources.primogems,
        request.resources.genesis_crystals,
        request.resources.masterless_starglitter
    )

    wish_state = WishState(
        intertwined_fates=starting_wishes,
        masterless_starglitter=masterless_starglitter,
        five_character_pity=request.pity.five_character_pity,
        four_character_pity=request.pity.four_character_pity,
        five_weapon_pity=request.pity.five_weapon_pity,
        four_weapon_pity=request.pity.four_weapon_pity,
        five_character_guarantee=request.pity.five_character_guarantee,
        four_character_guarantee=request.pity.four_character_guarantee,
        five_weapon_guarantee=request.pity.five_weapon_guarantee,
        four_weapon_guarantee=request.pity.four_weapon_guarantee,
        epitomized_path=request.pity.epitomized_path,
        capturing_radiance=request.pity.capturing_radiance,
        characters=request.characters.model_dump(),
        weapons = {"five" : {},"four" : {}},
        goals=request.goals,
        banners=request.banners
    )
    initialized_simulation_results = SimulationResults()
    initialized_debug_state = DebugState()

    settings = SimulationSettings(
        request.simulation_settings.iteration_count,
        request.simulation_settings.starglitter_refund,
        request.simulation_settings.continue_after_goals_are_finished

    )

    results = run_simulation(wish_state, initialized_simulation_results, settings, initialized_debug_state)
    return results