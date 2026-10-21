from app.services.goal_services import validate_goal, automatic_goal_name
from app.models.banners_state import Banner
from app.models.goals_state import Goal
from app.schemas.goals import GoalValidationRequest, CreateGoal

from app.errors import APIException

import pytest
from dataclasses import replace

# Defining fixtures for pytest
@pytest.fixture
def banner():
    return Banner(
        banner_name="Example Banner",
        banner_five_item_primary="Example Character",
        banner_five_item_secondary=None,
        banner_four_items=["Example 1", "Example 2", "Example 3"],
        item_type="character",
    )

@pytest.fixture
def goal_validation_request(banner):
    return GoalValidationRequest(
        existing_goals=[],
        new_goal=CreateGoal(
            goal_name="C0 Venti",
            item_name="Venti",
            goal_banner=banner,
            item_type = "character",
            item_rarity = "five",
            item_target_count = 0,
            item_high_priority=True,
            goal_uuid="7f4656ef-0c64-48c4-885b-59dde6a190de"
        
        )
    )
    
@pytest.fixture
def editing_goal_name_to_existing_one(banner):
    return GoalValidationRequest(
        existing_goals=[Goal(
            goal_name="TOTALLY Original Name",
            item_name="Venti",
            goal_banner=banner,
            item_type = "character",
            item_rarity = "five",
            item_target_count = 0,
            item_high_priority=True)],
        new_goal=CreateGoal(
            goal_name="TOTALLY Original Name",
            item_name="Raiden Shogun",
            goal_banner=banner,
            item_type = "character",
            item_rarity = "five",
            item_target_count = 0,
            item_high_priority=True,
        )
    )    
      
      
@pytest.fixture
def no_banner_goal_validation_request(goal_validation_request: GoalValidationRequest):
    new_goal = goal_validation_request.new_goal.model_copy(
        update={"goal_banner": None}
    )

    return goal_validation_request.model_copy(
        update={"new_goal": new_goal}
    )
 
@pytest.fixture    
def one_existing_goal_validation_request(goal_validation_request: GoalValidationRequest, banner):
    new_goal: CreateGoal = goal_validation_request.new_goal
    one_existing_goal_validation_request = goal_validation_request.model_copy(
        update={"existing_goals" : [Goal(
            goal_name=new_goal.goal_name,
            item_name="Venti",
            goal_banner=banner,
            item_type = "character",
            item_rarity = "five",
            item_target_count = 0,
            item_high_priority=True,
            goal_uuid = new_goal.goal_uuid
            
        )]
        }
    )
    return one_existing_goal_validation_request

def test_goal_validation_no_banner(no_banner_goal_validation_request: GoalValidationRequest):
    with pytest.raises(APIException) as exc_info:
        validate_goal(no_banner_goal_validation_request)
    
    assert exc_info.value.status_code == 400
    
@pytest.mark.parametrize(
    "item_type, target_count, expected_status_code",
    [
        ("character", -1, 400),
        ("character", 7, 400),
        ("weapon", 0, 400),
        ("weapon", 6, 400),
   ]
)
def test_goal_validation_under_or_over_item_target_count(goal_validation_request: GoalValidationRequest, item_type, target_count, expected_status_code):
    new_goal = goal_validation_request.new_goal.model_copy(
        update={"item_type" : item_type, "item_target_count" : target_count}
    )
    
    new_validation_request = goal_validation_request.model_copy(
        update={"new_goal": new_goal}
    )
   
    with pytest.raises(APIException) as exc_info:
        validate_goal(new_validation_request)
    
    assert exc_info.value.status_code == expected_status_code
    
@pytest.mark.parametrize(
    "item_type, target_count",
    [
        ("character", 0),
        ("character", 6),
        ("weapon", 1),
        ("weapon", 5),
   ]
)
def test_goal_validation_request_valid_item_target_inputs(goal_validation_request: GoalValidationRequest, item_type, target_count):
    new_goal = goal_validation_request.new_goal.model_copy(
        update={"item_type" : item_type, "item_target_count" : target_count}
    )
    
    new_validation_request = goal_validation_request.model_copy(
        update={"new_goal": new_goal}
    )
   
    validate_goal(new_validation_request)   

def test_goal_validation_creating_goal_with_occupied_name(one_existing_goal_validation_request: GoalValidationRequest):
    with pytest.raises(APIException) as exc_info:
        validate_goal(one_existing_goal_validation_request)
        
    assert exc_info.value.status_code == 409    
    
def test_goal_validation_editing_goal_with_same_uuid_allows_bypasses_same_name_error(one_existing_goal_validation_request: GoalValidationRequest):
    validate_goal(one_existing_goal_validation_request, allow_existing_goal_uuid=True)
    
def test_goal_validation_editing_goal_to_already_existing_name_with_different_uuid_raises_exception(editing_goal_name_to_existing_one: GoalValidationRequest):
    with pytest.raises(APIException) as exc_info:
        validate_goal(editing_goal_name_to_existing_one, allow_existing_goal_uuid=True)
        
    assert exc_info.value.status_code == 409    
        
