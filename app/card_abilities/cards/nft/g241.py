from typing import Union

from app.card_abilities import actions, signatures
from app.models import battle


class G241(signatures.BurnMixin, signatures.Serf):
    """
    Burn
    Warcry: Ensnare a creature.
    """

    def after_appear(
        self,
        state: signatures.State,
        destination: battle.Tile,
        source: Union[battle.CardHand, battle.CardGraveyard],
        target_tile=None,
    ):
        if target_tile:
            actions.ensnare_tiles(state, tiles=[target_tile], turns=1)
