from typing import Optional, Union

from django.conf import settings

from app.models.player import Player
from app.models.player import PlayerStatus as PlayerStatusModel
from app.redis_client import redis_client
from app.repositories.base import BaseRepository
from app.schemas.player import PlayerStatusOverWebsocket
from app.schemas.ws_schemas import PlayerStatus


class PlayerRepository(BaseRepository):

    DB_MODEL = Player

    @classmethod
    def get_player_status(cls, player: Player) -> PlayerStatus:
        status_over_websocket = cls.get_player_status_over_websocket(player)
        if status_over_websocket == PlayerStatusOverWebsocket.IN_BATTLE:
            return PlayerStatus(
                title=status_over_websocket.value,
                name=status_over_websocket.value,
            )

        if status_over_websocket == PlayerStatusOverWebsocket.ONLINE:
            if player.status:
                return PlayerStatus(title=player.status.title, name=player.status.name)
            return PlayerStatus(
                title=status_over_websocket.value,
                name=status_over_websocket.value,
            )
        return PlayerStatus(
            title=status_over_websocket.value,
            name=status_over_websocket.value,
        )

    @staticmethod
    def _has_lobby_connection(player: Player) -> bool:
        lobby_group_name = (
            f'asgi:group:{settings.LOBBY_CONSUMER_REDIS_GROUP_PREFIX}-{player.user_id}'
        )
        return bool(redis_client.zcard(lobby_group_name))

    @staticmethod
    def _has_battle_connection(player: Player) -> bool:
        battle_group_name = (
            f'asgi:group:{settings.BATTLE_CONSUMER_REDIS_GROUP_PREFIX}-{player.user_id}-events'
        )
        return bool(redis_client.zcard(battle_group_name))

    @classmethod
    def is_status_online(cls, player: Player) -> bool:
        return cls._has_lobby_connection(player) and not cls._has_battle_connection(player)

    @classmethod
    def is_status_in_battle(cls, player: Player) -> bool:
        return cls._has_battle_connection(player)

    @classmethod
    def is_status_changeable(
        cls, player: Player, new_status: Union[PlayerStatusModel, None]
    ) -> bool:
        status = cls.get_player_status_over_websocket(player)
        if status != PlayerStatusOverWebsocket.ONLINE:
            return False
        if not player.status and not new_status:
            return False
        if player.status and new_status and player.status.name == new_status.name:
            return False
        return True

    @classmethod
    def get_player_status_over_websocket(cls, player: Player) -> PlayerStatusOverWebsocket:
        if cls.is_status_in_battle(player):
            return PlayerStatusOverWebsocket.IN_BATTLE
        if cls.is_status_online(player):
            return PlayerStatusOverWebsocket.ONLINE
        return PlayerStatusOverWebsocket.OFFLINE

    @classmethod
    def get_player_channel_name(cls, player: Optional[Player]) -> Optional[str]:
        return f'{settings.BATTLE_CONSUMER_REDIS_GROUP_PREFIX}-{player.user_id}-events'

    @classmethod
    def delete_all_player_battle_connections_cache(cls, player: Player):
        cache_group_name = f'asgi:group:{cls.get_player_channel_name(player)}'
        redis_client.delete(cache_group_name)
