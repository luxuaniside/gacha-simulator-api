from pydantic import BaseModel, Field
from typing import Literal

class Resources(BaseModel):
    intertwined_fates: int = Field(default=90, ge=0, le=3_000)
    primogems: int = Field(default=0, ge=0, le=480_00)
    genesis_crystals: int = Field(default=0, ge=0, le=480_000)
    masterless_starglitter: int = Field(default=0, ge=0, le=15_000)

class Pity(BaseModel):
    five_character_pity: int = Field(ge=0, le=90, default=0)
    four_character_pity: int = Field(ge=0)
    five_weapon_pity: int = Field(ge=0, le=80, default=0)
    four_weapon_pity: int = Field(ge=0)
    five_character_guarantee: bool = Field(default=False)
    four_character_guarantee: bool = Field(default=False)
    five_weapon_guarantee: bool = Field(default=False)
    four_weapon_guarantee: bool = Field(default=False)
    epitomized_path: Literal[0, 1]
    capturing_radiance: Literal[0, 1, 2, 3]

class Characters(BaseModel):
    five: dict[str, int] = Field(default_factory=dict)
    four: dict[str, int] = Field(default_factory=dict)


