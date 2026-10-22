from app.errors import APIException
from app.schemas.banners import BannerValidationRequest, CreateBanner

def automatic_banner_name(banner_five_item_primary: str, banner_five_item_secondary: str | None, banner_four_items: list[str], item_type: str) -> str:
    """Creates a banner name if none was inputted.

    Args:
        banner_five_item_primary (str): Primary five-star item.
        banner_five_item_secondary (str | None): Secondary five-star item. Mainly exists for weapon banners.
        banner_four_items (list[str]): List of four-star items.
        item_type (str): "character" or "weapon"
    Raises:
        ValueError: If item type isn't character or weapon.
    Returns:
        banner_name (str): Automatically generated banner name.
    """
    #Character
    if item_type == "character":
        banner_name = f"{banner_five_item_primary} + ({', '.join(banner_four_items)})"
    #Weapon
    elif item_type == "weapon": 
        banner_name = f"{banner_five_item_primary} + {banner_five_item_secondary}"
    else:
        raise ValueError("item_type isn't character or weapon")
    return banner_name

def validate_banner(request: BannerValidationRequest, allow_existing_banner_uuid: bool = False) -> CreateBanner:
    """General goal creation and editing vbalidation

    Args:
        request (BannerValidationRequest):  Schema containing a list of existing banners and the new one to create.
        allow_existing_banner_uuid (bool, optional): Boolean to toggle whether or not to allow a banner with an already occupied UUID to be validated. Generally used for banner editing, as they will have the same UUID. Defaults to False.


    Raises:
        APIException: No five-star character selected on character banner. (400)
        APIException: Four-star character list on character banner is not exactly three items. (400)
        APIException: Duplicate four-star characters selected on banner. (400)
        APIException: Primary and or secondary weapons are missing on weapon banner (400)
        APIException: The primary and secondary weapons are the same value (400)
        APIException: Four-star weapon list on weapon banner is not exactly five items. (400) 
        APIException: Duplicate four-star weapons selected on banner. (400)
        APIException: When there is an attempt to create a banner with a name that currently is occupied. (409)

    Returns:
        CreateBanner: Banner Schema
    """
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
            
        if len(new_banner.banner_four_items) != len(set(new_banner.banner_four_items)):
             raise APIException(
                    code="banner_duplicate_four_star_characters_selected",
                    message="There are repeating 4✦ Characters selected!"
             )
    if new_banner.item_type == "weapon": 
        #Check if both weapons have an item
        if not new_banner.banner_five_item_primary or not new_banner.banner_five_item_secondary:
            raise APIException(
                code="banner_primary_or_secondary_weapon_missing",
                message="Please select two different 5✦ Weapons!"
        )
        
        #Check if 5* weapons are differnt
        if new_banner.banner_five_item_primary == new_banner.banner_five_item_secondary:
            raise APIException(
                code="banner_same_weapons_selected",
                message="The chosen 5✦ Weapons must be different!"
            )
        #Check if there's 5 four star items
        if len(new_banner.banner_four_items) != 5:
            raise APIException(
                code="banner_wrong_four_weapons_amount_selected",
                message="You must choose five different 4✦ Weapons!"
            )
        if len(new_banner.banner_four_items) != len(set(new_banner.banner_four_items)):
             raise APIException(
                    code="banner_duplicate_four_star_weapons_selected",
                    message="There are repeating 4✦ Weapons selected!"
             )
    if not new_banner.banner_name:
        new_banner.banner_name =  automatic_banner_name(new_banner.banner_five_item_primary, new_banner.banner_five_item_secondary, new_banner.banner_four_items, new_banner.item_type)

    for existing_banner in request.existing_banners:
        is_same_banner = existing_banner.banner_uuid == new_banner.banner_uuid
        
        if existing_banner.banner_name == request.new_banner.banner_name and (not allow_existing_banner_uuid or not is_same_banner):
            raise APIException(
                code="duplicate_banner_name",
                message="A banner with that name already exists. Try something else.",
                status_code=409
            )
        
    return request.new_banner
