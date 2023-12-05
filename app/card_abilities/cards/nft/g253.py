import random
from typing import Union

import app.card_abilities.state
from app import battle_service
from app.card_abilities import actions, signatures
from app.models import battle


class G253(signatures.Spell):
    """
    Destroy a creature with less than 4 ATK. Gain 4 Health.
    """

    def after_appear(
        self,
        state: app.card_abilities.state.State,
        destination: Union[battle.Tile, battle.BattlePlayer, None],
        source: battle.CardHand,
        target_tile=None,
    ):
        all_creatures = [
            *state.enemy.tile.non_free().exclude_mia(),
            *state.player.tile.non_free().exclude_mia(),
        ]
        target_creatures = [
            creature for creature in all_creatures if creature.get_attack_with_enchantments < 4
        ]
        if target_creatures:
            random_target = random.choice(target_creatures)
            card_behavior = battle_service.get_card_behavior(random_target)
            card_behavior.death(state, random_target)
        actions.add_hp_to_battle_player(state=state, target_player=state.player, value=4)
