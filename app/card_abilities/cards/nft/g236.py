from typing import Union

import app.card_abilities.state
from app.card_abilities import actions, signatures
from app.models import battle


class G236(signatures.Serf):
    """
    Gains +3 ATK when on an Electric tile.
    """

    def after_appear(
        self,
        state: app.card_abilities.state.State,
        destination: battle.Tile,
        source: Union[battle.CardHand, battle.CardGraveyard],
        target_tile=None,
    ):
        # Basic card attack: 1
        # Buff from tile since tile is electric: 1
        # The buff of this card from placing on an electric tile: 3
        # Since the total attack with all the buffs of the card should be 5
        if destination.element == battle.Tile.Elements.ELECTRIC:
            actions.add_attack_enchantment_to_tile(state, tile=destination, value=3)
