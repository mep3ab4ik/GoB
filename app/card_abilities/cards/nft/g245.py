from typing import Union

import app.card_abilities.state
from app.card_abilities import actions, signatures
from app.models import battle


class G245(signatures.DigMixin, signatures.Serf):
    """
    Dig
    Warcry: Give a friendly creature +3 HP.
    """

    def after_appear(
        self,
        state: app.card_abilities.state.State,
        destination: battle.Tile,
        source: Union[battle.CardHand, battle.CardGraveyard],
        target_tile=None,
    ):
        if target_tile:
            actions.add_hp_enchantment_to_tile(state, target_tile, value=3)
