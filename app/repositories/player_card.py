from typing import List

from app.models.card import Card
from app.models.player import Player, PlayerCard
from app.repositories.base import BaseRepository


class PlayerCardRepository(BaseRepository):

    DB_MODEL = PlayerCard

    @staticmethod
    def get(player: Player) -> List[Card]:
        list_card = []
        player_cards = list(PlayerCard.objects.filter(player=player).distinct('card'))
        for player_card in player_cards:
            if player_card.card.is_enabled and player_card.card not in list_card:
                list_card.append(player_card.card)
        return list_card
