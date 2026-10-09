from copy import deepcopy
from collections.abc import Callable
import random
import logging
import time

from app.models.iteration_state import WishState
from app.models.goals_state import Goal
from app.models.simulation_results import SimulationResults, FinalSimulationResults
from app.models.simulation_settings import SimulationSettings, DebugState

from app.services.probability_services import get_chance
from app.services.inventory_services import get_item, process_items, process_starglitter
from app.services.goal_services import get_current_goal

logger = logging.getLogger(__name__)

def record_goal_wishes(
    iteration_state: WishState,
    previous_goal: Goal,
    current_goal: Goal,
    all_goals_finished: bool,
) -> None:
    if previous_goal != current_goal or all_goals_finished:
        iteration_state.wishes_spent_in_goal[previous_goal.goal_name] = (
            iteration_state.wishes_used_for_goal_counter
        )
        if previous_goal != current_goal:
            iteration_state.wishes_used_for_goal_counter = 0


def run_simulation(
    initialized_iteration_state: WishState,
    simulation_results: SimulationResults,
    simulation_settings: SimulationSettings,
    debug_state: DebugState,
    progress_callback: Callable[[int, int], None] | None = None,
):
    simulation_start = time.time()
    goal_results = {}
    state_collection_wishes_spent_in_goal = []

    total_iterations = simulation_settings.iterations
    progress_interval = max(1, (total_iterations + 99) // 100)

    for iteration in range(total_iterations):
        iteration_state = deepcopy(initialized_iteration_state)

        engine(iteration_state, simulation_results, simulation_settings, debug_state)
        results = iteration_results(iteration_state,)

        for goal, val in results.items():
            goal_results[goal] = goal_results.get(goal, 0) + val

        state_collection_wishes_spent_in_goal.append(iteration_state.wishes_spent_in_goal)

        completed_iterations = iteration + 1
        if progress_callback and (
            completed_iterations % progress_interval == 0
            or completed_iterations == total_iterations
        ):
            progress_callback(completed_iterations, total_iterations)

    
    
    average_wishes_used = simulation_results.total_wishes_used / simulation_settings.iterations
    average_masterless_starglitter_earned = simulation_results.total_starglitter_earned / simulation_settings.iterations
    average_masterless_fortuna_earned = simulation_results.total_masterless_fortuna_earned / simulation_settings.iterations
    average_masterless_stardust_earned = simulation_results.total_stardust_earned / simulation_settings.iterations

    if simulation_settings.starglitter_refund and average_wishes_used>0:
        average_masterless_starglitter_refund = average_wishes_used/(average_wishes_used-average_masterless_starglitter_earned/simulation_settings.starglitter_to_wish_cost)
    else: 
        average_masterless_starglitter_refund = 0
    
    return FinalSimulationResults(
        finished_goals=goal_results,
        simulation_time=time.time()-simulation_start,
        average_wishes_used=average_wishes_used,
        average_masterless_starglitter_earned=average_masterless_starglitter_earned,
        average_masterless_starglitter_refund=average_masterless_starglitter_refund,
        average_masterless_fortuna_earned=average_masterless_fortuna_earned,
        average_masterless_stardust_earned=average_masterless_stardust_earned,
        starting_wishes=initialized_iteration_state.intertwined_fates,
        total_wishes_spent_in_goal=state_collection_wishes_spent_in_goal
    )

def engine(iteration_state: WishState, simulation_results: SimulationResults, simulation_settings: SimulationSettings, debug_state: DebugState):
 
    goal, all_goals_finished = get_current_goal(iteration_state, debug_state) #Tuple (Goal, Bool)
    

    #Iteration keeps going until there's no wishes left OR you have enough starglitter to refund AND starglitter refund is enabled.
    while iteration_state.intertwined_fates > 0 or (iteration_state.masterless_starglitter >= simulation_settings.starglitter_to_wish_cost and simulation_settings.starglitter_refund):

        if all_goals_finished and simulation_settings.continue_after_goals_are_finished == False:
            break

        iteration_state.intertwined_fates -= 1
        simulation_results.total_wishes_used +=1
        if all_goals_finished == False:
            iteration_state.wishes_used_for_goal_counter += 1


        if all_goals_finished and simulation_settings.continue_after_goals_are_finished == False:
            if debug_state.debug_alert_all_goals_are_finished:
                logger.debug(f"ITERATION {iteration_state.current_iteration} | Goals finished early!")
            #logger.debug(f"Loop (THROUGH GOALS IN SIMULATION()) ending: wishes={simulation_state.wishes}, "f"starglitter={simulation_state.starglitter}")
            break

        #Handle pity systems
        if goal.item_type == "character":
            iteration_state.five_character_pity += 1
            iteration_state.four_character_pity += 1
            five_pity = iteration_state.five_character_pity
            four_pity = iteration_state.four_character_pity

        if goal.item_type == "weapon":
            iteration_state.five_weapon_pity += 1
            iteration_state.four_weapon_pity += 1
            five_pity = iteration_state.five_weapon_pity
            four_pity = iteration_state.four_weapon_pity
        
        # Five stars have priority over four stars, if a five star is obtained, a four star will not, regardless of its chance.
        if random.random() < get_chance(iteration_state, simulation_settings, debug_state, goal.item_type, "five", five_pity):
            item_dropped, item_type = get_item(iteration_state, simulation_settings, simulation_results, debug_state, goal, "five")
            process_items(iteration_state, debug_state, item_dropped, item_type, "five")
            process_starglitter(iteration_state, simulation_results, simulation_settings, debug_state, item_dropped, item_type, "five")

            # Goal Handling            
            old_goal = goal
            goal, all_goals_finished = get_current_goal(iteration_state, debug_state) #Tuple (Goal, Bool

            record_goal_wishes(
                iteration_state,
                old_goal,
                goal,
                all_goals_finished,
            )
            if goal.item_type == "character":
                iteration_state.five_character_pity = 0
            elif goal.item_type == "weapon":
                iteration_state.five_weapon_pity = 0
            else:    
                raise KeyError("ITEM PASSED TO GET_ITEM() IS NOT character or weapon")               

        # Four Stars have higher priority over three stars            
        elif random.random() < get_chance(iteration_state, simulation_settings, debug_state, goal.item_type, "four", four_pity):
            item_dropped, item_type = get_item(iteration_state, simulation_settings, simulation_results, debug_state, goal, "four")
            process_items(iteration_state, debug_state, item_dropped, item_type, "four")
            process_starglitter(iteration_state, simulation_results, simulation_settings, debug_state, item_dropped, item_type, "four")

            # Goal Handling            
            old_goal = goal
            goal, all_goals_finished = get_current_goal(iteration_state, debug_state) #Tuple (Goal, Bool

            record_goal_wishes(
                iteration_state,
                old_goal,
                goal,
                all_goals_finished,
            )
                        
            
            if goal.item_type == "character":
                iteration_state.four_character_pity = 0
            elif goal.item_type == "weapon":
                iteration_state.four_weapon_pity = 0
            else:    
                raise KeyError("ITEM PASSED TO GET_ITEM() IS NOT character or weapon")
       
        #Three star obtained
        else:
            simulation_results.total_stardust_earned += simulation_settings.three_weapon_stardust

        if iteration_state.intertwined_fates == 0 and (iteration_state.masterless_starglitter >= simulation_settings.starglitter_to_wish_cost and simulation_settings.starglitter_refund):
            starglitter_refund = iteration_state.masterless_starglitter // simulation_settings.starglitter_to_wish_cost
            iteration_state.intertwined_fates += starglitter_refund
            if debug_state.debug_starglitter_refund:
                logger.debug(f"Refunding {starglitter_refund} Wishes from {iteration_state.masterless_starglitter} Starglitter at {simulation_settings.starglitter_to_wish_cost} a wish.")
            iteration_state.masterless_starglitter = iteration_state.masterless_starglitter % simulation_settings.starglitter_to_wish_cost
           
    # Record progress on unfinished goal
    if (
        not all_goals_finished
        and goal is not None
        and goal.goal_name not in iteration_state.wishes_spent_in_goal
    ):
        iteration_state.wishes_spent_in_goal[goal.goal_name] = (
            iteration_state.wishes_used_for_goal_counter
        )
    return simulation_results

def iteration_results(iteration_state: WishState):
    results = {}
    
    for goal in iteration_state.goals:
        fulfilled = False
        
        if goal.item_type == "character":
            inventory = iteration_state.characters[goal.item_rarity]
        else:
            inventory = iteration_state.weapons[goal.item_rarity] 

        current_copies = inventory.get(goal.item_name, -1)
        if current_copies >= goal.item_target_count:
            fulfilled = True

        results[goal.goal_name] = 1 if fulfilled else 0
    
    return results
