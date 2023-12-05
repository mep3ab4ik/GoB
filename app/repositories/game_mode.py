from app.models.card import Card
from app.models.game_mode import GameMode
from app.repositories.base import BaseRepository


class GameModeRepository(BaseRepository):
    DB_MODEL = GameMode

    @staticmethod
    def get_game_mode(game_mode_id: int = None) -> GameMode:
        if game_mode_id:
            return GameMode.objects.filter(id=game_mode_id).first()
        return GameMode.objects.filter(
            default_game_mode=True, earn_skill_points_in_this_mode=False
        ).first()

    @staticmethod
    def get_blocked_cards(game_mode: GameMode) -> set[Card]:
        return {x.card for x in game_mode.blocked_cards.all()}
