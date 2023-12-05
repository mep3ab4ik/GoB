from typing import Union

import app.card_abilities.state
from app.card_abilities import actions, signatures
from app.models import battle
from app.services.tile import TileService


class G199(signatures.Spell):
    """
    Give a tile Shock. Both players draw a card.
    """

    def after_appear(
        self,
        state: app.card_abilities.state.State,
        destination: Union[battle.Tile, battle.BattlePlayer, None],
        source: battle.CardHand,
        target_tile=None,
    ):
        if isinstance(destination, battle.Tile):
            TileService.tile_update_element(
                state=state, tile=destination, new_element=battle.Tile.Elements.ELECTRIC
            )
        actions.move_card_from_deck_to_hand(
            state, deck_player=state.player, hand_player=state.player
        )
        actions.move_card_from_deck_to_hand(state, deck_player=state.enemy, hand_player=state.enemy)
