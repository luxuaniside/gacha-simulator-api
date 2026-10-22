from app.schemas.banners import BannerValidationRequest, CreateBanner
from app.services.banner_services import validate_banner
from app.errors import APIException
import pytest
    
@pytest.fixture
def weapon_banner_validation_request():
    return BannerValidationRequest(
        existing_banners=[],
        new_banner=CreateBanner(
            banner_name="Test Weapon Banner",
            banner_five_item_primary="Freedom Sworn",
            banner_five_item_secondary="Summit Shaper",
            banner_four_items=["Favonius Sword", "Favonius Lance", "Favonius Greatsword", "Favonius Codex", "Favonius Bow"],
            item_type = "weapon"
        )
    )
    
@pytest.fixture    
def weapon_list_not_five(weapon_banner_validation_request: BannerValidationRequest):
    new_banner = weapon_banner_validation_request.new_banner.model_copy(
        update={"banner_four_items" : []}
    )
    
    weapon_list_not_five = weapon_banner_validation_request.model_copy(
        update={"new_banner" : new_banner}
    )
    
    return weapon_list_not_five

@pytest.fixture    
def four_weapon_list_repeats(weapon_banner_validation_request: BannerValidationRequest):
    new_banner = weapon_banner_validation_request.new_banner.model_copy(
        update={"banner_four_items" : ["Favonius Sword", "Favonius Sword", "Favonius Greatsword", "Favonius Codex", "Favonius Bow"]}
    )
    
    four_weapon_list_repeats = weapon_banner_validation_request.model_copy(
        update={"new_banner" : new_banner}
    )
    
    return four_weapon_list_repeats


# Weapon
def test_correct_weapon_banner_data(weapon_banner_validation_request: BannerValidationRequest):
    validate_banner(weapon_banner_validation_request)
    
@pytest.mark.parametrize(
    "primary, secondary",
    [
        ("Summit Shaper", None),
        (None, "Freedom Sworn"),
        (None, None)
    ]
)
def test_banner_validation_missing_primary_secondary_items(weapon_banner_validation_request: BannerValidationRequest, primary, secondary):
    new_banner = weapon_banner_validation_request.new_banner.model_copy(
        update={"banner_five_item_primary" : primary, "banner_five_item_secondary" : secondary}
    )
    
    weapon_banner_validation_request = weapon_banner_validation_request.model_copy(
        update={"new_banner" : new_banner}
    )
    
    with pytest.raises(APIException) as exc_info:
        validate_banner(weapon_banner_validation_request)
        
    assert exc_info.value.code == "banner_primary_or_secondary_weapon_missing"
    assert exc_info.value.status_code == 400
    
def test_banner_validation_wrong_amount_of_four_weapons(weapon_list_not_five: BannerValidationRequest):
    with pytest.raises(APIException) as exc_info:
        validate_banner(weapon_list_not_five)
    assert exc_info.value.code == "banner_wrong_four_weapons_amount_selected"
    assert exc_info.value.status_code == 400
    
def test_banner_validation_weapon_list_repeats(four_weapon_list_repeats: BannerValidationRequest):
    with pytest.raises(APIException) as exc_info:
        validate_banner(four_weapon_list_repeats)
    assert exc_info.value.code == "banner_duplicate_four_star_weapons_selected"
    assert exc_info.value.status_code == 400