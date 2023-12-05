from enum import Enum


class PlayerStatusOverWebsocket(Enum):
    """Player network statuses"""

    ONLINE = 'online'  #: Player is online
    OFFLINE = 'offline'  #: Player is offline
    IN_BATTLE = 'in_battle'  #: Player is in battle
