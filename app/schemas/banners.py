from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID, uuid4
from app.models.banners_state import Banner

class CreateBanner(BaseModel):
    banner_name: str
    banner_five_item_primary: str = Field(min_length=1)
    banner_five_item_secondary: str | None = Field(
        default=None,
        min_length=1
    )
    banner_four_items: list[str] = Field(min_length=0)   
    item_type: Literal["character", "weapon"]
    banner_uuid: UUID = Field(default_factory=uuid4)
    

class BannerValidationRequest(BaseModel):
    existing_banners: list[Banner]
    new_banner: CreateBanner
