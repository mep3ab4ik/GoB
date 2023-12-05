from abc import ABC
from time import time
from typing import Optional, Union

from pydantic import BaseModel, Field

from app.schemas.friendship import FriendshipStatus
from app.schemas.ws_lobby_event_schemas import (
    EventRequestBattleInviteType,
    EventRequestFriendshipType,
    EventRequestPlayerStatusType,
    EventRequestType,
    EventResponseType,
)


class PlayerStatus(BaseModel):
    name: str
    title: str

    class Config:
        orm_mode = True


class EventResponseFriendshipParamsPlayer(BaseModel):
    player_id: str
    status: PlayerStatus
    username: str

    class Config:
        orm_mode = True
        use_enum_values = True


class EventResponseFriendshipParams(BaseModel):
    friend: EventResponseFriendshipParamsPlayer
    status: FriendshipStatus


class EventResponseMessageBase(BaseModel, ABC):
    event: EventResponseType
    timestamp: float = Field(default_factory=time)


class EventResponseFriendshipListMessage(EventResponseMessageBase):
    params: list[EventResponseFriendshipParams]


class EventResponseFriendshipReceiveMessage(EventResponseMessageBase):
    params: list[EventResponseFriendshipParams]


class EventResponseFriendshipSendMessage(EventResponseMessageBase):
    params: EventResponseFriendshipParams


class EventRequestFriendshipPayload(BaseModel):
    to_username: str


class EventRequestMessageBase(BaseModel, ABC):
    event: EventRequestType


class EventRequestFriendshipMessage(EventRequestMessageBase):
    event: EventRequestFriendshipType
    params: EventRequestFriendshipPayload


class EventBattleInviteMessagePayload(BaseModel):
    to_username: str
    game_mode_id: Optional[int]


class EventRequestBattleInviteMessage(EventRequestMessageBase):
    event: EventRequestBattleInviteType
    params: EventBattleInviteMessagePayload


class EventResponseBattleInviteMessage(EventResponseMessageBase):
    params: EventBattleInviteMessagePayload


class EventResponseBattleInviteAcceptMessagePayload(BaseModel):
    room_id: str
    ticket: str


class EventResponseBattleInviteAcceptMessage(EventResponseMessageBase):
    params: EventResponseBattleInviteAcceptMessagePayload


class EventResponseErrorMessage(EventResponseMessageBase):
    event = EventResponseType.ERROR
    params: Optional[dict]


class EventRequestPlayerStatusPayload(BaseModel):
    status_name: Optional[str]


class EventRequestPlayerStatusMessage(EventRequestMessageBase):
    event: EventRequestPlayerStatusType
    params: EventRequestPlayerStatusPayload


EventResponseMessageRoot = Union[
    EventRequestFriendshipMessage,
    EventRequestBattleInviteMessage,
    EventResponseErrorMessage,
    EventRequestPlayerStatusMessage,
]


class EventResponseMessage(BaseModel):
    __root__: EventResponseMessageRoot
