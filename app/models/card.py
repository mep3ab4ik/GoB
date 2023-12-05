# pylint: disable=import-outside-toplevel
import uuid

import mimesis
from django.db import models
from django.utils import timezone

from app.enums.card import CardElements, CardRarities, CardTypes, SpellTargetingTypes, SpellTypes
from app.exceptions import CardAbilityNotFound
from app.utils.paths import (
    get_card_image_path,
    get_card_regular_image_frame_path,
    get_card_shiny_image_frame_path,
)
from bootstrap.utils import BootstrapGeneric, BootstrapMixin

from .minion import Minion


def get_card_default_custom_id(instance):
    return str(instance.id)


def get_first(tpl):
    return tpl[0][0]


SCRIPT_WRAPPER_HELP = (
    '<span style="color: crimson">To script map actions, you need to '
    'write a sequence of actions with code using entities that '
    'will be passed when the script is called to the global state </span><br><br>'
    '<span style="color: darkgreen">Base entity: </span><br><br>'
    'Player (Action initiator) <br>'
    'Enemy (Opponent)<br><br>'
    '<span style="color: darkgreen">Base childhood: </span><br><br>'
    'Deck <br>'
    'Hand <br>'
    'Tiles <br><br>'
    '<span style="color: darkgreen">Deck, Hand, Tiles childhood: </span><br><br>'
    'Card'
)


class Card(models.Model, BootstrapMixin):
    """
    Card model is responsible for storing all information about a specific card in the db
    """

    class Meta:
        indexes = [
            models.Index(
                fields=['targeting_type'],
                name='card_targeting_type_idx',
            ),
            models.Index(
                fields=['is_enabled'],
                name='card_is_enabled_idx',
            ),
        ]

    custom_id = models.CharField(max_length=64, verbose_name='ID', unique=True, default='0')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    by_artist = models.CharField(max_length=64, blank=True, null=True)
    rarity = models.CharField(max_length=32, choices=CardRarities, default=get_first(CardRarities))
    approval = models.CharField(
        max_length=32,
        choices=(
            ('in_progress', 'In-progress'),
            ('not_approved', 'Not approved'),
            ('completed', 'Completed'),
        ),
        default='in_progress',
    )
    description = models.TextField(max_length=512, blank=True, null=True)
    hp = models.IntegerField(default=0)
    type = models.CharField(max_length=32, choices=CardTypes, default=get_first(CardTypes))
    targeting = models.CharField(max_length=64, choices=SpellTypes, blank=True, null=True)
    targeting_type = models.CharField(
        max_length=64, choices=SpellTargetingTypes, blank=True, null=True
    )
    attack = models.IntegerField(default=0)
    element = models.CharField(max_length=32, choices=CardElements, default=get_first(CardElements))
    nft_card_type = models.CharField(
        max_length=32,
        choices=(
            ('non_nft', 'Non-NFT'),
            ('nft', 'NFT'),
        ),
        default='non_nft',
    )
    original_illustration = models.ImageField(upload_to=get_card_image_path, blank=True, null=True)
    regular_edition_illustration = models.ImageField(
        upload_to=get_card_regular_image_frame_path, blank=True, null=True
    )
    shiny_edition_illustration = models.ImageField(
        upload_to=get_card_shiny_image_frame_path, blank=True, null=True
    )
    card_series = models.ManyToManyField('CardSeries', blank=True)
    subtypes = models.ManyToManyField('CardSubtype', blank=True)
    script_on_appear = models.TextField(blank=True, help_text=SCRIPT_WRAPPER_HELP)
    script_on_disappear = models.TextField(blank=True, help_text=SCRIPT_WRAPPER_HELP)
    script_on_period = models.TextField(blank=True, help_text=SCRIPT_WRAPPER_HELP)
    script_on_trigger = models.TextField(blank=True, help_text=SCRIPT_WRAPPER_HELP)
    is_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.custom_id

    class Bootstrap(BootstrapGeneric):
        name = mimesis.Text().word

    def save(self, *args, **kwargs):
        if not self.is_enabled:
            return super().save(*args, **kwargs)

        from app.card_abilities.card_utils import get_class_card

        try:
            get_class_card(self.custom_id)
        except CardAbilityNotFound:
            self.is_enabled = False

        return super().save(*args, **kwargs)


class CardAction(models.Model, BootstrapMixin):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='card_actions')
    action_type = models.CharField(
        max_length=16,
        choices=(
            ('spawn_minion', 'spawn_minion'),
            ('spell', 'spell'),
        ),
        default='spawn_minion',
    )
    order = models.IntegerField()
    minion = models.ForeignKey(Minion, on_delete=models.CASCADE, blank=True, null=True)
    spell_name = models.CharField(max_length=64, blank=True, null=True)


class CardSeries(models.Model, BootstrapMixin):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class CardSubtype(models.Model, BootstrapMixin):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class CardRelationShip(models.Model, BootstrapMixin):
    card_type = models.CharField(max_length=32, choices=CardTypes, default=get_first(CardTypes))
    cards_exclude = models.ManyToManyField(
        Card, help_text='Exclude specific cards from type relationship'
    )
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='card_relationship')

    def __str__(self):
        return self.card_type

    class Meta:
        verbose_name = 'Card relationship'
        verbose_name_plural = 'Cards relationships'


class CardHistory(models.Model):
    class Meta:
        verbose_name = 'Card History'
        verbose_name_plural = 'Cards History'
        ordering = ('-created_at',)

    class RecordTypes(models.TextChoices):
        PLACED_ON_TILE = 'PLACED_ON_TILE', 'PLACED_ON_TILE'
        ATTACK = 'ATTACK', 'ATTACK'
        MYSTERY_ACTIVATED = 'MYSTERY_ACTIVATED', 'MYSTERY_ACTIVATED'
        SPELL_PLAYED = 'SPELL_PLAYED', 'SPELL_PLAYED'
        DEATH = 'DEATH', 'DEATH'

    created_at = models.DateTimeField(default=timezone.now)
    battle_player = models.ForeignKey(
        'BattlePlayer', on_delete=models.CASCADE, related_name='cards_history'
    )
    battle = models.ForeignKey(
        'Battle', on_delete=models.CASCADE, related_name='battle_cards_history'
    )
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    turn_number = models.IntegerField(default=0)
    record_type = models.CharField(
        max_length=32, choices=RecordTypes.choices, default=RecordTypes.PLACED_ON_TILE
    )
