from app.schemas.banners import BannerValidationRequest, CreateBanner
from app.services.banner_services import validate_banner
from app.errors import APIException
import pytest

@pytest.fixture
def character_banner_validation_request():
    return BannerValidationRequest(
        existing_banners=[],
        new_banner=CreateBanner(
            banner_name="Test Character Banner",
            banner_five_item_primary="Venti",
            banner_five_item_secondary=None,
            banner_four_items=["Bennett", "Fischl", "Sucrose"],
            item_type = "character"
        )
    )
    
    
@pytest.fixture    
def no_primary_character_request(character_banner_validation_request: BannerValidationRequest):
    new_banner = character_banner_validation_request.new_banner.model_copy(
        update={"banner_five_item_primary" : None}
    )
    
    no_primary_character_request = character_banner_validation_request.model_copy(
        update={"new_banner" : new_banner}
    )
    
    return no_primary_character_request

@pytest.fixture    
def character_list_not_three_state(character_banner_validation_request: BannerValidationRequest):
    new_banner = character_banner_validation_request.new_banner.model_copy(
        update={"banner_four_items" : []}
    )
    
    character_list_not_three_state = character_banner_validation_request.model_copy(
        update={"new_banner" : new_banner}
    )
    
    return character_list_not_three_state

@pytest.fixture    
def four_character_list_repeats(character_banner_validation_request: BannerValidationRequest):
    new_banner = character_banner_validation_request.new_banner.model_copy(
        update={"banner_four_items" : ["Bennett", "Sucrose", "Bennett"]}
    )
    
    four_character_list_repeats = character_banner_validation_request.model_copy(
        update={"new_banner" : new_banner}
    )
    
    return four_character_list_repeats

# Character
def test_correct_character_banner_data(character_banner_validation_request: BannerValidationRequest):
    validate_banner(character_banner_validation_request)

def test_banner_validation_no_primary_character(no_primary_character_request: BannerValidationRequest):
    with pytest.raises(APIException) as exc_info:
        validate_banner(no_primary_character_request)
    assert exc_info.value.code == "banner_no_primary_character_selected"
    assert exc_info.value.status_code == 400
    
def test_banner_validation_wrong_amount_of_four_characters(character_list_not_three_state: BannerValidationRequest):
    with pytest.raises(APIException) as exc_info:
        validate_banner(character_list_not_three_state)
    assert exc_info.value.code == "banner_wrong_four_characters_amount_selected"
    assert exc_info.value.status_code == 400
    
def test_banner_validation_character_list_repeats(four_character_list_repeats: BannerValidationRequest):
    with pytest.raises(APIException) as exc_info:
        validate_banner(four_character_list_repeats)
    assert exc_info.value.code == "banner_duplicate_four_star_characters_selected"
    assert exc_info.value.status_code == 400

