from fastapi import APIRouter
from app.schemas.banners import BannerValidationRequest
from app.services.banner_services import validate_banner

router = APIRouter(
    prefix="/banners",
    tags=["Banners"]
)

@router.post("")
def create_banner(request: BannerValidationRequest):
    return validate_banner(request)
    
@router.post("/edit")
def edit_banner(request: BannerValidationRequest):
    new_banner = validate_banner(request)
    
    for existing_banner in request.existing_banners:
        if existing_banner.banner_uuid == new_banner.banner_uuid:
            existing_banner.banner_name = new_banner.banner_name
            existing_banner.banner_five_item_primary = new_banner.banner_five_item_primary
            existing_banner.banner_five_item_secondary = new_banner.banner_five_item_secondary
            existing_banner.banner_four_items = new_banner.banner_four_items
            existing_banner.item_type = new_banner.item_type

            return existing_banner