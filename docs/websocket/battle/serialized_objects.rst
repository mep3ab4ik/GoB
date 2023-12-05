
Serialized Objects
------------------------------
Battle Object
~~~~~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :widths: 25 25 50
   :header-rows: 1
   :class: tight-table

   * - FIELD
     - TYPE
     - DESCRIPTION
   * - room_id
     - String
     - Battle Room ID
   * - state
     - Enum (String)
     - Current Room State. Possible options: CREATED, JOINED, ACTIVE, COMPLETED, DISCARDED
   * - winner
     - Int or null
     - Player object id of winner or null
   * - player_1_ticket
     - String
     - Room ticket for player 1
   * - player_2_ticket
     - String
     - Room ticket for player 2
   * - players
     - List of Objects
     - List of BattlePlayer objects
   * - turn
     - Int
     - 1 or 2
   * - cards_history
     - List of Objects
     - List of Card objects

Current Room State Options:
~~~~~~~~~~~~~~~~~~~~~~~~~~~
- CREATED - when the battle is created
- JOINED - when the first player joins
- CLOSED - when the second player is allocated
- ACTIVE - when the second player joins
- COMPLETED - when the battle is completed
- DISCARDED - when the battle is discarded because the player didn't wait for his opponent, or battle not completed (no auto resolution for now)

BattlePlayer Object
~~~~~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :widths: 25 25 50
   :header-rows: 1
   :class: tight-table

   * - FIELD
     - TYPE
     - DESCRIPTION
   * - idx
     - Enum (Int)
     - Player number. Options: 1, 2
   * - player
     - Int
     - Player object id
   * - battle
     - Int
     - Battle object id
   * - health
     - Int
     - Player health
   * - deck_counter
     - Int
     - Number of cards in the deck
   * - hand
     - List of Objects
     - List of CardHand objects
   * - graveyard
     - List of Objects
     - List of CardGraveyard objects
   * - tiles
     - List of Objects
     - List of Tile objects
   * - control
     - List of Objects
     - List of Control objects
   * - active_mystery
     - List of Objects
     - List of CardActiveMystery objects


CardHand Object
~~~~~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :widths: 25 25 50
   :header-rows: 1
   :class: tight-table

   * - FIELD
     - TYPE
     - DESCRIPTION
   * - id
     - Int
     - CardHand object id
   * - hp
     - Int
     - CardHand object hp
   * - attack
     - Int
     - CardHand object attack
   * - order
     - Int
     - CardHand object order
   * - card
     - Object  or null
     - Card object


CardGraveyard Object
~~~~~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :widths: 25 25 50
   :header-rows: 1
   :class: tight-table

   * - FIELD
     - TYPE
     - DESCRIPTION
   * - id
     - Int
     - CardGraveyard object id
   * - hp
     - Int
     - CardGraveyard object hp
   * - attack
     - Int
     - CardGraveyard object attack
   * - order
     - Int
     - CardGraveyard object order
   * - card
     - Object  or null
     - Card object


Card Object
~~~~~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :widths: 25 25 50
   :header-rows: 1
   :class: tight-table

   * - FIELD
     - TYPE
     - DESCRIPTION
   * - custom_id
     - String
     - Card custom id
   * - name
     - String
     - Card name
   * - rarity
     - Enum (String)
     - Card rarity. Options: common, rare, epic, legendary
   * - description
     - String
     - Card Description
   * - type
     - Enum (String)
     - Card type. Options: serf, spell, mystery
   * - targeting
     - Enum (String)
     - Targeting. Options: regular, target
   * - targeting_type
     - Enum (String)
     - Targeting Types. Options: only_opponent_tiles, only_opponent_creatures, only_opponent_avatar, only_opponent_everything, only_player_tiles, only_player_creatures, only_player_avatar, only_player_everything, both_player_tiles, both_player_avatars, both_player_creatures, both_player_everything
   * - element
     - Enum (String)
     - Card Element. Options: neutral, water, fire, earth, electric
   * - hp
     - Int
     - Card obj hp (initial value)
   * - attack
     - Int
     - Card obj attack (initial value)

Tile Object
~~~~~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :widths: 25 25 50
   :header-rows: 1
   :class: tight-table

   * - FIELD
     - TYPE
     - DESCRIPTION
   * - id
     - Int
     - Tile object id
   * - hp
     - Int
     - Tile obj hp
   * - attack
     - Int
     - Tile obj attack
   * - order
     - Int
     - Tile obj order (from 0 to 6 inclusive)
   * - card
     - Object
     - Card object
   * - state
     - Enum (String)
     - Options: FREE, ASLEEP, ACTIVE, USED
   * - element
     - Enum (String)
     - Options: NEUTRAL, WATER, FIRE, EARTH, ELECTRIC
   * - enchantments
     - List of Objects
     - List of Enchantment objects


Control Object
~~~~~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :widths: 25 25 50
   :header-rows: 1
   :class: tight-table

   * - FIELD
     - TYPE
     - DESCRIPTION
   * - id
     - Int
     - Control object id
   * - hp
     - Int
     - Control obj hp
   * - attack
     - Int
     - Control obj attack
   * - order
     - Int
     - Control obj order
   * - turns
     - Int
     - How many turns left under control
   * - is_infinite
     - bool
     - Is control infinite
   * - card
     - Object
     - Card object
   * - tile
     - Int
     - Tile obj id


CardActiveMystery Object
~~~~~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :widths: 25 25 50
   :header-rows: 1
   :class: tight-table

   * - FIELD
     - TYPE
     - DESCRIPTION
   * - id
     - Int
     - CardActiveMystery object id
   * - order
     - Int
     - CardActiveMystery obj order
   * - card
     - Object
     - CardActiveMystery object

Enchantment Object
~~~~~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :widths: 25 25 50
   :header-rows: 1
   :class: tight-table

   * - FIELD
     - TYPE
     - DESCRIPTION
   * - keyword
     - Enum (String)
     - Enchantment keyword. Options: warcry, censor, leech, insult, pounce, barrier, untouchable, mummy, ensnare, mia, tile_buff
   * - type
     - Enum (String)
     - Enchantment type. Options: buff, debuff
   * - affects_hp
     - bool
     - Is set to True if it directly affects hp
   * - affects_attack
     - bool
     - Is set to True if it directly affects attack
   * - hp_change_value
     - int
     - Is used to modify hp of a Tile or CardHand
   * - attack_change_value
     - int
     - Is used to modify attack of a Tile or CardHand


CardDeck Object
~~~~~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :widths: 25 25 50
   :header-rows: 1
   :class: tight-tab

   * - FIELD
     - TYPE
     - DESCRIPTION
   * - id
     - Int
     - CardDeck object id
   * - card
     - Int
     - Card object id
   * - player
     - Int
     - Player object id