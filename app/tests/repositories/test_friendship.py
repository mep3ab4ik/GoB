# pylint: disable=protected-access,redefined-outer-name
import pytest
from faker import Faker

from app.exceptions import PermissionDenied
from app.models.player import Friendship, Player
from app.models.user import User
from app.repositories.friendship import FriendshipRepository
from app.schemas.friendship import FriendshipStatus


def create_player() -> Player:
    return Player.objects.create(user=User.objects.create(username=Faker().user_name()))


@pytest.fixture()
def player_1(db) -> Player:  # pylint: disable=unused-argument, invalid-name
    return create_player()


@pytest.fixture()
def player_2(db) -> Player:  # pylint: disable=unused-argument, invalid-name
    return create_player()


@pytest.fixture()
def player_3(db) -> Player:  # pylint: disable=unused-argument, invalid-name
    return create_player()


@pytest.fixture()
def friendship(player_1, player_2):
    player1, player2 = sorted([player_1, player_2], key=lambda x: x.id)
    return Friendship.objects.create(friend=player1, player=player2, sender=player_1)


@pytest.fixture()
def _accepted_friendship(friendship):
    friendship.is_accepted = True
    friendship.save()


def test_create(player_1, player_2):
    friendship = FriendshipRepository.create(sender_player=player_1, invited_player=player_2)
    assert isinstance(friendship, Friendship)
    assert friendship.friend == player_1
    assert friendship.player == player_2


def test_create_from_lower_id_to_higher(player_1, player_2):
    friendship = FriendshipRepository.create(sender_player=player_2, invited_player=player_1)
    assert isinstance(friendship, Friendship)
    assert friendship.friend == player_1
    assert friendship.player == player_2


def test_create_same_user(player_1):
    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.create(sender_player=player_1, invited_player=player_1)
    assert PermissionDenied.message == e.value.message


@pytest.mark.usefixtures('friendship')
def test_exists_error(player_1, player_2):
    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.create(sender_player=player_1, invited_player=player_2)
    assert PermissionDenied.message == e.value.message


def test_get(friendship, player_1, player_2, player_3):
    get_friendship = FriendshipRepository._get_friendship(player_1, player_2)
    assert isinstance(get_friendship, Friendship)
    assert get_friendship == friendship

    get_friendship = FriendshipRepository._get_friendship(player_1, player_3)
    assert get_friendship is None


@pytest.mark.usefixtures('friendship')
def test_accept(player_1, player_2):
    friendship = FriendshipRepository.accept(sender_player=player_1, invited_player=player_2)
    assert isinstance(friendship, Friendship)
    assert friendship.is_accepted is True


def test_accept_non_existing(player_1):
    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.accept(sender_player=player_1, invited_player=player_1)
    assert PermissionDenied.message == e.value.message


@pytest.mark.usefixtures('friendship')
def test_accept_same_user(player_1, player_2):
    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.accept(sender_player=player_2, invited_player=player_1)
    assert PermissionDenied.message == e.value.message


@pytest.mark.usefixtures('friendship')
def test_cancel(player_1, player_2):
    FriendshipRepository.cancel(sender_player=player_1, invited_player=player_2)
    assert FriendshipRepository._get_friendship(player_1, player_2) is None


@pytest.mark.usefixtures('friendship')
def test_cancel_same_user(player_1, player_2):
    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.cancel(sender_player=player_2, invited_player=player_1)
    assert PermissionDenied.message == e.value.message


@pytest.mark.usefixtures('friendship')
def test_cancel_non_existing(player_1):
    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.cancel(sender_player=player_1, invited_player=player_1)
    assert PermissionDenied.message == e.value.message


@pytest.mark.usefixtures('friendship')
def test_decline(player_1, player_2):
    FriendshipRepository.decline(sender_player=player_2, invited_player=player_1)
    assert FriendshipRepository._get_friendship(player_1, player_2) is None


@pytest.mark.usefixtures('friendship')
def test_decline_same_user(player_1, player_2):
    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.decline(sender_player=player_1, invited_player=player_2)
    assert PermissionDenied.message == e.value.message


@pytest.mark.usefixtures('friendship')
def test_decline_non_existing(player_1):
    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.cancel(sender_player=player_1, invited_player=player_1)
    assert PermissionDenied.message == e.value.message


@pytest.mark.usefixtures('_accepted_friendship')
def test_remove(player_1, player_2):
    FriendshipRepository.remove(player1=player_1, player2=player_2)
    assert FriendshipRepository._get_friendship(player_1, player_2) is None

    player1, player2 = sorted([player_1, player_2], key=lambda x: x.id)
    Friendship.objects.create(friend=player1, player=player2, sender=player_1, is_accepted=True)

    FriendshipRepository.remove(player1=player_2, player2=player_1)
    assert FriendshipRepository._get_friendship(player_2, player_1) is None


@pytest.mark.usefixtures('friendship')
def test_remove_is_accepted(player_1, player_2):
    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.remove(player1=player_1, player2=player_2)
    assert PermissionDenied.message == e.value.message


@pytest.mark.usefixtures('friendship')
def test_remove_non_existing(player_1, player_3):
    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.remove(player1=player_1, player2=player_3)
    assert PermissionDenied.message == e.value.message

    with pytest.raises(PermissionDenied) as e:
        FriendshipRepository.remove(player1=player_1, player2=player_1)
    assert PermissionDenied.message == e.value.message


def test_get_list_empty(friendship, player_1, player_2, player_3):
    friendship_list_player1 = list(
        FriendshipRepository.get_friendship_list(player=player_1, is_accepted=True)
    )
    assert not friendship_list_player1

    friendship_list_player2 = list(
        FriendshipRepository.get_friendship_list(player=player_2, is_accepted=True)
    )
    assert not friendship_list_player2

    friendship_list_player3 = list(
        FriendshipRepository.get_friendship_list(player=player_3, is_accepted=False)
    )
    assert not friendship_list_player3

    friendship_list_player1 = list(
        FriendshipRepository.get_friendship_list(player=player_1, is_accepted=False)
    )
    assert friendship_list_player1 == [friendship]

    friendship_list_player2 = list(
        FriendshipRepository.get_friendship_list(player=player_1, is_accepted=False)
    )
    assert friendship_list_player2 == [friendship]


def test_get_status_relative_player(friendship, player_1, player_2):
    player_1_status = FriendshipRepository.get_status_relative_player(friendship, player_1)
    player_2_status = FriendshipRepository.get_status_relative_player(friendship, player_2)
    assert player_1_status == FriendshipStatus.REQUESTED
    assert player_2_status == FriendshipStatus.RECEIVED
    friendship.is_accepted = True
    friendship.save()
    player_1_status = FriendshipRepository.get_status_relative_player(friendship, player_1)
    player_2_status = FriendshipRepository.get_status_relative_player(friendship, player_2)
    assert player_1_status == FriendshipStatus.ACCEPTED
    assert player_2_status == FriendshipStatus.ACCEPTED
