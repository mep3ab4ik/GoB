from time import time
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class BattleInvite(BaseModel):
    sender_username: str
    invited_username: str
    game_mode_id: int
    room_id: str = Field(default_factory=lambda: str(uuid4()))
    ticket_1: str = Field(default_factory=lambda: str(uuid4()))
    ticket_2: str = Field(default_factory=lambda: str(uuid4()))


class Card(BaseModel):
    id: int
    custom_id: str
    name: str
    description: str
    rarity: str
    type: str
    hp: int
    attack: int
    element: str

    class Config:
        orm_mode = True


class Deck(BaseModel):
    next_card: Optional[Card]


class Enchantment(BaseModel):
    id: int
    turns: Optional[int]
    card_hand: Optional[int]
    player: Optional[int]
    keyword: str
    type: str
    affects_hp: bool = False
    affects_attack: bool = False
    hp_change_value: Optional[int]
    attack_change_value: Optional[int]
    protect: Optional[int]
    active: bool


class Tile(BaseModel):
    id: int
    enchantments: dict[int, Enchantment] = Field(default_factory=dict)


class BattlePlayer(BaseModel):
    id: int
    deck: Optional[Deck]
    tiles: dict[int, Tile] = Field(default_factory=dict)


class Battle(BaseModel):
    players: dict[int, BattlePlayer]
    round_started_at: int = Field(default_factory=time)
    last_battle_card_id: int = 0
