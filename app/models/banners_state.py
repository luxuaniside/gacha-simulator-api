from dataclasses import dataclass, field
from typing import Literal
import uuid
@dataclass
class Banner:
    banner_name: str
    banner_five_item_primary: str
    banner_five_item_secondary: str | None
    banner_four_items: list
    item_type: Literal["character", "weapon"]
    banner_uuid: uuid.UUID = field(default_factory=uuid.uuid4)