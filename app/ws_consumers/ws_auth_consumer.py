import asyncio
import copy
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Union

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings

from app.battle_service import get_card_behavior
from app.enums.card import CardTypesEnum
from app.models.battle import Battle, BattlePlayer, CardActiveMystery, Tile
from app.models.player import Player
from app.models.user import User
from app.redis_client import redis_client
from app.schemas import channel_schemas
from app.serializers.battle import TileSerializer
from app.tasks import save_battle_log_to_mongo
from app.utils.battle_consumer_utils import BattleServerEventsEnum, ServerEventData, get_state
from app.utils.websocket import safe

logger = logging.getLogger()


@dataclass
class EventState:
    user_id: int

    @property
    def user(self):
        return User.objects.get(id=self.user_id)

    @property
    def player(self):
        return self.user.player


def reformat_event(event: str):
    return event.replace('_', '.')


async def send_ping(connection):
    logger.info('Ping task for user %s started', connection.user_id)
    await asyncio.sleep(settings.PING_SLEEP_TIME)
    connection.ping_uuid = str(uuid.uuid4())
    content_dict = {'events': [{'event': 'ping', 'params': {'uuid': connection.ping_uuid}}]}
    await connection.send(text_data=json.dumps(content_dict))
    try:
        await asyncio.sleep(settings.PING_SLEEP_TIME)
    except asyncio.CancelledError:
        return

    logger.info('Ping failed calling disconnect for user %s', connection.user_id)
    await connection.channel_layer.group_discard(
        f'{settings.BATTLE_CONSUMER_REDIS_GROUP_PREFIX}-{connection.user_id}-events',
        connection.channel_name,
    )
    await connection.close()


