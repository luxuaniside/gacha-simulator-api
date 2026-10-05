from fastapi import APIRouter
from app.schemas.goals import GoalValidationRequest
from app.services.goal_services import validate_goal

router = APIRouter(
    prefix="/goals",
    tags=["Goals"]
)

@router.post("")
def create_goal(request: GoalValidationRequest):
    return validate_goal(request)

@router.post("/edit")
def edit_goal(request: GoalValidationRequest):
    new_goal = validate_goal(request, allow_existing_goal_uuid=True)
    assert new_goal.goal_banner is not None
    
    for existing_goal in request.existing_goals:
        if existing_goal.goal_uuid == new_goal.goal_uuid:
            existing_goal.goal_name = new_goal.goal_name
            existing_goal.item_name = new_goal.item_name
            existing_goal.goal_banner = new_goal.goal_banner
            existing_goal.item_type = new_goal.item_type
            existing_goal.item_rarity = new_goal.item_rarity
            existing_goal.item_target_count = new_goal.item_target_count
            existing_goal.item_high_priority = new_goal.item_high_priority
            
            return existing_goal