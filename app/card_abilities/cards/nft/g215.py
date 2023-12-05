from typing import Union

import app.card_abilities.state
from app.card_abilities import signatures
from app.enums.card import CardTypesEnum
from app.models import battle
from app.repositories.base import BaseRepository
from app.services.tile import TileService


class G215(signatures.Spell):
    """
    Deal 3 damage to 2 random creatures. Tiles occupied by those creatures gain Shock.
    """

    def after_appear(
        self,
        state: app.card_abilities.state.State,
        destination: battle.Tile,
        source: Union[battle.CardHand, battle.CardGraveyard],
        target_tile: Union[None, battle.Tile] = None,
    ):
        enemy_serfs = [
            *state.enemy.tile.exclude(card__isnull=True).filter(card__type=CardTypesEnum.serf),
            *state.player.tile.exclude(card__isnull=True).filter(card__type=CardTypesEnum.serf),
        ]
        tiles = BaseRepository.random_objects(subsequence=enemy_serfs, count_objects=2)
        self.spell_attack_tiles(state, damage=3, tiles=tiles)

        for tile in tiles:
            tile.refresh_from_db()
            TileService.tile_update_element(
                state=state, tile=tile, new_element=battle.Tile.Elements.ELECTRIC
            )
