from app.models.battle import BattlePlayer, CardGraveyard
from app.repositories.base import BaseRepository


class CardGraveyardRepository(BaseRepository):
    DB_MODEL = CardGraveyard

    @staticmethod
    def delete_from_payers(players: list[BattlePlayer]):
        CardGraveyard.objects.filter(player__in=players).delete()
