from typing import Union

import app.card_abilities.state
from app.card_abilities import actions, signatures
from app.enums.card import CardTypesEnum
from app.models import battle


class G261(signatures.Spell):
    """
    Return all enemy creatures with an ATK less than the number
    of Water tiles you control to their owner's hand.
    """

    def after_appear(
        self,
        state: app.card_abilities.state.State,
        destination: battle.Tile,
        source: Union[battle.CardHand, battle.CardGraveyard],
        target_tile: Union[None, battle.Tile] = None,
    ):
        count_water_tiles = state.player.tile.filter(element=battle.Tile.Elements.WATER).count()
        tiles = state.enemy.tile.exclude(card__isnull=True).filter(card__type=CardTypesEnum.serf)

        for tile in tiles:
            if tile.get_attack_with_enchantments < count_water_tiles:
                actions.move_card_from_tile_to_hand(state=state, tile=tile, hand_player=state.enemy)
