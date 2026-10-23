from app.errors import APIException
from app.models.goals_state import Goal
from app.schemas.goals import GoalValidationRequest, CreateGoal

from app.models.iteration_state import IterationState
from app.models.simulation.simulation_settings import DebugState
import logging

logger = logging.getLogger(__name__)

def automatic_goal_name(item_type: str, item_target_count: int, item_name:str , item_high_priority: bool) -> str:
    """Creates a goal name if none was inputted.

    Args:
        item_type (str): Item category. Must be "character" or "weapon".
        item_target_count (int): Amount of copies expected.
        item_name (str): Name of the item.
        item_high_priority (bool): Whether or not the item is high priority.

    Raises:
        ValueError: If item type isn't character or weapon.
    Returns:
        goal_name (str): Automatically generated goal name.
        
    """
    #Character
    if item_type == "character":
        goal_name = f"C{item_target_count} {item_name}"
    #Weapon
    elif item_type == "weapon":
        goal_name = f"R{item_target_count} {item_name}"
    else:
        raise ValueError("item_type isn't character or weapon")
    if not item_high_priority:
        goal_name += " (Low Priority)"

    return goal_name

def get_current_goal(iteration_state: IterationState, debug_state: DebugState) -> tuple[Goal, bool]:
    """Obtains the first non-fulfilled goal from the goals iteration_state list.

    Args:
        iteration_state (IterationState): Contains the goals list.
        debug_state (DebugState): Logging goals info configuration.

    Returns:
        tuple[Goal, bool]: 
            * **goal (Goal)**: Current goal to process.
            * **all_goals_complete (bool)**: A flag that tells the engine that all goals have been fulfilled, or not.
    """
    while iteration_state.current_goal_index < len(iteration_state.goals):
        goal: Goal = iteration_state.goals[iteration_state.current_goal_index]

        #Set up inventory
        if goal.item_type == "character":
            inventory = iteration_state.characters[goal.item_rarity]
        else:
            inventory = iteration_state.weapons[goal.item_rarity]
        

        current_copies = inventory.get(goal.item_name, -1)

        #If item has enough copies to surpass the requirement, or is not high priority, move on.
        if current_copies >= goal.item_target_count or goal.item_high_priority == False:
            iteration_state.current_goal_index +=1
            if debug_state.debug_current_goal:
                logger.debug(f"{goal.goal_name} {goal.item_name}, {current_copies}/{goal.item_target_count}, {goal.item_rarity}, {goal.item_type} GOAL FINISHED")
            continue
        
        if current_copies < goal.item_target_count:
            if debug_state.debug_current_goal:
                logger.debug(f"{goal.goal_name} {goal.item_name}, {current_copies}/{goal.item_target_count}, {goal.item_rarity}, {goal.item_type} GOAL NOT FINISHED")
            all_goals_complete = False
            return goal, all_goals_complete

    #Last goal
    goal: Goal = iteration_state.goals[-1]  
    all_goals_complete = True
    if debug_state.debug_current_goal:
        logger.debug(f"ALL GOALS FINISHED!")

    return goal, all_goals_complete

def validate_goal(request: GoalValidationRequest, allow_existing_goal_uuid: bool = False) -> CreateGoal:
    """General goal creation and editing validation.

    Args:
        request (GoalValidationRequest): Schema containing a list of existing goals and the new one to create.
        allow_existing_goal_uuid (bool, optional): Boolean to toggle whether or not to allow a goal with an already occupied UUID to be validated. Generally used for goal editing, as they will have the same UUID. Defaults to False.

    Raises:
        APIException: When new_goal does not have a banner. (400) 
        APIException: When the item target count is not within the specified range for character. (400)
        APIException: When the item target count is not within the specified range for weapons. (400)
        APIException: When there is an attempt to create a goal with a name that currently is occupied. (409)

    Returns:
        CreateGoal: Goal Schema.
    """
    new_goal = request.new_goal
    if new_goal.goal_banner is None:
        raise APIException(
            code="goal_banner_missing",
            message="No banner selected. Create one to continue."
        )

    if new_goal.item_type == "character":
        if new_goal.item_target_count < 0 or new_goal.item_target_count > 6:
            raise APIException(
                code="invalid_constellation_target",
                message="Constellation Target must be between C0 and C6!"
            ) 
    elif new_goal.item_type == "weapon":
        if new_goal.item_target_count < 1 or new_goal.item_target_count > 5:
            raise APIException(
                code="invalid_refinement_target",
                message="Refinement Target must be between R1 and R5!"
            ) 


    # If no name exists, automatically create one.
    if not new_goal.goal_name:
        new_goal.goal_name = automatic_goal_name(new_goal.item_type, new_goal.item_target_count, new_goal.item_name, new_goal.item_high_priority)

    for existing_goal in request.existing_goals:
        is_same_goal = existing_goal.goal_uuid == new_goal.goal_uuid
        
        if existing_goal.goal_name == new_goal.goal_name and (not allow_existing_goal_uuid or not is_same_goal):
            raise APIException(
                code="duplicate_goal_name",
                message="A goal with that name already exists. Try something else!",
                status_code=409
            )

    return request.new_goal
