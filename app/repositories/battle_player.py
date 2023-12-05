from app.models.battle import Battle, BattlePlayer
from app.repositories.base import BaseRepository


class BattlePlayerRepository(BaseRepository):
    DB_MODEL = BattlePlayer

    @staticmethod
    def get(player_id: int, battle: Battle) -> BattlePlayer:
        return battle.players.get(player_id=player_id)

    @staticmethod
    def get_enemy_player(exclude_player_id: int, battle: Battle) -> BattlePlayer:
        return (
            BattlePlayer.objects.filter(battle=battle).exclude(player_id=exclude_player_id).first()
        )

    @staticmethod
    def filter_to_battle(battle: Battle):
        return battle.players.all()
