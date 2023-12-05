from app.models.battle import BattlePlayer, CardActiveMystery
from app.repositories.base import BaseRepository


class CardActiveMysteryRepository(BaseRepository):
    DB_MODEL = CardActiveMystery

    @staticmethod
    def delete_from_payers(players: list[BattlePlayer]):
        CardActiveMystery.objects.filter(player__in=players).delete()
