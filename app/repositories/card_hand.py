from typing import Optional

from django.core.exceptions import ObjectDoesNotExist

from app.models.battle import BattlePlayer, CardHand
from app.repositories.base import BaseRepository


class HandCardRepository(BaseRepository):

    DB_MODEL = CardHand

    @staticmethod
    def hand_card_get_from_id(hand_card_id: int) -> Optional[CardHand]:
        try:
            return CardHand.objects.get(id=hand_card_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def delete_from_payers(players: list[BattlePlayer]):
        CardHand.objects.filter(player__in=players).delete()
