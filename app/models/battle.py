# pylint: disable=too-many-lines
from dataclasses import dataclass
from typing import Optional
from uuid import uuid1, uuid4

from django.db import models
from django.utils import timezone
from djongo import models as mongo_models

from app.card_abilities.enums import CardPlaces
from app.enums.card import SpellTargetingTypesEnum, SpellTypesEnum

from .card import Card
from .player import Player


def generate_random_id():
    return str(uuid1()) + str(uuid4())


class Battle(models.Model):
    class Meta:
        verbose_name = 'Battle'
        verbose_name_plural = 'Battles'
        ordering = ('-created_at',)
        indexes = [
            models.Index(
                fields=['state'],
                name='battle_state_idx',
            ),
            models.Index(
                fields=['game_mode'],
                name='battle_game_mode_idx',
            ),
            models.Index(
                fields=['battle_end'],
                name='battle_battle_end_idx',
            ),
            models.Index(
                fields=['winner'],
                name='battle_winner_idx',
            ),
            models.Index(
                fields=['room_id'],
                name='battle_room_id_idx',
            ),
        ]

    class States(models.TextChoices):
        CREATED = 'CREATED', 'created'  # when battle is created
        JOINED = 'JOINED', 'joined'  # when first player joins
        CLOSED = 'CLOSED', 'closed'  # when second player is allocated
        ACTIVE = 'ACTIVE', 'active'  # when second player joins
        COMPLETED = 'COMPLETED', 'completed'  # when battle is over
        DISCARDED = (
            'DISCARDED',
            'discarded',
        )  # when battle is discarded because player didn't wait for his opponent,
        # or battle not completed (no auto resolution)
        AWAITING_RECONNECT = (
            'AWAITING_RECONNECT',
            'awaiting_reconnect',
        )  # one of the two players disconnected and
        # we're giving him time to reconnect

        @classmethod
        def active_states(cls) -> tuple:
            return cls.ACTIVE, cls.AWAITING_RECONNECT, cls.JOINED

    class FirstTurnIdx(models.IntegerChoices):
        ONE = 1
        TWO = 2

    room_id = models.CharField(max_length=40)
    player_1_ticket = models.CharField(max_length=40, unique=True, blank=True, null=True)
    player_2_ticket = models.CharField(max_length=40, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    battle_start = models.DateTimeField(blank=True, null=True)
    battle_end = models.DateTimeField(blank=True, null=True)
    winner = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='battle_wins',
    )
    battle_end_type = models.CharField(
        max_length=32,
        choices=(
            ('player_killed', 'player_killed'),
            ('player_disconnected', 'player_disconnected'),
        ),
        blank=True,
        null=True,
    )
    state = models.CharField(max_length=32, choices=States.choices, default=States.CREATED)
    turn = models.IntegerField(blank=True, null=True)
    turn_number = models.IntegerField(
        default=1, verbose_name='Battle turn number'
    )  # updated after both players complete a turn
    first_turn_idx = models.IntegerField(choices=FirstTurnIdx.choices, default=FirstTurnIdx.ONE)
    game_mode = models.ForeignKey('GameMode', on_delete=models.CASCADE, blank=True, null=True)
    game_mode_season = models.ForeignKey(
        'GameModeSeason', on_delete=models.CASCADE, blank=True, null=True
    )
    current_turn_player = models.OneToOneField(
        'BattlePlayer',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='current_battle',
    )

    def complete(self, winner: Optional[Player]) -> None:
        self.state = Battle.States.COMPLETED
        self.winner = winner
        self.battle_end = timezone.now()
        self.save()


class CardRelation(models.Model):
    class Meta:
        abstract = True
        ordering = ('order',)

    hp = models.IntegerField(default=0)
    attack = models.IntegerField(default=0)
    order = models.IntegerField()
    clear_description = models.BooleanField(default=False)
    remove_mummy = models.BooleanField(default=False)
    remove_last_breath = models.BooleanField(default=False)
    battle_card_id = models.IntegerField(null=True, blank=True)  # this value is unique

    @property
    def player(self):
        raise NotImplementedError

    @property
    def card(self):
        raise NotImplementedError


class CardDeck(CardRelation):
    class Meta:
        indexes = [
            models.Index(
                fields=['player'],
                name='card_deck_player_idx',
            ),
            models.Index(
                fields=['card'],
                name='card_deck_card_idx',
            ),
        ]
        ordering = ('order',)

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name=CardPlaces.deck)
    player = models.ForeignKey(
        'BattlePlayer', on_delete=models.CASCADE, related_name=CardPlaces.deck
    )


