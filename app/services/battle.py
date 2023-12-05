from uuid import uuid4

from app.models.battle import Battle, BattlePlayer
from app.models.game_mode import GameMode
from app.models.player import Player
from app.repositories.battle import BattleRepository
from app.repositories.battle_player import BattlePlayerRepository


class BattleService:
    @classmethod
    def create_battle(cls, player: Player, game_mode: GameMode) -> Battle:
        battle: Battle = BattleRepository.create(
            room_id=str(uuid4()),
            player_1_ticket=str(uuid4()),
            game_mode=game_mode,
            game_mode_season=game_mode.current_season,
        )
        BattlePlayerRepository.create(
            idx=BattlePlayer.PlayerId.ONE,
            battle=battle,
            player=player,
            hp=game_mode.start_battle_player_hp,
        )
        return battle

    @staticmethod
    def battle_join(battle: Battle, player: Player) -> Battle:
        assert battle.state not in [
            Battle.States.COMPLETED,
            Battle.States.DISCARDED,
        ], 'Battle already closed'
        BattlePlayerRepository.create(
            idx=BattlePlayer.PlayerId.TWO,
            battle=battle,
            player=player,
            hp=battle.game_mode.start_battle_player_hp,
        )
        BattleRepository.update(battle, player_2_ticket=str(uuid4()), state=Battle.States.CLOSED)
        BattleRepository.save(battle)
        return battle
