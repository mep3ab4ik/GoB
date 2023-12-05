# pylint: disable=raise-missing-from
from typing import Iterable, Optional

from django.db import IntegrityError
from django.db.models import Q

from app.exceptions import PermissionDenied
from app.models.player import Friendship, Player
from app.schemas.friendship import FriendshipStatus


class FriendshipRepository:
    @staticmethod
    def get_status_relative_player(friendship: Friendship, player: Player) -> FriendshipStatus:
        if friendship.is_accepted:
            return FriendshipStatus.ACCEPTED
        if friendship.sender_id == player.id:
            return FriendshipStatus.REQUESTED
        return FriendshipStatus.RECEIVED

    @staticmethod
    def _get_friendship(player1: Player, player2: Player) -> Optional[Friendship]:
        return Friendship.objects.filter(
            Q(friend=player1, player=player2) | Q(friend=player2, player=player1)
        ).first()

    @staticmethod
    def get_friendship_list(
        player: Player, is_accepted: Optional[bool] = None
    ) -> Iterable[Friendship]:
        queryset = Friendship.objects.filter(Q(friend=player) | Q(player=player))
        if is_accepted is not None:
            return queryset.filter(is_accepted=is_accepted)
        return queryset

    @classmethod
    def remove(
        cls,
        player1: Player,
        player2: Player,
    ):
        friendship = cls._get_friendship(player1, player2)
        if not friendship or not friendship.is_accepted:
            raise PermissionDenied()
        friendship.delete()

    @classmethod
    def decline(
        cls,
        *,
        sender_player: Player,
        invited_player: Player,
    ):
        friendship = cls._get_friendship(sender_player, invited_player)
        if not friendship or friendship.sender == sender_player or friendship.is_accepted:
            raise PermissionDenied()
        friendship.delete()

    @classmethod
    def cancel(
        cls,
        *,
        sender_player: Player,
        invited_player: Player,
    ):
        friendship = cls._get_friendship(sender_player, invited_player)
        if not friendship or friendship.sender == invited_player or friendship.is_accepted:
            raise PermissionDenied()
        friendship.delete()

    @classmethod
    def accept(
        cls,
        *,
        sender_player: Player,
        invited_player: Player,
    ):
        if sender_player == invited_player:
            raise PermissionDenied()

        friendship = cls._get_friendship(invited_player, sender_player)
        if not friendship or friendship.sender == invited_player or friendship.is_accepted:
            raise PermissionDenied()

        friendship.is_accepted = True
        friendship.save()
        return friendship

    @classmethod
    def create(
        cls,
        *,
        sender_player: Player,
        invited_player: Player,
    ) -> Friendship:
        """Create friendship between two players"""
        if sender_player == invited_player:
            raise PermissionDenied()

        player1, player2 = sorted([sender_player, invited_player], key=lambda x: x.id)
        friendship = Friendship(friend=player1, player=player2, sender=sender_player)

        try:
            friendship.save()
        except IntegrityError:
            raise PermissionDenied()
        return friendship