class CardHand(CardRelation):
    class Meta:
        indexes = [
            models.Index(
                fields=['player'],
                name='card_hand_player_idx',
            ),
            models.Index(
                fields=['card'],
                name='card_hand_card_idx',
            ),
        ]
        ordering = ('order',)

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name=CardPlaces.hand)
    player = models.ForeignKey(
        'BattlePlayer', on_delete=models.CASCADE, related_name=CardPlaces.hand
    )
    card_death_count = models.IntegerField(default=0)

    @property
    def get_attack_with_enchantments(self):
        base_attack = self.attack
        for enchantment in self.enchantments.filter(affects_attack=True):
            base_attack += enchantment.attack_change_value
        return base_attack

    @property
    def get_hp_with_enchantments(self):
        base_hp = self.hp
        for enchantment in self.enchantments.filter(affects_hp=True):
            base_hp += enchantment.hp_change_value
        return base_hp

    def check_if_target_tile_is_valid(self, target_tile) -> bool:
        target_tile_type = 'friendly' if target_tile.player == self.player else 'opponent'
        target_types_dict = {
            SpellTargetingTypesEnum.only_opponent_tiles: ['opponent'],
            SpellTargetingTypesEnum.only_opponent_creatures: ['opponent'],
            SpellTargetingTypesEnum.only_opponent_everything: ['opponent'],
            SpellTargetingTypesEnum.only_player_tiles: ['friendly'],
            SpellTargetingTypesEnum.only_player_creatures: ['friendly'],
            SpellTargetingTypesEnum.only_player_everything: ['friendly'],
            SpellTargetingTypesEnum.both_player_tiles: ['friendly', 'opponent'],
            SpellTargetingTypesEnum.both_player_creatures: ['friendly', 'opponent'],
            SpellTargetingTypesEnum.both_player_everything: ['friendly', 'opponent'],
        }
        if (
            self.card
            and self.card.targeting == SpellTypesEnum.target
            and self.card.targeting_type in target_types_dict
            and target_tile_type not in target_types_dict[self.card.targeting_type]
        ):
            return False
        return True


class CardGraveyard(CardRelation):
    class Meta:
        indexes = [
            models.Index(
                fields=['player'],
                name='card_graveyard_player_idx',
            ),
            models.Index(
                fields=['card'],
                name='card_graveyard_card_idx',
            ),
        ]
        ordering = ('order',)

    player = models.ForeignKey(
        'BattlePlayer', on_delete=models.CASCADE, related_name=CardPlaces.graveyard
    )
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name=CardPlaces.graveyard)


class CardActiveMystery(CardRelation):
    class Meta:
        indexes = [
            models.Index(
                fields=['player'],
                name='card_mystery_player_idx',
            ),
            models.Index(
                fields=['card'],
                name='card_mystery_card_idx',
            ),
        ]
        ordering = ('order',)

    player = models.ForeignKey(
        'BattlePlayer', on_delete=models.CASCADE, related_name=CardPlaces.active_mystery
    )
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name=CardPlaces.active_mystery)


class TileQuerySet(models.QuerySet):
    def non_free(self):
        return self.exclude(state=Tile.States.FREE)

    def exclude_mia(self):
        return self.exclude(enchantments__keyword=EnchantmentKeywordsEnum.mia)

    def exclude_censor(self):
        return self.exclude(enchantments__keyword=EnchantmentKeywordsEnum.censor)


class TileManager(models.Manager):
    def get_queryset(self) -> TileQuerySet:
        return TileQuerySet(self.model, using=self._db)

    def non_free(self):
        return self.get_queryset().non_free()

    def exclude_mia(self):
        return self.get_queryset().exclude_mia()

    def exclude_censor(self):
        return self.get_queryset().exclude_censor()


