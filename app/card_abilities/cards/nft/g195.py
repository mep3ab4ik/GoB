from typing import List

import app.card_abilities.state
from app.card_abilities import actions, signatures
from app.enums.card import CardTypesEnum
from app.models import battle, card


class G195(signatures.Mystery):
    """
    Mystery: When a friendly creature dies, Ensnare all enemy creatures.
    """

    def on_friendly_creature_death(
        self,
        state: app.card_abilities.state.State,
        active_mystery: battle.CardActiveMystery,
        creature_card: card.Card,
    ):
        player = state.player if active_mystery.player != state.player else state.enemy
        enemy = state.enemy if state.enemy == player else state.player
        signatures.send_mystery_card_activated_event(state, player, active_mystery)

        enemy_serfs: List[battle.Tile] = (
            enemy.tile.exclude_mia()
            .exclude(card__isnull=True)
            .filter(card__type=CardTypesEnum.serf)
        )
        actions.ensnare_tiles(state, tiles=enemy_serfs, turns=1)
        super().disappear(state, active_mystery)
