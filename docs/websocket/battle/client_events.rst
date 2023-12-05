Client Events
---------------

Client events are events that are sent in the messages from the client to the server.


Format
~~~~~~~~~~~~~~~

.. code-block:: python

    {
      "event": "<event_name>",
      "params": {
        "<name>": "<value>"
      }
    }


Events List
~~~~~~~~~~~~~~~

.. autoclass:: app.ws_consumers.battle_consumer.BattleConsumer
   :noindex:
   :members: battle_next_round, card_from_hand_to_tile, card_from_hand_to_tile_with_target, tile_attack_tile, battle_surrender, tile_attack_player, play_spell_card, select_card_in_hand, play_mystery_card, cancel_battle, ready_for_battle

