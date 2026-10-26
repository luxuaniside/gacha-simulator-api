from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID, uuid4
from app.models.banners_state import Banner

class CreateBanner(BaseModel):
    """Schema for creating a simulation banner."""

    banner_name: str = Field(
        description="Name identifying the banner."
    )
    banner_five_item_primary: str = Field(
        min_length=1,
        description="Name of the primary five-star item available on the banner."
    )
    banner_five_item_secondary: str | None = Field(
        default=None,
        min_length=1,
        description="Name of the secondary five-star item, if applicable."
    )
    banner_four_items: list[str] = Field(
        min_length=0,
        description="Names of the four-star items available on the banner."
    )
    item_type: Literal["character", "weapon"] = Field(
        description="Type of banner: character or weapon."
    )
    banner_uuid: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier automatically generated for the banner."
    )


class BannerValidationRequest(BaseModel):
    """Request schema for validating a new banner against existing banners."""

    existing_banners: list[Banner] = Field(
        description="Banners already present in the simulation, "
                    "used to validate the new banner."
    )
    new_banner: CreateBanner = Field(
        description="Banner to validate against the existing banners."
    )