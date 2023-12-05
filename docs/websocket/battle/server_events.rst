Server Events
---------------

Server events are events that are sent in the messages from the server to the client.


Format
~~~~~~~~~~~~~~~

Events that appear at the same time are passed in one socket message.

.. code-block:: python

    {
      "events": [
        {
          "event": "<event_name>",
          "params": {
            "<name>": "<value>"
          }
        }
      ]
    }



Events List
~~~~~~~~~~~~~~~

.. autoclass:: app.ws_consumers.battle_consumer.BattleConsumer
    :members: battle_state, play_start_battle_animations, start_battle, opponent_selected_card, move_card_from_hand_to_deck, move_card_from_hand_to_graveyard, move_card_from_graveyard_to_hand, move_card_from_deck_to_hand, move_card_from_deck_to_graveyard, move_card_from_hand_to_tile, move_card_from_graveyard_to_deck, move_card_from_tile_to_deck, spell_card_played, player_joined, opponent_joined, opponent_left, next_turn, battle_complete, server_error, abilities_debug_logger, tile_card_death, move_card_from_tile_to_graveyard, creature_attack_creature, creature_attack_avatar, avatar_damage, creature_damage, reveal_card_from_hand, move_card_from_graveyard_to_tile, mystery_card_played, mystery_card_activated, battle_cancelled, reveal_card_from_deck,enchant_tile, player_avatar_increase_hp, add_hp_enchantment, add_attack_enchantment, add_insult_enchantment, mia_enchantment_removed, buff_activated, compare_revealed_deck_cards, move_card_from_tile_to_hand, resurrect_card, enchant_hand_card

