from app.models.battle import BattlePlayer, Control
from app.repositories.base import BaseRepository


class ControlRepository(BaseRepository):

    DB_MODEL = Control

    @staticmethod
    def delete_from_payers(players: list[BattlePlayer]):
        Control.objects.filter(player__in=players).delete()
