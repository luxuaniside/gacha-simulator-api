from app.models.banners_state import Banner
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
def duplicate_name_with_diff_uuid():
    return BannerValidationRequest(
        existing_banners=[
            Banner(
                banner_name="Duplicate Banner Name",
                banner_five_item_primary="Venti",
                banner_five_item_secondary=None,
                banner_four_items = ["1", "2", "3"],
                item_type = "character"
            )
        ],
        new_banner=CreateBanner(
                banner_name="Duplicate Banner Name",
                banner_five_item_primary="Freedom Sworn",
                banner_five_item_secondary="Summit Shaper",
                banner_four_items = ["1", "2", "3", "4", "5"],
                item_type = "weapon"
        )
    )
    


@pytest.fixture
def duplicate_banner_request(character_banner_validation_request: BannerValidationRequest):
    existing_banner: CreateBanner = character_banner_validation_request.new_banner
    existing_banner = Banner(
        banner_name = existing_banner.banner_name,
        banner_five_item_primary= existing_banner.banner_five_item_primary,
        banner_five_item_secondary=existing_banner.banner_five_item_secondary,
        banner_four_items=["1", "2", "3"],
        item_type="character",
        banner_uuid=existing_banner.banner_uuid
        
        
    )
    
    return BannerValidationRequest(
        existing_banners=[existing_banner],
        new_banner=CreateBanner(
            banner_name="Test Character Banner",
            banner_five_item_primary="Venti",
            banner_five_item_secondary=None,
            banner_four_items=["Bennett", "Fischl", "Sucrose"],
            item_type = "character",
            banner_uuid=existing_banner.banner_uuid            
            
        )
    )

def test_validation_duplicate_name_request_fails(duplicate_banner_request: BannerValidationRequest):
    with pytest.raises(APIException) as exc_info:
        validate_banner(duplicate_banner_request)
        
    assert exc_info.value.code == "duplicate_banner_name"
    assert exc_info.value.status_code == 409
    
def test_validation_duplicate_name_request_doesnt_fail_if_editing_and_same_uuid(duplicate_banner_request: BannerValidationRequest):
    validate_banner(duplicate_banner_request, allow_existing_banner_uuid=True)


def test_validation_duplicate_name_request_fails(duplicate_name_with_diff_uuid: BannerValidationRequest):
    with pytest.raises(APIException) as exc_info:
        validate_banner(duplicate_name_with_diff_uuid, allow_existing_banner_uuid=True)
        
    assert exc_info.value.code == "duplicate_banner_name"
    assert exc_info.value.status_code == 409
    