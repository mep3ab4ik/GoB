# pylint: disable=protected-access,redefined-outer-name
import pytest
from django.core.cache import cache
from faker import Faker
from mock.mock import call

from app.exceptions import PermissionDenied
from app.models.battle import Battle
from app.models.game_mode import GameMode
from app.models.player import Player
from app.models.user import User
from app.redis_client import redis_client
from app.repositories.battle_invite import BattleInviteRepository
from app.schemas.battle import BattleInvite


@pytest.fixture()
def battle_invite_repository_lock(mocker):
    return mocker.patch.object(BattleInviteRepository, 'lock')


@pytest.fixture()
def sender_player(db) -> Player:  # pylint: disable=unused-argument, invalid-name
    return Player.objects.create(user=User.objects.create(username=Faker().user_name()))


@pytest.fixture()
def invited_player(db) -> Player:  # pylint: disable=unused-argument, invalid-name
    return Player.objects.create(user=User.objects.create(username=Faker().user_name()))


@pytest.fixture()
def battle_invite_key(sender_player, invited_player) -> str:
    return BattleInviteRepository._get_key(sender_player, invited_player)


@pytest.fixture()
def game_mode(db) -> GameMode:  # pylint: disable=unused-argument, invalid-name
    return GameMode.objects.create(
        title='test',
        description='test',
        battlefield_timer_duration=60,
        default_game_mode=True,
        earn_skill_points_in_this_mode=False,
    )


@pytest.fixture()
def battle_invite(sender_player, invited_player, battle_invite_key, game_mode):
    battle_invite = BattleInvite(
        sender_username=sender_player.user.username,
        invited_username=invited_player.user.username,
        game_mode_id=game_mode.id,
    )
    cache.set(battle_invite_key, battle_invite)
    return battle_invite


def assert_accepted_battle(battle, sender_player, invited_player):
    sender_player_battle = sender_player.battle_players.first().battle
    invited_player_battle = invited_player.battle_players.first().battle
    assert isinstance(battle, Battle)
    assert len(redis_client.keys('*')) == 0
    assert sender_player.battle_players.count() == 1
    assert invited_player.battle_players.count() == 1
    assert sender_player_battle == invited_player_battle == battle
    assert Battle.objects.count() == 1


def test_get_empty(sender_player, invited_player):
    battle_invite = BattleInviteRepository.get(
        sender_player=sender_player, invited_player=invited_player
    )
    assert battle_invite is None


def test_get(battle_invite, sender_player, invited_player):
    created_battle_invite = BattleInviteRepository.get(
        sender_player=sender_player, invited_player=invited_player
    )
    assert isinstance(battle_invite, BattleInvite)
    assert created_battle_invite == battle_invite


def test_create_private(sender_player, invited_player, battle_invite_key, game_mode):
    battle_invite = BattleInviteRepository._create(
        sender_player=sender_player, invited_player=invited_player, game_mode=game_mode
    )

    assert isinstance(battle_invite, BattleInvite)
    assert battle_invite == BattleInviteRepository.get(
        sender_player=sender_player, invited_player=invited_player
    )
    assert battle_invite.dict() == cache.get(battle_invite_key)


def test_create(
    sender_player, invited_player, battle_invite_key, battle_invite_repository_lock, game_mode
):
    battle_invite = BattleInviteRepository.create(
        sender_player=sender_player, invited_player=invited_player, game_mode=game_mode
    )

    assert isinstance(battle_invite, BattleInvite)
    assert battle_invite == BattleInviteRepository.get(
        sender_player=sender_player, invited_player=invited_player
    )
    assert battle_invite.dict() == cache.get(battle_invite_key)
    battle_invite_repository_lock.assert_called_once_with(
        sender_player=invited_player, invited_player=sender_player
    )


def test_create_same_user(sender_player, battle_invite_repository_lock, game_mode):
    with pytest.raises(PermissionDenied) as e:
        BattleInviteRepository.create(
            sender_player=sender_player, invited_player=sender_player, game_mode=game_mode
        )
    assert PermissionDenied.message == e.value.message
    battle_invite_repository_lock.assert_not_called()


@pytest.mark.usefixtures('battle_invite')
def test_create_players_invited_each_other(
    sender_player, invited_player, battle_invite_repository_lock, game_mode
):
    battle = BattleInviteRepository.create(
        sender_player=invited_player, invited_player=sender_player, game_mode=game_mode
    )
    assert_accepted_battle(battle, sender_player, invited_player)
    battle_invite_repository_lock.assert_has_calls(
        [
            call(sender_player=sender_player, invited_player=invited_player),
            call().__enter__(),  # pylint: disable=unnecessary-dunder-call
            call(sender_player=sender_player, invited_player=invited_player),
            call().__enter__(),  # pylint: disable=unnecessary-dunder-call
            call().__exit__(None, None, None),
            call().__exit__(None, None, None),
        ]
    )


@pytest.mark.usefixtures('battle_invite')
def test_cancel(sender_player, invited_player):
    BattleInviteRepository.cancel(sender_player=sender_player, invited_player=invited_player)
    assert len(redis_client.keys('*')) == 0


@pytest.mark.usefixtures('battle_invite')
def test_cancel_wrong_user(sender_player, invited_player):
    with pytest.raises(PermissionDenied) as e:
        BattleInviteRepository.cancel(sender_player=invited_player, invited_player=sender_player)

    assert PermissionDenied.message == e.value.message
    assert len(redis_client.keys('*')) == 1


def test_cancel_non_existing_invite(sender_player, invited_player):
    with pytest.raises(PermissionDenied) as e:
        BattleInviteRepository.cancel(sender_player=sender_player, invited_player=invited_player)

    assert PermissionDenied.message == e.value.message
    assert len(redis_client.keys('*')) == 0


@pytest.mark.usefixtures('battle_invite')
def test_decline(sender_player, invited_player):
    BattleInviteRepository.decline(sender_player=sender_player, invited_player=invited_player)
    assert len(redis_client.keys('*')) == 0


@pytest.mark.usefixtures('battle_invite')
def test_decline_wrong_user(sender_player, invited_player):
    with pytest.raises(PermissionDenied) as e:
        BattleInviteRepository.decline(sender_player=invited_player, invited_player=sender_player)

    assert PermissionDenied.message == e.value.message
    assert len(redis_client.keys('*')) == 1


def test_decline_non_existing_invite(sender_player, invited_player):
    with pytest.raises(PermissionDenied) as e:
        BattleInviteRepository.decline(sender_player=sender_player, invited_player=invited_player)

    assert PermissionDenied.message == e.value.message
    assert len(redis_client.keys('*')) == 0


@pytest.mark.usefixtures('battle_invite')
def test_accept(sender_player, invited_player):
    battle = BattleInviteRepository.accept(
        sender_player=sender_player, invited_player=invited_player
    )
    assert_accepted_battle(battle, sender_player, invited_player)


@pytest.mark.usefixtures('battle_invite')
def test_accept_wrong_user(sender_player, invited_player):
    with pytest.raises(PermissionDenied) as e:
        BattleInviteRepository.accept(sender_player=invited_player, invited_player=sender_player)

    assert PermissionDenied.message == e.value.message
    assert len(redis_client.keys('*')) == 1


def test_accept_non_existing_invite(sender_player, invited_player):
    with pytest.raises(PermissionDenied) as e:
        BattleInviteRepository.accept(sender_player=sender_player, invited_player=invited_player)

    assert PermissionDenied.message == e.value.message
    assert len(redis_client.keys('*')) == 0
