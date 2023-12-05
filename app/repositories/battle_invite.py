from contextlib import contextmanager
from typing import Optional, Union

from django.core.cache import cache

from app.exceptions import PermissionDenied
from app.models.battle import Battle
from app.models.game_mode import GameMode
from app.models.player import Player
from app.redis_client import redis_client
from app.repositories.battle import BattleRepository
from app.repositories.game_mode import GameModeRepository
from app.schemas.battle import BattleInvite


class BattleInviteRepository:
    @classmethod
    @contextmanager
    def lock(cls, sender_player: Player, invited_player: Player):
        with redis_client.lock(cls._get_key(sender_player, invited_player)):
            yield

    @staticmethod
    def _get_key(sender_player: Player, invited_player: Player) -> str:
        return f'battle_invite_{sender_player.user_id}_x_{invited_player.user_id}'

    @classmethod
    def get(cls, sender_player: Player, invited_player: Player) -> Optional[BattleInvite]:
        battle_invite_data = cache.get(cls._get_key(sender_player, invited_player))
        return BattleInvite.parse_obj(battle_invite_data) if battle_invite_data else None

    @classmethod
    def _delete_battle_invite(cls, sender_player: Player, invited_player: Player):
        cache.delete(cls._get_key(sender_player=sender_player, invited_player=invited_player))

    @classmethod
    def accept(
        cls,
        *,
        sender_player: Player,
        invited_player: Player,
    ) -> Battle:
        with cls.lock(sender_player=sender_player, invited_player=invited_player):
            return cls._accept(sender_player=sender_player, invited_player=invited_player)

    @classmethod
    def _accept(
        cls,
        *,
        sender_player: Player,
        invited_player: Player,
    ) -> Battle:
        battle_invite = cls.get(sender_player=sender_player, invited_player=invited_player)
        if not battle_invite:
            raise PermissionDenied()
        game_mode = GameModeRepository.get_game_mode(battle_invite.game_mode_id)
        cls._delete_battle_invite(sender_player=sender_player, invited_player=invited_player)
        return BattleRepository.create_battle(
            player1=invited_player,
            player2=sender_player,
            battle_invite=battle_invite,
            game_mode=game_mode,
        )

    @classmethod
    def decline(
        cls,
        *,
        sender_player: Player,
        invited_player: Player,
    ):
        with cls.lock(sender_player=sender_player, invited_player=invited_player):
            battle_invite = cls.get(sender_player=sender_player, invited_player=invited_player)
            if battle_invite is None:
                raise PermissionDenied()
            cls._delete_battle_invite(sender_player=sender_player, invited_player=invited_player)

    @classmethod
    def cancel(
        cls,
        *,
        sender_player: Player,
        invited_player: Player,
    ):
        with cls.lock(sender_player=sender_player, invited_player=invited_player):
            battle_invite = cls.get(sender_player=sender_player, invited_player=invited_player)
            if battle_invite is None:
                raise PermissionDenied()
            cls._delete_battle_invite(sender_player=sender_player, invited_player=invited_player)

    @classmethod
    def create(
        cls,
        *,
        sender_player: Player,
        invited_player: Player,
        game_mode: GameMode,
    ) -> Union[BattleInvite, Battle]:
        if invited_player == sender_player:
            raise PermissionDenied()

        with cls.lock(sender_player=invited_player, invited_player=sender_player):
            existing_battle_invite = cls.get(
                sender_player=invited_player, invited_player=sender_player
            )
            if existing_battle_invite:
                return cls.accept(sender_player=invited_player, invited_player=sender_player)

            return cls._create(
                sender_player=sender_player, invited_player=invited_player, game_mode=game_mode
            )

    @classmethod
    def _create(
        cls,
        *,
        sender_player: Player,
        invited_player: Player,
        game_mode: GameMode,
    ):
        battle_invite = BattleInvite(
            sender_username=sender_player.user.username,
            invited_username=invited_player.user.username,
            game_mode_id=game_mode.id,
        )
        cache.set(
            cls._get_key(sender_player=sender_player, invited_player=invited_player),
            battle_invite.dict(),
        )
        return battle_invite
