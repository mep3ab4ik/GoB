from typing import Union

from app.card_abilities import signatures
from app.card_abilities.actions import move_card_from_tile_to_hand
from app.models import battle


class G214(signatures.Spell):
    """
    All creatures are returned to their owners' hands.
    """

    def after_appear(
        self,
        state: signatures.State,
        destination: battle.Tile,
        source: Union[battle.CardHand, battle.CardGraveyard],
        target_tile: Union[None, battle.Tile] = None,
    ):
        all_creatures = [
            *state.enemy.tile.non_free().exclude_mia(),
            *state.player.tile.non_free().exclude_mia(),
        ]
        for creature in all_creatures:
            move_card_from_tile_to_hand(state=state, tile=creature, hand_player=creature.player)