class AuthConsumer(AsyncJsonWebsocketConsumer):
    """
    AuthConsumer is responsible for maintaining basic websocket events and logic: connect, disconnect, send message to
    opponent, send message to player, send message to both players.
    receive method creates an abstraction to conveniently receive messages from the websocket and call required methods
    with a predefined structure.
    """

    def __init__(self, *args, **kwargs):
        self.room_id = ''
        self.room_group_id = ''
        self.opponent_channel_id = ''
        self.opponent_disconnected = False
        self.battle = None
        self.battle_player = None
        self.user_id = 0
        self.player_id = 0
        self.events = []
        self.channel_name = ''
        self.opponent_player = None
        self.ping_task = None
        self.ping_uuid = None
        super(AuthConsumer, self).__init__(*args, **kwargs)

    def check_triggers(self, event: ServerEventData):
        if not self.get_opponent_player:
            # to avoid checking triggers on cancel battle
            return
        state = get_state(self.battle, self.player_id, self)
        # check friendly avatar damage
        if (
            event.event == 'avatar_damage'
            and event.params['target_avatar'] == 'player'
            and event.to_opponent_only
        ):
            active_mysteries = CardActiveMystery.objects.filter(player=state.enemy)
            for active_mystery in active_mysteries:
                behavior = get_card_behavior(active_mystery)
                behavior.on_player_avatar_damage(
                    state, active_mystery, state.player, damage=event.params['damage']
                )
        if (
            event.event == 'move_card_from_hand_to_tile'
            and state.player.tile.exclude_mia().filter(id=event.params['tile_id']).exists()
        ):
            active_mysteries = CardActiveMystery.objects.filter(player=state.enemy)
            tile_with_card = Tile.objects.get(id=event.params['tile_id'])
            for active_mystery in active_mysteries:

                behavior = get_card_behavior(active_mystery)
                behavior.on_opponent_creature_play(state, active_mystery, tile_with_card)
            tile_serializer_data = TileSerializer(tile_with_card).data
            description = (
                tile_serializer_data['card']['description']
                if tile_serializer_data['card'] and tile_serializer_data['card']['description']
                else ''
            )
            if (description and 'warcry</b>:' in description.lower()) or (
                tile_with_card.original_card
                and tile_with_card.original_card.description
                and 'warcry:' in tile_with_card.original_card.description.lower()
            ):
                for tile in (
                    state.player.tile.exclude_mia()
                    .exclude_censor()
                    .non_free()
                    .exclude(id=tile_with_card.id)
                ):
                    behavior = get_card_behavior(tile)
                    behavior.on_play_friendly_creature_with_warcry(state, tile)

        if event.event == 'mia_enchantment_removed':
            tile = Tile.objects.get(id=event.params['tile_id'])
            behavior = get_card_behavior(tile)
            behavior.on_awake_from_mia(state, tile)

        if event.event == BattleServerEventsEnum.tile_card_death:
            tile_battle_player = Tile.objects.get(id=event.params['tile_id']).player
            active_mysteries = CardActiveMystery.objects.filter(player=tile_battle_player)
            for active_mystery in active_mysteries:
                tile = Tile.objects.get(id=event.params['tile_id'])
                behavior = get_card_behavior(active_mystery)
                if tile.card.type == CardTypesEnum.serf:
                    behavior.on_friendly_creature_death(state, active_mystery, tile.card)
            tiles = (
                tile_battle_player.tile.exclude_mia()
                .exclude_censor()
                .non_free()
                .exclude(id=event.params['tile_id'])
            )
            for tile in tiles:
                behavior = get_card_behavior(tile)
                behavior.on_friendly_creature_death(state, tile)
        if (
            event.event == BattleServerEventsEnum.spell_card_played
            and not event.to_opponent_only
            and state.player.hand.filter(id=event.params['card_hand']['id']).exists()
        ):
            tiles = state.player.tile.exclude_mia().exclude_censor().non_free()
            for tile in tiles:
                behavior = get_card_behavior(tile)
                behavior.on_any_spell_card_played(state, event.params['card_hand']['id'], tile)

    def store_event(self, event, check_triggers=True):
        if not event:
            logger.info('store_event called with empty event!')
            return
        event.timestamp = datetime.now().timestamp()
        self.events.append(event)
        if check_triggers:
            self.check_triggers(event=event)

    def append_event_params(self, event_name: str, param_name: str, value):
        for event in self.events:
            if event.event == event_name:
                event.params[param_name].append(value)

    def remove_stored_event(self, event_to_remove: ServerEventData):
        for index, event in enumerate(self.events):
            if event_to_remove.event == event.event and event_to_remove.params == event.params:
                self.events.pop(index)

    def flush_events(self):
        self.events = []

    def fire_event_to_player(self, events: list, target: str):
        """

        :param state: State
        :param events:
        :param target: player / opponent
        :return:
        """
        event = copy.deepcopy(events[0])
        event_params = event.params
        for extra_event in events[1:]:
            try:
                event_params['extra_events'].append(extra_event.to_data())
            except KeyError:
                event_params['extra_events'] = [extra_event.to_data()]

        if target == 'player':
            self.send_message_to_client(event.event, event_params)
        elif target == 'opponent':
            self.send_message_to_opponent(event.event, event_params)

    def fire_events(self):
        pass

        events = self.events
        events = sorted(events, key=lambda e: e.timestamp)
        events_to_player = list(filter(lambda e: not e.to_opponent_only, events))
        if events_to_player:
            self.fire_event_to_player(events_to_player, 'player')
        events_to_opponent = list(filter(lambda e: not e.to_player_only, events))
        if events_to_opponent:
            self.fire_event_to_player(events_to_opponent, 'opponent')
        self.flush_events()
        if self.battle.state in (Battle.States.COMPLETED, Battle.States.DISCARDED):
            self.disconnect()

    @property
    def get_opponent_player(self) -> Union[Player, None]:
        """
        None is returned when there's only one player in the battle
        """
        if self.opponent_player:
            return self.opponent_player
        for player in self.battle.players.all():
            if player.player.id != self.player_id:
                self.opponent_player = player.player
                return (
                    player.player
                )  # this will return the player object instead of the battle player object
        return None

    def check_if_opponent_exists_and_send_error(self) -> bool:
        opponent_player = self.get_opponent_player
        if not opponent_player:
            self.store_event(
                ServerEventData(
                    BattleServerEventsEnum.server_error,
                    params={
                        'error_name': 'Invalid State',
                        'error_message': 'Cannot find opponent player',
                    },
                    to_player_only=True,
                )
            )
            self.fire_events()
            return False
        return True

    async def connect(self):
        # write room_id, room_group_id, user_id and battle for internal usage
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_id = f'{settings.REDIS_GROUP_PREFIX}{self.room_id}'
        self.user_id = self.scope['user'].id
        self.player_id = (await sync_to_async(Player.objects.get)(user__id=self.user_id)).id
        self.battle: Battle = await sync_to_async(Battle.objects.get)(room_id=self.room_id)
        self.battle_player = await sync_to_async(
            BattlePlayer.objects.filter(player_id=self.player_id, battle=self.battle).first
        )()
        if self.battle.state in (Battle.States.COMPLETED, Battle.States.DISCARDED):
            await self.accept()
            is_winner = await sync_to_async(
                lambda: self.battle.winner == self.battle_player.player
            )()
            result_type = 'victory' if is_winner else 'loss'
            content_dict = {
                'events': [
                    {
                        'event': BattleServerEventsEnum.battle_complete,
                        'params': {'result_type': result_type},
                    }
                ]
            }
            await self.send(text_data=json.dumps(content_dict))
            await self.close()  # close socket connection from the server side

        # disconnect another player battle connection if exists
        cache_group_name = f'{settings.BATTLE_CONSUMER_REDIS_GROUP_PREFIX}-{self.user_id}-events'

        await self.channel_layer.group_send(
            cache_group_name,
            {
                'type': 'disconnect',
            },
        )

        # Join room group
        await self.channel_layer.group_add(self.room_group_id, self.channel_name)
        await self.channel_layer.group_add(
            f'{settings.BATTLE_CONSUMER_REDIS_GROUP_PREFIX}-{self.user_id}-events',
            self.channel_name,
        )
        await self.accept()
        if not settings.DISABLE_PING:
            self.create_ping_task()

    def create_ping_task(self):
        logger.debug('Creating ping task for user %s', self.user_id)
        self.ping_task = asyncio.create_task(send_ping(self))

    async def disconnect(self, close_code=None, from_ping_task: bool = False):
        logger.info(f'disconnect called on user {self.user_id} for battle {self.battle.id}')
        await self.channel_layer.group_discard(self.room_group_id, self.channel_name)
        await self.channel_layer.group_discard(
            f'{settings.BATTLE_CONSUMER_REDIS_GROUP_PREFIX}-{self.user_id}-events',
            self.channel_name,
        )
        if not from_ping_task and not settings.DISABLE_PING:
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass

    @property
    def get_opponent_channel_name(self):
        if self.opponent_channel_id and not self.opponent_disconnected:
            return self.opponent_channel_id
        for channel in self.get_room_connected_channels:
            if channel != self.channel_name:
                return channel

    @property
    def get_room_connected_channels(self):
        cache_group_name = f'asgi:group:{self.room_group_id}'
        scan_result = redis_client.zscan(cache_group_name)
        return [item[0] for item in scan_result[1]]

    @property
    def my_player_idx(self):
        for battle_player in self.battle.players.all():
            if battle_player.player.id == self.player_id:
                return battle_player.idx

    @property
    def is_my_turn(self):
        self.battle.refresh_from_db()
        return self.battle.turn == self.my_player_idx

    @sync_to_async
    def set_last_player_activity(self):
        player = self.battle_player.player
        if player:
            player.update_last_activity()

    @safe
    async def receive(self, *arg, **kwargs):
        await self.set_last_player_activity()
        await super().receive(*arg, **kwargs)

    @safe
    async def send(self, *arg, **kwargs):
        await self.set_last_player_activity()
        await super().send(*arg, **kwargs)

    async def send_json(self, content, close=False):
        # save server event
        save_battle_log_to_mongo.apply_async(
            args=(
                str(self.battle.id),
                str(self.battle_player.id),
                'server_event',
                content,
            ),
        )
        await super().send_json(content, close)

    async def receive_json(self, content, **kwargs):
        if 'event' not in content:
            raise ValueError("Incoming client event has no 'event' attribute")

        if (
            not settings.DISABLE_PING
            and content['event'] == 'pong'
            and content['params']['uuid'] == self.ping_uuid
            and self.ping_task
        ):
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass
            self.create_ping_task()
            return

        save_battle_log_to_mongo.apply_async(
            args=(
                str(self.battle.id),
                str(self.battle_player.id),
                'client_event',
                content,
            ),
        )
        event = content['event']
        params = content['params'] if 'params' in content.keys() else {}
        # use slightly modified dispatch method from SyncConsumer class for correct event processing logic
        handler = getattr(self, event, None)
        if handler:
            if asyncio.iscoroutinefunction(handler):
                await handler(**params)
            else:
                await sync_to_async(handler)(**params)
        else:
            raise ValueError('No handler for event %s' % event)

    def send_message_to_lobby_consumer(
        self, player: Player, event: channel_schemas.ChannelTypeEventMessage
    ):
        async_to_sync(self.channel_layer.group_send)(f'lobby-{player.user_id}', event.dict())

    def send_message(self, message_type, message_body=None, target='group'):
        if target == 'group':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_id, {'type': message_type, 'message': message_body}
            )
        else:
            target_channel_name = (
                self.channel_name if target == 'client' else self.get_opponent_channel_name
            )
            if not target_channel_name:
                logger.info('Error sending message %s target channel name is empty', message_type)
                return
            async_to_sync(self.channel_layer.send)(
                target_channel_name, {'type': message_type, 'message': message_body}
            )

    def send_message_to_group(self, message_type, message_body=None):
        self.send_message(message_type, message_body=message_body, target='group')

    def send_message_to_client(self, message_type, message_body=None):
        self.send_message(message_type, message_body=message_body, target='client')

    def send_message_to_opponent(self, message_type, message_body=None):
        self.send_message(message_type, message_body=message_body, target='opponent')
