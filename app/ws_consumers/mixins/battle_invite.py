from app.exceptions import (
    NotInWhitelist,
    OpponentSelectedDeckIsNotPlayable,
    SelectedDeckIsNotPlayable,
    WSHandlerRecipientNotFoundException,
)
from app.models.battle import Battle
from app.models.player import Player
from app.repositories.battle_invite import BattleInviteRepository
from app.repositories.deck import DeckRepository
from app.repositories.game_mode import GameModeRepository
from app.schemas import channel_schemas, ws_schemas
from app.schemas.ws_lobby_event_schemas import (
    ChannelEventType,
    EventRequestBattleInviteType,
    EventResponseType,
)
from app.ws_consumers.lobby_consumer_base import LobbyConsumerBase


class BattleInviteMixin(LobbyConsumerBase):
    @classmethod
    def _map_ws_handlers(cls):
        return {
            EventRequestBattleInviteType.BATTLE_INVITE_CREATE: cls.handle_ws_battle_invite_create,
            EventRequestBattleInviteType.BATTLE_INVITE_CANCEL: cls.handle_ws_battle_invite_cancel,
            EventRequestBattleInviteType.BATTLE_INVITE_DECLINE: cls.handle_ws_battle_invite_decline,
            EventRequestBattleInviteType.BATTLE_INVITE_ACCEPT: cls.handle_ws_battle_invite_accept,
        }

    @classmethod
    def _map_channel_handlers(cls):
        return {
            ChannelEventType.HANDLE_BATTLE_INVITE_SHOW: cls.handle_channel_battle_invite_show,
            ChannelEventType.HANDLE_BATTLE_INVITE_ACCEPT: cls.handle_channel_battle_invite_accept,
        }

    def handle_ws_battle_invite_create(self, event: ws_schemas.EventRequestBattleInviteMessage):
        """
        Create a battle invite

        Other Parameters
        -------------------
        Request Attributes:
             :event:`ws_schemas.EventRequestBattleInviteMessage`
        Response:
            :func:`BattleInviteRepository.create`
        """
        invited_player = self.find_player(event.params.to_username)
        if not invited_player:
            raise WSHandlerRecipientNotFoundException()

        player = self.player
        player_custom_deck = DeckRepository.get_player_selected_deck(player)
        invited_player_custom_deck = DeckRepository.get_player_selected_deck(invited_player)
        if not (player.is_whitelist_user or player.num_avatars_owned) or not (
            invited_player.is_whitelist_user or invited_player.num_avatars_owned
        ):
            raise NotInWhitelist()

        game_mode = GameModeRepository.get_game_mode(event.params.game_mode_id)
        if not game_mode.is_random_generated_deck:
            if not player_custom_deck or not DeckRepository.is_playable(
                game_mode.max_cards_in_deck, player_custom_deck
            ):
                raise SelectedDeckIsNotPlayable()
            if not invited_player_custom_deck or not DeckRepository.is_playable(
                game_mode.max_cards_in_deck, invited_player_custom_deck
            ):
                raise OpponentSelectedDeckIsNotPlayable()

        invite_or_battle = BattleInviteRepository.create(
            sender_player=player, invited_player=invited_player, game_mode=game_mode
        )
        if isinstance(invite_or_battle, Battle):
            return self._battle_invite_accept(sender_player=invited_player, invited_player=player)

        event = self._create_channel_event_battle_invite_show(
            receiver=invited_player,
            to_username=player.username,
            event_send_type=EventResponseType.BATTLE_INVITE_RECEIVE,
        )
        self._produce_event(event)
        return None

    def handle_ws_battle_invite_decline(self, event: ws_schemas.EventRequestBattleInviteMessage):
        """
        Decline a battle invite

        Other Parameters
        -------------------
        Request Attributes:
             :event:`ws_schemas.EventRequestBattleInviteMessage`
        Response:
            :func:`BattleInviteRepository.decline`
        """
        sender_player = self.find_player(event.params.to_username)
        if not sender_player:
            raise WSHandlerRecipientNotFoundException()

        player = self.player
        BattleInviteRepository.decline(sender_player=sender_player, invited_player=player)
        event = self._create_channel_event_battle_invite_show(
            receiver=sender_player,
            to_username=player.username,
            event_send_type=EventResponseType.BATTLE_INVITE_DECLINE,
        )
        self._produce_event(event)

    def handle_ws_battle_invite_cancel(
        self,
        event: ws_schemas.EventRequestBattleInviteMessage,
    ):
        """
        Cancel a battle invite

        Other Parameters
        -------------------
        Request Attributes:
             :event:`ws_schemas.EventRequestBattleInviteMessage`
        Response:
            :func:`BattleInviteRepository.decline`
        """
        invited_player = self.find_player(event.params.to_username)
        if not invited_player:
            raise WSHandlerRecipientNotFoundException()

        player = self.player
        BattleInviteRepository.cancel(sender_player=player, invited_player=invited_player)
        event = self._create_channel_event_battle_invite_show(
            receiver=invited_player,
            to_username=player.username,
            event_send_type=EventResponseType.BATTLE_INVITE_CANCEL,
        )
        self._produce_event(event)

    def handle_ws_battle_invite_accept(
        self,
        event: ws_schemas.EventRequestBattleInviteMessage,
    ):
        """
        Accept a battle invite

        Other Parameters
        -------------------
        Request Attributes:
             :event:`ws_schemas.EventRequestBattleInviteMessage`
        Response:
            :func:`BattleInviteRepository.accept`
        """
        sender_player = self.find_player(event.params.to_username)
        if not sender_player:
            raise WSHandlerRecipientNotFoundException()

        player = self.player
        self._battle_invite_accept(sender_player=sender_player, invited_player=player)

    def _battle_invite_accept(self, sender_player: Player, invited_player: Player):
        battle = BattleInviteRepository.accept(
            sender_player=sender_player, invited_player=invited_player
        )

        events_to_produce = [
            self._create_channel_event_battle_invite_accept(
                self.player, battle.room_id, battle.player_2_ticket
            ),
            self._create_channel_event_battle_invite_accept(
                sender_player, battle.room_id, battle.player_1_ticket
            ),
        ]
        self._produce_events(events_to_produce)

    def handle_channel_battle_invite_show(self, event: channel_schemas.ChannelEventBattleMessage):
        ws_event = ws_schemas.EventResponseBattleInviteMessage(
            event=event.event,
            params=ws_schemas.EventBattleInviteMessagePayload(
                to_username=event.payload.to_username
            ),
        )
        self.send_json(ws_event)

    def handle_channel_battle_invite_accept(
        self, event: channel_schemas.ChannelEventBattleAcceptMessage
    ):
        ws_event = ws_schemas.EventResponseBattleInviteAcceptMessage(
            event=event.event,
            params=ws_schemas.EventResponseBattleInviteAcceptMessagePayload(
                room_id=event.payload.room_id, ticket=event.payload.ticket
            ),
        )
        self.send_json(ws_event)

    @staticmethod
    def _create_channel_event_battle_invite_show(
        receiver: Player, to_username: str, event_send_type: EventResponseType
    ) -> channel_schemas.ChannelEventMessageProducing:
        return channel_schemas.ChannelEventMessageProducing(
            receiver=receiver,
            event=channel_schemas.ChannelEventBattleMessage(
                channel_type_event=ChannelEventType.HANDLE_BATTLE_INVITE_SHOW,
                event=event_send_type,
                payload=channel_schemas.ChannelEventBattleRequestPayload(
                    to_username=to_username,
                ),
            ),
        )

    @staticmethod
    def _create_channel_event_battle_invite_accept(
        player: Player, room_id: str, ticket: str
    ) -> channel_schemas.ChannelEventMessageProducing:
        return channel_schemas.ChannelEventMessageProducing(
            receiver=player,
            event=channel_schemas.ChannelEventBattleAcceptMessage(
                channel_type_event=ChannelEventType.HANDLE_BATTLE_INVITE_ACCEPT,
                event=EventResponseType.BATTLE_INVITE_ACCEPT,
                payload=channel_schemas.InfoBattleAcceptPayload(room_id=room_id, ticket=ticket),
            ),
        )