class Tile(CardRelation):
    class Meta:
        indexes = [
            models.Index(
                fields=['player'],
                name='tile_player_idx',
            ),
            models.Index(
                fields=['card'],
                name='tile_card_idx',
            ),
            models.Index(
                fields=['element'],
                name='tile_element_idx',
            ),
            models.Index(
                fields=['state'],
                name='tile_state_idx',
            ),
        ]
        ordering = ('order',)

    class States(models.TextChoices):
        FREE = 'FREE', 'free'
        ASLEEP = 'ASLEEP', 'asleep'
        ACTIVE = 'ACTIVE', 'active'
        USED = 'USED', 'used'
        LOCKED = 'LOCKED', 'locked'

    class Elements(models.TextChoices):
        NEUTRAL = 'NEUTRAL', 'neutral'
        WATER = 'WATER', 'water'
        FIRE = 'FIRE', 'fire'
        EARTH = 'EARTH', 'earth'
        ELECTRIC = 'ELECTRIC', 'electric'

    element = models.CharField(max_length=32, default=Elements.NEUTRAL)
    state = models.TextField(choices=States.choices, default=States.FREE)
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name=CardPlaces.tile,
    )
    player = models.ForeignKey(
        'BattlePlayer', on_delete=models.CASCADE, related_name=CardPlaces.tile
    )
    card_death_count = models.IntegerField(default=0)

    # original_card is necessary for correct warcry
    # trigger processing on cards that become a copy of another card
    original_card = models.ForeignKey(
        Card, on_delete=models.CASCADE, null=True, blank=True, related_name='card_to_tile_original'
    )
    objects = TileManager()

    @property
    def get_attack_with_enchantments(self):
        # get sum of all buffs/debuffs for attack value
        attack_difference = (
            self.enchantments.filter(affects_attack=True).aggregate(
                attack_change=models.Sum('attack_change_value')
            )['attack_change']
            or 0
        )
        return max(0, self.attack + attack_difference)  # max ensures that value is positive

    @property
    def get_hp_with_enchantments(self):
        base_hp = self.hp
        for enchantment in self.enchantments.filter(affects_hp=True):
            base_hp += enchantment.hp_change_value
        return base_hp

    def flush(self):
        self.card = None
        self.battle_card_id = None
        self.state = Tile.States.FREE
        self.hp = 0
        self.attack = 0
        self.card_death_count = 0
        self.enchantments.all().delete()
        self.save()


class Control(CardRelation):
    class Meta:
        indexes = [
            models.Index(
                fields=['tile'],
                name='control_tile_idx',
            ),
        ]
        ordering = ('order',)

    turns = models.PositiveIntegerField(default=0)
    is_infinite = models.BooleanField(default=False)
    card = models.ForeignKey(Card, models.CASCADE, related_name=CardPlaces.control)
    tile = models.ForeignKey(Tile, models.CASCADE, related_name=CardPlaces.control)
    player = models.ForeignKey('BattlePlayer', models.CASCADE, related_name=CardPlaces.control)


class BattlePlayer(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=['battle'],
                name='battle_player_battle_idx',
            ),
            models.Index(
                fields=['player'],
                name='battle_player_idx',
            ),
            models.Index(
                fields=['player_id'],
                name='battle_player_id_idx',
            ),
        ]

    class PlayerId(models.IntegerChoices):
        ONE = 1
        TWO = 2

    idx = models.IntegerField(choices=PlayerId.choices)
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='players')
    hp = models.IntegerField(default=30)
    hp_limit = models.IntegerField(default=30)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='battle_players')
    deck: CardDeck.objects
    hand: CardHand.objects
    graveyard: CardGraveyard.objects
    tile: Tile.objects
    control: Control.objects
    active_mystery: CardActiveMystery.objects

    def __str__(self):
        return f'BattlePlayer {self.id}'


class EventHistory(models.Model):
    class Meta:
        verbose_name = 'Event History'
        verbose_name_plural = 'Event Histories'
        ordering = ('-created_at',)

    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='event_history')
    created_at = models.DateTimeField(default=timezone.now)
    event_source = models.CharField(
        max_length=16,
        db_index=True,
        choices=(
            ('player1', 'player1'),
            ('player2', 'player2'),
            ('server', 'server'),
        ),
    )
    event_destination = models.CharField(
        max_length=16,
        db_index=True,
        choices=(
            ('player1', 'player1'),
            ('player2', 'player2'),
            ('both', 'both'),
            ('none', 'none'),
        ),
    )
    event_type = models.CharField(
        max_length=32,
        db_index=True,
        choices=(
            ('select_deck', 'select_deck'),
            ('player_connected', 'player_connected'),
            ('battle_start', 'battle_start'),
            ('draw_cards', 'draw_cards'),
            ('start_turn', 'start_turn'),
            ('play_card', 'play_card'),
            ('minion_attack', 'minion_attack'),
            ('minion_damage', 'minion_damage'),
            ('player_attack', 'player_attack'),
            ('player_damage', 'player_damage'),
            ('player_destroy', 'player_destroy'),
            ('end_turn', 'end_turn'),
            ('end_battle', 'end_battle'),
            ('opponent_disconnected', 'opponent_disconnected'),
            ('battle_state_change', 'battle_state_change'),
        ),
    )
    event_raw_message = models.TextField()


@dataclass
class EnchantmentKeywordsEnum:
    warcry = 'warcry'
    censor = 'censor'
    leech = 'leech'
    insult = 'insult'
    pounce = 'pounce'
    barrier = 'barrier'
    untouchable = 'untouchable'
    mummy = 'mummy'
    ensnare = 'ensnare'
    mia = 'mia'
    tile_buff = 'tile_buff'
    protect = 'protect'
    invisible = 'invisible'


@dataclass
class EnchantmentTypeEnum:
    buff = 'buff'
    debuff = 'debuff'


