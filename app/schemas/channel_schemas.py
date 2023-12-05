from abc import ABC
from typing import Union

from pydantic import BaseModel

from app.models.player import Player
from app.models.user import User
from app.schemas.ws_lobby_event_schemas import ChannelEventType, EventResponseType

CHANNEL_EVENT_TYPE = 'channel_handler'


class ChannelEventMessageBase(BaseModel, ABC):
    type: str = CHANNEL_EVENT_TYPE  # noqa: A003
    channel_type_event: ChannelEventType

    class Config:
        use_enum_values = True


class ChannelTypeEventMessagePayload(BaseModel):
    event_send_type: EventResponseType

    class Config:
        use_enum_values = True


class ChannelTypeEventMessage(ChannelEventMessageBase):
    payload: ChannelTypeEventMessagePayload


class ChannelFriendshipIDMessagePayload(BaseModel):
    friendship_id: int


class ChannelFriendshipIDMessage(ChannelEventMessageBase):
    payload: ChannelFriendshipIDMessagePayload


class ChannelEventBattleRequestPayload(BaseModel):
    to_username: str


class ChannelEventBattleMessage(ChannelEventMessageBase):
    event: EventResponseType
    payload: ChannelEventBattleRequestPayload


class InfoBattleAcceptPayload(BaseModel):
    room_id: str
    ticket: str


class ChannelEventBattleAcceptMessage(ChannelEventMessageBase):
    event: EventResponseType
    payload: InfoBattleAcceptPayload


ChannelEventMessageRoot = Union[
    ChannelTypeEventMessage,
    ChannelFriendshipIDMessage,
    ChannelEventBattleMessage,
    ChannelEventBattleAcceptMessage,
]


class ChannelEventMessageProducing(BaseModel):
    receiver: Union[User, Player]
    event: ChannelEventMessageRoot

    class Config:
        arbitrary_types_allowed = True


class ChannelEventMessage(BaseModel):
    __root__: ChannelEventMessageRoot
