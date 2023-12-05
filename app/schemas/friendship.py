from enum import Enum


class FriendshipStatus(Enum):
    """Friendship statuses"""

    REQUESTED = 'requested'  #: Player send friend request to another player
    RECEIVED = 'received'  #: Player receive friend request from another player
    ACCEPTED = 'accepted'  #: Player is your accepted friend