class Enchantment(models.Model):
    """Enchantment represents buffs and de-buffs on card object"""

    class Meta:
        indexes = [
            models.Index(
                fields=['keyword'],
                name='enchantment_keyword_idx',
            ),
            models.Index(
                fields=['tile'],
                name='enchantment_tile_idx',
            ),
            models.Index(
                fields=['turns'],
                name='enchantment_turns_idx',
            ),
            models.Index(
                fields=['player'],
                name='enchantment_player_idx',
            ),
            models.Index(
                fields=['affects_attack'],
                name='enchantment_affects_attack_idx',
            ),
            models.Index(
                fields=['type'],
                name='enchantment_type_idx',
            ),
            models.Index(
                fields=['attack_change_value'],
                name='enchantment_attack_change_idx',
            ),
        ]

    KEYWORDS = (
        (EnchantmentKeywordsEnum.warcry, 'Warcry'),
        (EnchantmentKeywordsEnum.censor, 'Censor'),
        (EnchantmentKeywordsEnum.leech, 'Leech'),
        (EnchantmentKeywordsEnum.insult, 'Insult'),
        (EnchantmentKeywordsEnum.pounce, 'Pounce'),
        (EnchantmentKeywordsEnum.barrier, 'Barrier'),
        (EnchantmentKeywordsEnum.untouchable, 'Untouchable'),
        (EnchantmentKeywordsEnum.mummy, 'Mummy'),
        (EnchantmentKeywordsEnum.ensnare, 'Ensnare'),
        (EnchantmentKeywordsEnum.mia, 'MIA'),
        (EnchantmentKeywordsEnum.tile_buff, 'Tile Buff'),
        (EnchantmentKeywordsEnum.protect, 'Protect'),
        (EnchantmentKeywordsEnum.invisible, 'Invisible'),
    )

    TYPES = ((EnchantmentTypeEnum.buff, 'buff'), (EnchantmentTypeEnum.debuff, 'debuff'))

    #: How many turns enchantments will be on card, if empty - infinite
    turns = models.PositiveIntegerField(blank=True, null=True)
    #: Hand card to affect it
    card_hand = models.ForeignKey(
        CardHand, models.CASCADE, blank=True, null=True, related_name='enchantments'
    )
    #: Tile card to affect it
    tile = models.ForeignKey(
        Tile, models.CASCADE, blank=True, null=True, related_name='enchantments'
    )
    player = models.ForeignKey(
        BattlePlayer, models.CASCADE, blank=True, null=True, related_name='enchantments'
    )
    #: Enchantment keyword
    keyword = models.CharField(
        max_length=100, choices=KEYWORDS, default=EnchantmentKeywordsEnum.warcry
    )
    #: type is either buff or debuff
    type = models.CharField(max_length=16, choices=TYPES, default='buff')
    #: affects_hp is set to True if it directly affects hp
    affects_hp = models.BooleanField(default=False)
    #: affects_attack is set to True if it directly affects attack
    affects_attack = models.BooleanField(default=False)
    #: hp_change_value is used to modify hp of a Tile or CardHand
    hp_change_value = models.IntegerField(blank=True, null=True)
    #: attack_change_value is used to modify attack of Tile or CardHand
    attack_change_value = models.IntegerField(blank=True, null=True)
    #: How much damage get card, if empty - usual
    protect = models.PositiveIntegerField(blank=True, null=True)


class BattleLog(models.Model):
    class Meta:
        ordering = ('timestamp',)
        verbose_name = 'Battle Log'
        verbose_name_plural = 'Battle Logs'

    battle = models.ForeignKey(Battle, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    battle_player = models.ForeignKey(BattlePlayer, on_delete=models.CASCADE)
    event_type = models.CharField(
        choices=(('client_event', 'client_event'), ('server_event', 'server_event')),
        default='client_event',
        max_length=32,
    )
    event_json = models.JSONField()


class BattleLogMongo(mongo_models.Model):
    class Meta:
        in_db = 'nonrel'
        ordering = ('timestamp',)
        managed = False
        verbose_name = 'Battle Log'
        verbose_name_plural = 'Battle Logs'

    id = mongo_models.CharField(
        max_length=64,
        primary_key=True,
        editable=False,
        verbose_name='ID',
        default=generate_random_id,
    )
    timestamp = mongo_models.DateTimeField(default=timezone.now)
    battle_id = mongo_models.TextField(db_index=True)
    battle_player_id = mongo_models.TextField(db_index=True)
    event_type = mongo_models.CharField(
        choices=(('client_event', 'client_event'), ('server_event', 'server_event')),
        default='client_event',
        max_length=32,
    )
    event_json = mongo_models.JSONField()
