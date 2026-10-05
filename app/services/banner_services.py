from app.errors import APIException
from app.models.banners_state import Banner
from app.schemas.banners import BannerValidationRequest

def automatic_banner_name(banner_five_item_primary, banner_five_item_secondary, banner_four_items, item_type):
    #Character
    if item_type == "character":
        banner_name = f"{banner_five_item_primary} + ({', '.join(banner_four_items)})"
    #Weapon
    else: 
        banner_name = f"{banner_five_item_primary} + {banner_five_item_secondary}"

    return banner_name

def validate_banner(request: BannerValidationRequest):
    new_banner = request.new_banner
    if new_banner.item_type == "character":
        if not new_banner.banner_five_item_primary:
            raise APIException(
                code="banner_no_primary_character_selected",
                message="Please select a 5✦ Character!",
            )
        if len(new_banner.banner_four_items) != 3:
            raise APIException(
                code="banner_wrong_four_characters_amount_selected",
                message="You must select three different 4✦ Characters!",
            )
    if new_banner.item_type == "weapon": 
        #Check if both weapons have an item
        if not new_banner.banner_five_item_primary or not new_banner.banner_five_item_secondary:
            raise APIException(
                code="banner_primary_or_secondary_weapon_missing",
                message="Please select two different 5★ Weapons!"
        )
        
        #Check if 5* weapons are differnt
        if new_banner.banner_five_item_primary == new_banner.banner_five_item_secondary:
            raise APIException(
                code="banner_same_weapons_selected",
                message="The chosen 5★ Weapons must be different!"
            )
        #Check if there's 5 four star items
        if len(new_banner.banner_four_items) != 5:
            raise APIException(
                code="banner_wrong_four_weapons_amount_selected",
                message="You must choose five different 4★ Weapons!"
            )
        
    if not new_banner.banner_name:
        new_banner.banner_name =  automatic_banner_name(new_banner.banner_five_item_primary, new_banner.banner_five_item_secondary, new_banner.banner_four_items, new_banner.item_type)

    for existing_banner in request.existing_banners:
        if existing_banner.banner_name == request.new_banner.banner_name and existing_banner.banner_uuid != new_banner.banner_uuid:
            raise APIException(
                code="duplicate_banner_name",
                message="A banner with that name already exists. Try something else.",
                status_code=409
            )
        
    return request.new_banner
