import app.card_abilities.state
from app.card_abilities import signatures
from app.models import battle
from app.repositories.base import BaseRepository
from app.services.tile import TileService


class G201(signatures.DigMixin, signatures.Serf):
    """Dig
    Last Breath: Give 2 random friendly tiles Dig
    """

    def after_death(self, state: app.card_abilities.state.State, target: battle.Tile):
        tile_ids = list(
            battle.BattlePlayer.objects.get(tile=target).tile.values_list('id', flat=True)
        )
        tile_ids = BaseRepository.random_objects(subsequence=tile_ids, count_objects=2)
        tiles = battle.Tile.objects.filter(id__in=tile_ids)
        for tile in tiles:
            TileService.tile_update_element(
                state=state, tile=tile, new_element=battle.Tile.Elements.EARTH
            )
