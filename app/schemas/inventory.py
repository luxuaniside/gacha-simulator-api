from pydantic import BaseModel, Field
from typing import Literal

class Resources(BaseModel):
    """Initial resources available to the simulation."""

    intertwined_fates: int = Field(
        default=90,
        ge=0,
        le=3_000,
        description="Number of Intertwined Fates available initially."
    )
    primogems: int = Field(
        default=0,
        ge=0,
        le=48_000,
        description="Number of Primogems available initially."
    )
    genesis_crystals: int = Field(
        default=0,
        ge=0,
        le=480_000,
        description="Number of Genesis Crystals available initially."
    )
    masterless_starglitter: int = Field(
        default=0,
        ge=0,
        le=15_000,
        description="Amount of Masterless Starglitter available initially."
    )


class Pity(BaseModel):
    """Initial pity counters and guarantee states for each banner type."""

    five_character_pity: int = Field(
        default=0,
        ge=0,
        le=90,
        description="Number of wishes since the last five-star character "
                    "on the character event banner."
    )
    four_character_pity: int = Field(
        default=0,
        ge=0,
        description="Number of wishes since the last four-star item "
                    "on the character event banner."
    )
    five_weapon_pity: int = Field(
        default=0,
        ge=0,
        le=80,
        description="Number of wishes since the last five-star weapon "
                    "on the weapon event banner."
    )
    four_weapon_pity: int = Field(
        default=0,
        ge=0,
        description="Number of wishes since the last four-star item "
                    "on the weapon event banner."
    )
    five_character_guarantee: bool = Field(
        default=False,
        description="Whether the next five-star character event-banner "
                    "drop is guaranteed to be a featured character."
    )
    four_character_guarantee: bool = Field(
        default=False,
        description="Whether the next four-star character event-banner "
                    "drop is guaranteed to be a featured item."
    )
    five_weapon_guarantee: bool = Field(
        default=False,
        description="Whether the next five-star weapon-banner drop is "
                    "guaranteed to be a featured weapon."
    )
    four_weapon_guarantee: bool = Field(
        default=False,
        description="Whether the next four-star weapon-banner drop is "
                    "guaranteed to be a featured item."
    )
    epitomized_path: Literal[0, 1] = Field(
        default=0,
        description="Initial Epitomized Path fate-point state."
    )
    capturing_radiance: Literal[0, 1, 2, 3] = Field(
        default=0,
        description="Initial Capturing Radiance state used by the simulation."
    )


class Characters(BaseModel):
    """Initial owned character and weapon copy counts."""

    five: dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of five-star item names to the number of copies owned."
    )
    four: dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of four-star item names to the number of copies owned."
    )