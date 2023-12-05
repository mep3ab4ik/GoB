# pylint: disable=protected-access,redefined-outer-name
import pytest
from faker import Faker

from app.models.battle import Battle
from app.models.game_mode import GameMode
from app.models.player import Player
from app.models.user import User
from app.repositories.battle import BattleRepository
from app.schemas.battle import BattleInvite


@pytest.fixture()
def sender_player(db) -> Player:  # pylint: disable=unused-argument, invalid-name
    return Player.objects.create(user=User.objects.create(username=Faker().user_name()))


@pytest.fixture()
def invited_player(db) -> Player:  # pylint: disable=unused-argument, invalid-name
    return Player.objects.create(user=User.objects.create(username=Faker().user_name()))


@pytest.fixture()
def game_mode(db) -> GameMode:  # pylint: disable=unused-argument, invalid-name
    return GameMode.objects.create(
        title='test',
        description='test',
        battlefield_timer_duration=60,
        default_game_mode=True,
        earn_skill_points_in_this_mode=False,
    )


def test_battle_create(game_mode, sender_player, invited_player):
    battle_invite = BattleInvite(
        sender_username=sender_player.user.username,
        invited_username=invited_player.user.username,
        game_mode_id=1,
    )
    battle = BattleRepository.create_battle(game_mode, sender_player, invited_player, battle_invite)
    assert isinstance(battle, Battle)
