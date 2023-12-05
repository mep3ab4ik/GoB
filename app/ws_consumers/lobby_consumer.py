# pylint: disable=too-many-ancestors
from .mixins.battle_invite import BattleInviteMixin
from .mixins.friendship import FriendshipMixin


class LobbyConsumer(FriendshipMixin, BattleInviteMixin):
    def __init__(self):
        super().__init__()
        FriendshipMixin.update_handlers_mapping(
            self.WS_HANDLERS_MAPPING, self.CHANNEL_HANDLERS_MAPPING
        )
        BattleInviteMixin.update_handlers_mapping(
            self.WS_HANDLERS_MAPPING, self.CHANNEL_HANDLERS_MAPPING
        )
