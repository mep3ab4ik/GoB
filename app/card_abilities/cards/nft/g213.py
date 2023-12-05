from typing import Union

import app.card_abilities.state
from app.card_abilities import actions, signatures
from app.models import battle


class G213(signatures.AquaMixin, signatures.Serf):
    """
    Aqua
    Insult
    Warcry: Give a creature Invisibility.
    """

    def after_appear(
        self,
        state: app.card_abilities.state.State,
        destination: battle.Tile,
        source: Union[battle.CardHand, battle.CardGraveyard],
        target_tile=None,
    ):
        actions.add_insult_enchantment(state=state, tile=destination)
        if target_tile:
            actions.add_invisible_enchantment(state, target_tile)
