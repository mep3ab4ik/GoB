from enum import Enum


class EventResponseType(Enum):
    ERROR = 'ERROR'
    FRIEND_LIST = 'friends.list'
    FRIEND_UPDATED = 'friend.updated'
    FRIEND_CONNECTED = 'friend.connected'
    FRIEND_DISCONNECTED = 'friend.disconnected'
    FRIENDSHIP_REQUEST_RECEIVE = 'friends.request.show'
    FRIENDS_REQUEST_DECLINE = 'friends.request.decline'
    FRIENDS_REQUEST_REMOVE = 'friend.remove'
    FRIENDS_REQUEST_CANCEL = 'friends.request.cancel'
    FRIENDS_REQUEST_ACCEPT = 'friends.request.accept'

    BATTLE_INVITE_RECEIVE = 'battle.invite.show'
    BATTLE_INVITE_CANCEL = 'battle.invite.cancel'
    BATTLE_INVITE_DECLINE = 'battle.invite.decline'
    BATTLE_INVITE_ACCEPT = 'battle.invite.accept'


class EventRequestType(Enum):
    pass


class EventRequestFriendshipType(EventRequestType):
    FRIENDSHIP_REQUEST_CREATE = 'friends_request_send'
    FRIENDSHIP_REQUEST_DECLINE = 'friends_request_decline'
    FRIENDSHIP_REMOVE = 'friend_remove'
    FRIENDSHIP_REQUEST_CANCEL = 'friends_request_cancel'
    FRIENDSHIP_REQUEST_ACCEPT = 'friends_request_accept'


class EventRequestBattleInviteType(EventRequestType):
    BATTLE_INVITE_CREATE = 'battle_invite_send'
    BATTLE_INVITE_CANCEL = 'battle_invite_cancel'
    BATTLE_INVITE_DECLINE = 'battle_invite_decline'
    BATTLE_INVITE_ACCEPT = 'battle_invite_accept'


class ChannelEventType(Enum):
    HANDLE_UPDATE_FRIENDSHIP_LIST = 'handle_channel_update_friendship_list'
    HANDLE_CHANNEL_USER_STATUS = 'handle_channel_user_status'
    HANDLE_FRIENDSHIP_REQUEST_RECEIVE = 'handle_channel_friendship_request_receive'

    HANDLE_BATTLE_INVITE_SHOW = 'handle_channel_battle_invite_show'
    HANDLE_BATTLE_INVITE_ACCEPT = 'handle_channel_battle_invite_accept'


class EventRequestPlayerStatusType(EventRequestType):
    CHANGE_PLAYER_STATUS = 'change_player_status'
