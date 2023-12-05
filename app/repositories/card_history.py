from app.models.battle import Battle, BattlePlayer
from app.models.card import Card, CardHistory
from app.repositories.base import BaseRepository


class CardHistoryRepository(BaseRepository):

    DB_MODEL = CardHistory

    @staticmethod
    def create_card_history(
        battle_player: BattlePlayer,
        card: Card,
        battle: Battle,
        turn_number: int,
        record_type: CardHistory.RecordTypes,
    ) -> None:
        CardHistory.objects.create(
            battle_player=battle_player,
            card=card,
            battle=battle,
            turn_number=turn_number,
            record_type=record_type,
        )
