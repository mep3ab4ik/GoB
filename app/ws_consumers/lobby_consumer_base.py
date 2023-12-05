# pylint: disable=broad-except, too-many-public-methods
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings
from pydantic import ValidationError

from app.exceptions import (
    WSHandlerDataNotValidException,
    WSHandlerException,
    WSHandlerInvalidStatusException,
    WSHandlerUnknownEventException,
)
from app.models.player import Player
from app.models.user import User
from app.schemas import channel_schemas, ws_schemas
from app.schemas.ws_lobby_event_schemas import ChannelEventType, EventRequestType, EventResponseType

logger = logging.getLogger('django.channels.server')
logger.setLevel(logging.DEBUG)


class LobbyConsumerBase(JsonWebsocketConsumer, ABC):
    WS_HANDLERS_MAPPING = {}
    CHANNEL_HANDLERS_MAPPING = {}

    @classmethod
    def update_handlers_mapping(cls, ws_handlers_mapping: dict, channel_handlers_mapping: dict):
        ws_handlers_mapping.update(cls._map_ws_handlers())
        channel_handlers_mapping.update(cls._map_channel_handlers())

    @classmethod
    @abstractmethod
    def _map_ws_handlers(cls):
        pass

    @classmethod
    @abstractmethod
    def _map_channel_handlers(cls):
        pass

    @property
    def user(self) -> Optional[User]:
        try:
            user = self.scope.get('user')
        except KeyError:
            return None
        if isinstance(user, User):
            return user
        return None

    @property
    def player(self) -> Player:
        return Player.objects.get(user=self.scope.get('user'))

    def connect(self):
        if self.user is None:
            return self.close()
        self.accept()
        self.on_user_connect()
        return None

    def on_user_connect(self):
        async_to_sync(self.channel_layer.group_add)(
            f'{settings.LOBBY_CONSUMER_REDIS_GROUP_PREFIX}-{self.player.user_id}', self.channel_name
        )

    def disconnect(self, code):
        if self.user:
            self.on_user_disconnect()

    def on_user_disconnect(self):
        async_to_sync(self.channel_layer.group_discard)(
            f'{settings.LOBBY_CONSUMER_REDIS_GROUP_PREFIX}-{self.player.user_id}', self.channel_name
        )

    def _produce_events(
        self,
        events_to_produce: List[channel_schemas.ChannelEventMessageProducing],
    ):
        for event in events_to_produce:
            self._produce_event(event)

    def _produce_event(
        self,
        event: channel_schemas.ChannelEventMessageProducing,
    ):
        """Send the payload data to the type function which is in the channel lobby."""
        user_id = event.receiver.id if isinstance(event.receiver, User) else event.receiver.user_id
        async_to_sync(self.channel_layer.group_send)(
            f'{settings.LOBBY_CONSUMER_REDIS_GROUP_PREFIX}-{user_id}',
            event.event.dict(),
        )

    @classmethod
    def encode_json(cls, content: ws_schemas.EventResponseMessageBase):
        return content.json()

    @staticmethod
    def find_player(
        username: str,
    ) -> Optional[Player]:
        return Player.objects.filter(user__username=username).first()

    def receive(self, *args, **kwargs):  # pylint: disable=unused-argument, too-many-statements
        """Accepts all events."""
        logger.info('WS received data: %s', kwargs['text_data'])
        try:
            ws_event = ws_schemas.EventResponseMessage.parse_raw(kwargs['text_data']).__root__
        except ValidationError as e:
            prepared_errors = []
            for error in e.errors():
                prepared_errors.append(
                    {
                        'loc': list(error['loc']),
                        'message': error['msg'],
                        'type': error['type'],
                    }
                )

            self.send_json(
                ws_schemas.EventResponseErrorMessage(
                    event=EventResponseType.ERROR,
                    params={
                        'message': WSHandlerDataNotValidException.message,
                        'validation_errors': prepared_errors,
                    },
                )
            )
            return None

        try:
            handler = self._get_ws_handler(ws_event.event)
        except WSHandlerUnknownEventException as e:
            self.send_json(
                ws_schemas.EventResponseErrorMessage(
                    event=EventResponseType.ERROR,
                    params={
                        'message': str(e),
                        'type': type(e).__name__,
                    },
                )
            )
            return None

        try:
            return handler(self, ws_event)
        except WSHandlerInvalidStatusException as e:
            error_message = str(e.message)
            error_data = e.data
        except WSHandlerException as e:
            error_message = str(e.message)
            error_data = e.data
        except Exception as e:
            logger.exception('Got exception in WS handler')
            error_message = f'{type(e).__name__}: {str(e)}'
            error_data = {}

        self.send_json(
            ws_schemas.EventResponseErrorMessage(
                event=EventResponseType.ERROR,
                params={
                    'message': error_message,
                    'data': error_data,
                },
            ),
        )
        return None

    def channel_handler(self, data: dict):
        """Accepts all events."""
        logger.info('Channel received data: %s', data)
        channel_event = channel_schemas.ChannelEventMessage.parse_obj(data).__root__
        channel_event.channel_type_event = ChannelEventType(channel_event.channel_type_event)
        handler = self._get_channel_handler(channel_event.channel_type_event)
        handler(self, channel_event)

    def _get_ws_handler(self, type_event: EventRequestType) -> Callable[[Any], Any]:
        handler = self.WS_HANDLERS_MAPPING.get(type_event)
        if not handler:
            raise WSHandlerUnknownEventException(event=type_event.value)
        return handler

    def _get_channel_handler(self, type_event: ChannelEventType) -> Callable[[Any], Any]:
        handler = self.CHANNEL_HANDLERS_MAPPING.get(type_event)
        if not handler:
            raise ValueError(f'No channel handler for {type_event}')
        return handler
