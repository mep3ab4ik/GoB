# pylint: disable=line-too-long,too-many-public-methods,too-many-lines,broad-except
from app.exceptions import WSHandlerInvalidStatusException, WSHandlerRecipientNotFoundException
from app.models.player import Friendship, Player, PlayerStatus
from app.repositories.friendship import FriendshipRepository
from app.repositories.player import PlayerRepository
from app.schemas import channel_schemas, ws_schemas
from app.schemas.ws_lobby_event_schemas import (
    ChannelEventType,
    EventRequestFriendshipType,
    EventRequestPlayerStatusType,
    EventResponseType,
)
from app.ws_consumers.lobby_consumer_base import LobbyConsumerBase


class FriendshipMixin(LobbyConsumerBase):
    @classmethod
    def _map_ws_handlers(cls):
        return {
            EventRequestFriendshipType.FRIENDSHIP_REQUEST_CREATE: cls.handle_ws_friendship_request_create,
            EventRequestFriendshipType.FRIENDSHIP_REQUEST_DECLINE: cls.handle_ws_friendship_request_decline,
            EventRequestFriendshipType.FRIENDSHIP_REQUEST_CANCEL: cls.handle_ws_friendship_request_cancel,
            EventRequestFriendshipType.FRIENDSHIP_REMOVE: cls.handle_ws_friendship_remove,
            EventRequestFriendshipType.FRIENDSHIP_REQUEST_ACCEPT: cls.handle_ws_friendship_request_accept,
            EventRequestPlayerStatusType.CHANGE_PLAYER_STATUS: cls.handle_ws_change_player_status,
        }

    @classmethod
    def _map_channel_handlers(cls):
        return {
            ChannelEventType.HANDLE_UPDATE_FRIENDSHIP_LIST: cls.handle_channel_update_friendship_list,
            ChannelEventType.HANDLE_CHANNEL_USER_STATUS: cls.handle_channel_user_status,
            ChannelEventType.HANDLE_FRIENDSHIP_REQUEST_RECEIVE: cls.handle_channel_friendship_request_receive,
        }

    def on_user_connect(self):
        super().on_user_connect()
        self._send_friend_list()
        player = self.player
        player.status = None
        player.save()
        events_to_produce = []
        self._update_friends_friendship_list(
            EventResponseType.FRIEND_CONNECTED, self.player, events_to_produce
        )
        self._produce_events(events_to_produce)

    def on_user_disconnect(self):
        super().on_user_disconnect()
        events_to_produce = []
        self._update_friends_friendship_list(
            EventResponseType.FRIEND_DISCONNECTED, self.player, events_to_produce
        )
        self._produce_events(events_to_produce)

    def _send_friend_list(self, type_event: EventResponseType = EventResponseType.FRIEND_LIST):
        player = self.player
        friendships = FriendshipRepository.get_friendship_list(player=player)
        friend_list = []
        for friendship in friendships:
            friendship_player = self._get_other_player(friendship, player)
            friendship_status = FriendshipRepository.get_status_relative_player(friendship, player)
            friendship_model = ws_schemas.EventResponseFriendshipParams(
                status=friendship_status,
                friend=ws_schemas.EventResponseFriendshipParamsPlayer(
                    player_id=friendship_player.player_id,
                    status=PlayerRepository.get_player_status(friendship_player),
                    username=friendship_player.username,
                ),
            )
            friend_list.append(friendship_model)
        event = ws_schemas.EventResponseFriendshipListMessage(
            event=type_event,
            params=friend_list,
        )
        self.send_json(event)

    @staticmethod
    def _get_other_player(friendship: Friendship, player: Player) -> Player:
        return friendship.player if friendship.friend_id == player.id else friendship.friend

    def handle_ws_friendship_request_create(self, event: ws_schemas.EventRequestFriendshipMessage):
        """
        Create a friendship request

        Other Parameters
        -------------------
        Request Attributes:
             :event:`ws_schemas.EventRequestFriendshipMessage`
        Response:
            :func:`FriendshipRepository.create`
        """
        invited_player = self.find_player(event.params.to_username)
        if not invited_player:
            raise WSHandlerRecipientNotFoundException()

        friendship = FriendshipRepository.create(
            sender_player=self.player, invited_player=invited_player
        )
        events_to_produce = [
            self._create_channel_event_update_friendship_list(
                self.player, EventResponseType.FRIEND_LIST
            ),
            self._create_channel_event_friendship_request_receive(invited_player, friendship.pk),
        ]
        self._produce_events(events_to_produce)

    def handle_ws_friendship_request_accept(self, event: ws_schemas.EventRequestFriendshipMessage):
        """
        Accept a friendship request

        Other Parameters
        -------------------
        Request Attributes:
             :event:`ws_schemas.EventRequestFriendshipMessage`
        Response:
            :func:`FriendshipRepository.accept`
        """
        sender_player = self.find_player(event.params.to_username)
        if not sender_player:
            raise WSHandlerRecipientNotFoundException()

        FriendshipRepository.accept(invited_player=self.player, sender_player=sender_player)
        events_to_produce = [
            self._create_channel_event_update_friendship_list(
                self.player, EventResponseType.FRIEND_LIST
            ),
            self._create_channel_event_update_friendship_list(
                sender_player, EventResponseType.FRIENDS_REQUEST_ACCEPT
            ),
        ]
        self._produce_events(events_to_produce)

    def handle_ws_friendship_remove(self, event: ws_schemas.EventRequestFriendshipMessage):
        """Remove a friendship request.

        Other Parameters
        -------------------
        Request Attributes:
             :event:`ws_schemas.EventRequestFriendshipMessage`
        Response:
            :func:`FriendshipRepository.decline`
        """
        other_player = self.find_player(event.params.to_username)
        if not other_player:
            raise WSHandlerRecipientNotFoundException()

        FriendshipRepository.remove(
            self.player,
            other_player,
        )

        events_to_produce = [
            self._create_channel_event_update_friendship_list(
                self.player, EventResponseType.FRIEND_LIST
            ),
            self._create_channel_event_update_friendship_list(
                other_player, EventResponseType.FRIENDS_REQUEST_REMOVE
            ),
        ]
        self._produce_events(events_to_produce)

    def handle_ws_friendship_request_cancel(self, event: ws_schemas.EventRequestFriendshipMessage):
        """
        Cancel a friendship request

        Other Parameters
        -------------------
        Request Attributes:
             :event:`ws_schemas.EventRequestFriendshipMessage`
        Response:
            :func:`FriendshipRepository.decline`
        """
        invited_player = self.find_player(event.params.to_username)
        if not invited_player:
            raise WSHandlerRecipientNotFoundException()

        FriendshipRepository.cancel(
            sender_player=self.player,
            invited_player=invited_player,
        )
        events_to_produce = [
            self._create_channel_event_update_friendship_list(
                self.player, EventResponseType.FRIEND_LIST
            ),
            self._create_channel_event_update_friendship_list(
                invited_player, EventResponseType.FRIEND_LIST
            ),
        ]
        self._produce_events(events_to_produce)

    def handle_ws_friendship_request_decline(
        self,
        event: ws_schemas.EventRequestFriendshipMessage,
    ):
        """
        Decline a friendship request

        Other Parameters
        -------------------
        Request Attributes:
             :event:`ws_schemas.EventRequestFriendshipMessage`
        Response:
            :func:`FriendshipRepository.decline`
        """
        invited_player = self.find_player(event.params.to_username)
        if not invited_player:
            raise WSHandlerRecipientNotFoundException()

        FriendshipRepository.decline(
            sender_player=self.player,
            invited_player=invited_player,
        )

        events_to_produce = [
            self._create_channel_event_update_friendship_list(
                self.player, EventResponseType.FRIEND_LIST
            ),
            self._create_channel_event_update_friendship_list(
                invited_player, EventResponseType.FRIENDS_REQUEST_DECLINE
            ),
        ]

        self._produce_events(events_to_produce)

    def handle_ws_change_player_status(self, event: ws_schemas.EventRequestPlayerStatusMessage):
        player = self.player
        status = None
        if event.params.status_name:
            status = PlayerStatus.objects.filter(name=event.params.status_name).first()
            if not status:
                raise WSHandlerInvalidStatusException(status=event.params.status_name)

        if not PlayerRepository.is_status_changeable(player, status):
            return

        player.status = status
        player.save()

        events_to_produce = []
        self._update_friends_friendship_list(
            EventResponseType.FRIEND_UPDATED, player, events_to_produce
        )
        self._produce_events(events_to_produce)

    def handle_channel_update_friendship_list(self, event: channel_schemas.ChannelTypeEventMessage):
        self._send_friend_list(event.payload.event_send_type)

    def handle_channel_user_status(self, event: channel_schemas.ChannelTypeEventMessage):
        events_to_produce = []
        self._update_friends_friendship_list(
            event.payload.event_send_type, self.player, events_to_produce
        )
        self._produce_events(events_to_produce)

    def handle_channel_friendship_request_receive(
        self, event: channel_schemas.ChannelFriendshipIDMessage
    ):
        friendship = Friendship.objects.get(pk=event.payload.friendship_id)
        requested_player = self._get_other_player(friendship, self.player)
        ws_message = self._create_ws_message_friendship_request_receive(
            friendship, self.player, requested_player
        )
        self.send_json(ws_message)

    @staticmethod
    def _create_channel_event_update_friendship_list(
        player: Player, event_send_type: EventResponseType
    ) -> channel_schemas.ChannelEventMessageProducing:
        return channel_schemas.ChannelEventMessageProducing(
            receiver=player,
            event=channel_schemas.ChannelTypeEventMessage(
                channel_type_event=ChannelEventType.HANDLE_UPDATE_FRIENDSHIP_LIST,
                payload=channel_schemas.ChannelTypeEventMessagePayload(
                    event_send_type=event_send_type
                ),
            ),
        )

    @staticmethod
    def _create_channel_event_friendship_request_receive(
        player: Player, friendship_id: int
    ) -> channel_schemas.ChannelEventMessageProducing:
        return channel_schemas.ChannelEventMessageProducing(
            receiver=player,
            event=channel_schemas.ChannelFriendshipIDMessage(
                channel_type_event=ChannelEventType.HANDLE_FRIENDSHIP_REQUEST_RECEIVE,
                payload=channel_schemas.ChannelFriendshipIDMessagePayload(
                    friendship_id=friendship_id
                ),
            ),
        )

    @staticmethod
    def _create_ws_message_friendship_request_receive(
        friendship: Friendship, player: Player, requested_player: Player
    ) -> ws_schemas.EventResponseFriendshipReceiveMessage:
        return ws_schemas.EventResponseFriendshipReceiveMessage(
            event=EventResponseType.FRIENDSHIP_REQUEST_RECEIVE,
            params=[
                ws_schemas.EventResponseFriendshipParams(
                    id=friendship.id,
                    status=FriendshipRepository.get_status_relative_player(friendship, player),
                    friend=ws_schemas.EventResponseFriendshipParamsPlayer(
                        player_id=requested_player.player_id,
                        status=PlayerRepository.get_player_status(requested_player),
                        username=requested_player.username,
                    ),
                )
            ],
        )

    def _update_friends_friendship_list(
        self,
        type_event: EventResponseType,
        player: Player,
        events_to_produce: list,
    ):
        friendships = FriendshipRepository.get_friendship_list(player=player, is_accepted=True)
        event = channel_schemas.ChannelTypeEventMessage(
            channel_type_event=ChannelEventType.HANDLE_UPDATE_FRIENDSHIP_LIST,
            payload=channel_schemas.ChannelTypeEventMessagePayload(event_send_type=type_event),
        )
        for friendship in friendships:
            friendship_player = self._get_other_player(friendship, player)
            events_to_produce.append(
                channel_schemas.ChannelEventMessageProducing(
                    receiver=friendship_player,
                    event=event,
                )
            )
