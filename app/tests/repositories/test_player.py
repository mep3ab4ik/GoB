# pylint: disable=protected-access,redefined-outer-name
import pytest
from django.conf import settings
from faker import Faker
from mock.mock import call

from app.models.player import Player
from app.models.user import User
from app.repositories.player import PlayerRepository
from app.schemas.player import PlayerStatusOverWebsocket
from app.schemas.ws_schemas import PlayerStatus


@pytest.fixture()
def redis_client(mocker):
    mock = mocker.patch('app.repositories.player.redis_client', ruturn_value=None)
    mock.zcard.return_value = None
    return mock


@pytest.fixture()
def _redis_client_zcard_side_effect_online(
    redis_client, player_status_battle_group_name, player_status_lobby_group_name
):
    def side_effect(value):
        if value == player_status_battle_group_name:
            return None
        if value == player_status_lobby_group_name:
            return 1
        return None

    redis_client.zcard.side_effect = side_effect


@pytest.fixture()
def player(db) -> Player:  # pylint: disable=unused-argument, invalid-name
    return Player.objects.create(user=User.objects.create(username=Faker().user_name()))


@pytest.fixture()
def player_status_in_battle() -> PlayerStatus:
    return PlayerStatus(
        title=PlayerStatusOverWebsocket.IN_BATTLE.value,
        name=PlayerStatusOverWebsocket.IN_BATTLE.value,
    )


@pytest.fixture()
def player_status_offline() -> PlayerStatus:
    return PlayerStatus(
        title=PlayerStatusOverWebsocket.OFFLINE.value,
        name=PlayerStatusOverWebsocket.OFFLINE.value,
    )


@pytest.fixture()
def player_status_online() -> PlayerStatus:
    return PlayerStatus(
        title=PlayerStatusOverWebsocket.ONLINE.value,
        name=PlayerStatusOverWebsocket.ONLINE.value,
    )


@pytest.fixture()
def _set_player_status(player):
    player.status_id = 'away'
    player.save()


@pytest.fixture()
def player_status_away(player) -> PlayerStatus:
    return PlayerStatus(title=player.status.title, name=player.status.name)


@pytest.fixture()
def player_status_battle_group_name(player) -> str:
    return f'asgi:group:{settings.BATTLE_CONSUMER_REDIS_GROUP_PREFIX}-{player.user_id}-events'


@pytest.fixture()
def player_status_lobby_group_name(player) -> str:
    return f'asgi:group:{settings.LOBBY_CONSUMER_REDIS_GROUP_PREFIX}-{player.user_id}'


def test_player_status_in_battle(
    redis_client, player_status_in_battle, player_status_battle_group_name, player
):
    redis_client.zcard.return_value = 1
    status = PlayerRepository.get_player_status(player)
    redis_client.zcard.assert_called_once_with(player_status_battle_group_name)
    assert status == player_status_in_battle


def test_player_status_offline(
    redis_client,
    player_status_offline,
    player_status_lobby_group_name,
    player_status_battle_group_name,
    player,
):
    status = PlayerRepository.get_player_status(player)
    redis_client.zcard.assert_has_calls(
        [call(player_status_battle_group_name), call(player_status_lobby_group_name)]
    )
    assert status == player_status_offline


@pytest.mark.usefixtures('_redis_client_zcard_side_effect_online')
def test_player_status_online(
    redis_client,
    player_status_online,
    player_status_lobby_group_name,
    player_status_battle_group_name,
    player,
):
    status = PlayerRepository.get_player_status(player)
    redis_client.zcard.assert_has_calls(
        [call(player_status_battle_group_name), call(player_status_lobby_group_name)]
    )
    assert status == player_status_online


@pytest.mark.usefixtures('_redis_client_zcard_side_effect_online', '_set_player_status')
def test_player_status_away(
    redis_client,
    player_status_away,
    player_status_lobby_group_name,
    player_status_battle_group_name,
    player,
):
    status = PlayerRepository.get_player_status(player)
    redis_client.zcard.assert_has_calls(
        [call(player_status_battle_group_name), call(player_status_lobby_group_name)]
    )
    assert status == player_status_away
