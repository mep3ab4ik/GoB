from typing import Optional, Union

import app.card_abilities.state
from app.card_abilities import actions, signatures
from app.enums.card import CardElementsEnum
from app.models import battle


class G230(signatures.DigMixin, signatures.WarcryMixin, signatures.Serf):
    """Dig
    Warcry: Give a creature +1/+1 for each Earth card you have in hand.
    """

    def after_appear(
        self,
        state: app.card_abilities.state.State,
        destination: battle.Tile,
        source: Union[battle.CardHand, battle.CardGraveyard],
        target_tile: Optional[battle.Tile] = None,
    ):
        buff: int = battle.CardHand.objects.filter(
            player=source.player, card__element=CardElementsEnum.earth
        ).count()
        if buff == 0 or not target_tile:
            return

        actions.add_hp_enchantment_to_tile(state, target_tile, buff)
        actions.add_attack_enchantment_to_tile(state, target_tile, buff)
