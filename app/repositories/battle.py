import logging
from contextlib import contextmanager
from datetime import datetime
from time import time
from typing import Optional
from uuid import uuid4

from django.conf import settings

from app.exceptions import PermissionDenied
from app.models.battle import Battle, BattlePlayer
from app.models.game_mode import GameMode
from app.models.player import Player
from app.redis_client import redis_client
from app.repositories.base import BaseRepository
from app.repositories.battle_player import BattlePlayerRepository
from app.schemas import battle as schemas

logger = logging.getLogger('django.channels.server')


class BattleRepository(BaseRepository):  # pylint: disable=too-many-public-methods

    DB_MODEL = Battle

    @classmethod
    @contextmanager
    def lock(cls, battle: Battle):
        with redis_client.lock(cls.get_key(battle)):
            yield

    @classmethod
    def create_battle(
        cls,
        game_mode: GameMode,
        player1: Player,
        player2: Player,
        battle_invite: schemas.BattleInvite,
    ) -> Battle:
        if not battle_invite:
            raise PermissionDenied()

        battle = Battle.objects.create(
            room_id=battle_invite.room_id,
            player_1_ticket=str(uuid4()),
            player_2_ticket=str(uuid4()),
            game_mode=game_mode,
        )
        start_hp = battle.game_mode.start_battle_player_hp
        BattlePlayerRepository.create(
            idx=BattlePlayer.PlayerId.TWO, battle=battle, player=player1, hp=start_hp
        )
        BattlePlayerRepository.create(
            idx=BattlePlayer.PlayerId.ONE, battle=battle, player=player2, hp=start_hp
        )
        return battle

    @staticmethod
    def battle_surrender(battle: Battle, player_id: int):
        winner_player = battle.players.all().exclude(player__id=player_id).first()
        if winner_player:
            battle.complete(winner_player.player)
        else:
            logger.error(
                'Cannot find winner player for battle %s. Discarding broken battle to '
                'avoid player being stuck',
                battle.id,
            )
            battle.state = Battle.States.DISCARDED
            battle.save()

    @staticmethod
    def get_battle_end_turn_timer_cache_name(battle_id, turn_number, turn_idx):
        return f'battle_end_turn_timer_active_{battle_id}_{turn_number}_{turn_idx}'

    @classmethod
    def remove_state_in_redis(cls, battle: Battle) -> None:
        cls._remove_state_in_redis(battle)

    @classmethod
    def _remove_state_in_redis(cls, battle: Battle) -> None:
        redis_client.delete(cls.get_key(battle))

    @classmethod
    def get_state_from_redis(cls, battle: Battle) -> schemas.Battle:
        return cls._get_state_from_redis(battle)

    @classmethod
    def _get_state_from_redis(cls, battle: Battle) -> schemas.Battle:
        return schemas.Battle.parse_raw(redis_client.get(cls.get_key(battle)))

    @classmethod
    def get_key(cls, battle: Battle) -> str:
        return f'{settings.BATTLE_STATE_REDIS_PREFIX}-{battle.room_id}'

    @classmethod
    def update_state_in_redis(cls, battle: Battle, new_state: schemas.Battle) -> None:
        if new_state is None:
            raise TypeError('Are you dyrak? Trying to save None as state')

        logger.info('Update state in redis for battle %s', battle.id)
        cls._update_state_in_redis(battle, new_state)

    @classmethod
    def _update_state_in_redis(cls, battle: Battle, new_state: schemas.Battle) -> None:
        redis_client.set(cls.get_key(battle), new_state.json(), settings.BATTLE_STATE_TTL)

    @staticmethod
    def set_battle_in_redis(
        player_id: int,
        enemy_id: int,
    ) -> schemas.Battle:
        return schemas.Battle(
            players={
                player_id: schemas.BattlePlayer(
                    id=player_id,
                    deck=schemas.Deck(),
                ),
                enemy_id: schemas.BattlePlayer(
                    id=enemy_id,
                    deck=schemas.Deck(),
                ),
            },
        )

    @staticmethod
    def filter_to_battle_states() -> list[Battle]:
        battle_state = Battle.States
        list_state = [
            battle_state.ACTIVE,
            battle_state.JOINED,
            battle_state.AWAITING_RECONNECT,
        ]
        return Battle.objects.filter(state__in=list_state)

    @staticmethod
    def update_battle_state(battles, state: str) -> int:
        return battles.update(state=state)

    @staticmethod
    def _get_reconnect_cache_name(battle_id: int, player_id: int) -> str:
        return f'{settings.BATTLE_RECONNECT_REDIS_PREFIX}_{battle_id}_{player_id}'

    @classmethod
    def delete_reconnect_cache(cls, battle_id: int, player_id: int):
        redis_client.delete(cls._get_reconnect_cache_name(battle_id, player_id))

    @classmethod
    def get_reconnect_cache(cls, battle_id: int, player_id: int):
        return redis_client.get(cls._get_reconnect_cache_name(battle_id, player_id))

    @classmethod
    def set_reconnect_cache(cls, battle_id: int, player_id: int, data: str, ttl: int):
        name_key = cls._get_reconnect_cache_name(battle_id, player_id)
        return redis_client.set(
            name_key,
            data,
            ttl,
        )

    @staticmethod
    def set_state(
        battle, state: str, winner: Optional[Player] = None, ended_at: Optional[datetime] = None
    ):
        battle.state = state
        if winner is not None:
            battle.winner = winner
        if ended_at is not None:
            battle.battle_end = ended_at

    @staticmethod
    def get_from_battle_id(battle_id: int) -> Battle:
        return Battle.objects.get(id=battle_id)

    @staticmethod
    def get_battle_channel_name(battle: Optional[Battle]) -> Optional[str]:
        return f'{settings.REDIS_GROUP_PREFIX}{battle.room_id}'

    @staticmethod
    def set_round_started_at(battle: schemas.Battle):
        battle.round_started_at = int(time())

    @classmethod
    def get_time_to_end_round(cls, battle: Battle, state_in_redis: schemas.Battle):
        time_since_started_round = cls.get_time_since_started_round(state_in_redis)
        return battle.game_mode.battlefield_timer_duration - time_since_started_round

    @classmethod
    def get_time_since_started_round(cls, state_in_redis: schemas.Battle):
        return int(time()) - state_in_redis.round_started_at
