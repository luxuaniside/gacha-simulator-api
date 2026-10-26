from dataclasses import dataclass, field
from typing import Literal
import uuid
@dataclass
class Banner:
    """
    Represents a character or weapon banner configuration.
    Goals pull from items within them.

    Attributes:
        banner_name (str): Name of the banner.
        banner_five_item_primary (str): Primary featured 5-star item.
        banner_five_item_secondary (str | None): Secondary featured 5-star item, generally for weapon banners.
        banner_four_items (list[str]): List of featured 4-star items.
        item_type (Literal["character, "weapon"]): Type of banner, either character or weapon.
        banner_uuid (uuid.UUID): Unique identifier for the banner, generated automatically
            if not provided.
    """

    banner_name: str
    banner_five_item_primary: str
    banner_five_item_secondary: str | None
    banner_four_items: list
    item_type: Literal["character", "weapon"]
    banner_uuid: uuid.UUID = field(default_factory=uuid.uuid4)