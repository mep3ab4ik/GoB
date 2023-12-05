from typing import Optional

from django.core.exceptions import ObjectDoesNotExist

from app.models.battle import BattlePlayer, Tile
from app.models.card import Card
from app.repositories.base import BaseRepository
from app.schemas import battle as schemas_battle


class TileRepository(BaseRepository):

    DB_MODEL = Tile

    @classmethod
    def create_from_battle_player(
        cls, battle_player: BattlePlayer, state: Optional[schemas_battle.Battle] = None
    ) -> Optional[Tile]:
        last_player_tile = Tile.objects.filter(player=battle_player).last()
        last_tile_order = last_player_tile.order if last_player_tile else 0
        if last_tile_order >= battle_player.battle.game_mode.max_tiles_per_player:
            return None
        tile = Tile.objects.create(player=battle_player, order=last_tile_order + 1)
        if state:
            cls._create_cache(battle_player=battle_player, state=state, tile=tile)
        return tile

    @staticmethod
    def _create_cache(battle_player: BattlePlayer, state: schemas_battle.Battle, tile: Tile):
        state.players[battle_player.player.id].tiles[tile.id] = schemas_battle.Tile(id=tile.id)

    @staticmethod
    def get_tile_from_id(tile_id: int) -> Optional[Tile]:
        try:
            return Tile.objects.get(id=tile_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def update_tile(
        *,
        card: Card,
        tile: Tile,
        card_death_count: int = 0,
        clear_description: bool = False,
        remove_mummy: bool = False,
        remove_last_breath: bool = False,
        original_card: Optional[Card] = None,
        battle_card_id: Optional[int] = None,
    ) -> Tile:
        tile.card = card
        tile.hp = card.hp
        tile.attack = card.attack
        tile.state = Tile.States.ASLEEP
        tile.card_death_count = card_death_count
        tile.clear_description = clear_description
        tile.remove_mummy = remove_mummy
        tile.remove_last_breath = remove_last_breath
        tile.original_card = original_card
        tile.battle_card_id = battle_card_id
        return tile

    @staticmethod
    def delete_from_payers(players: list[BattlePlayer]):
        Tile.objects.filter(player__in=players).delete()

    @classmethod
    def update_element(cls, tile: Tile, new_element: str):
        tile.element = new_element
