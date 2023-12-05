from typing import Union

from app.card_abilities import actions, signatures
from app.models import battle


class G231(signatures.Serf):
    """Warcry: Destroy all enemy Mystery cards."""

    def after_appear(
        self,
        state: signatures.State,
        destination: battle.Tile,
        source: Union[battle.CardHand, battle.CardGraveyard],
        target_tile=None,
    ):
        mystery_cards = state.enemy.active_mystery.all()

        for card in mystery_cards:
            actions.move_mystery_card_from_hand_to_graveyard(state, card, state.enemy)
