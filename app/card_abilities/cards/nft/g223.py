from typing import Union

import app.card_abilities.state
from app.card_abilities import actions, signatures
from app.models import battle


class G223(signatures.AquaMixin, signatures.Serf):
    """
    MIA for 2 turns.
    Aqua
    """

    def after_appear(
        self,
        state: app.card_abilities.state.State,
        destination: battle.Tile,
        source: Union[battle.CardHand, battle.CardGraveyard],
        target_tile=None,
    ):
        actions.add_mia_enchantment(state, destination, turns=3)  # 2 turns for each player
