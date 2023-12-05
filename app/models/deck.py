# pylint: disable=import-outside-toplevel
from django.core.exceptions import ValidationError
from django.db import models

from app.enums.card import CardEditions, CardEditionsEnum
from app.models.player import Player


class PreAssembledDeck(models.Model):
    class Meta:
        verbose_name = 'Pre-assembled Deck'
        verbose_name_plural = 'Pre-assembled Decks'
        ordering = ('order',)

    name = models.CharField(max_length=128)
    order = models.IntegerField()
    cards = models.ManyToManyField('Card', through='PreAssembledDeckToCard')

    def __str__(self):
        return self.name


class PreAssembledDeckToCard(models.Model):
    class Meta:
        ordering = ('order',)

    pre_assembled_deck = models.ForeignKey(
        PreAssembledDeck,
        on_delete=models.CASCADE,
        related_name='pre_assembled_deck_to_card',
    )
    card = models.ForeignKey(
        'Card', on_delete=models.CASCADE, related_name='card_to_pre_assembled_deck'
    )
    involved_in_auto_gathering = models.BooleanField(
        default=True,
        help_text='Card involved in auto generate custom deck to fresh user',
    )
    order = models.IntegerField(default=0)


class CustomDeck(models.Model):
    class Meta:
        ordering = ('order',)
        indexes = [
            models.Index(
                fields=['player'],
                name='custom_deck_player_idx',
            ),
        ]

    name = models.CharField(max_length=128)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='custom_decks')
    order = models.IntegerField(default=0)
    is_selected = models.BooleanField(default=False)
    cards = models.ManyToManyField('Card', through='CustomDeckToCard')
    player_cards = models.ManyToManyField('PlayerCard', through='CustomDeckToCard')
    is_generated = models.BooleanField(default=False)

    def clean(self):
        if not self.pk and self.player.custom_decks.filter(is_generated=False).count() >= 5:
            raise ValidationError('You cannot create more than 5 decks!')

    def save(self, *args, **kwargs):
        if not self.id:
            last_order = (
                self.player.custom_decks.last().order  # pylint: disable=no-member
                if self.player.custom_decks.exists()
                else 0
            )
            self.order = last_order + 1
        super().save(*args, **kwargs)

    @property
    def all_cards_coded(self):
        return all(card.is_enabled for card in self.cards.all())


def default_player_card_in_custom_deck_to_card(obj):
    from app.models.player import PlayerCard

    return PlayerCard.objects.filter(player=obj.deck.player, card=obj.card).first()


class CustomDeckToCard(models.Model):
    class Meta:
        ordering = ('order',)
        indexes = [
            models.Index(
                fields=['player_card'],
                name='custom_deck_to_card_idx',
            ),
            models.Index(
                fields=['deck'],
                name='custom_deck_to_card_deck_idx',
            ),
        ]

    deck = models.ForeignKey(
        CustomDeck, on_delete=models.CASCADE, related_name='custom_deck_to_card'
    )
    card = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='card_to_custom_deck')
    player_card = models.ForeignKey(
        'PlayerCard',
        on_delete=models.CASCADE,
        related_name='player_card_to_custom_deck',
        blank=True,
        null=True,
    )
    order = models.IntegerField(null=True)
    is_played = models.BooleanField(default=False)
    edition = models.CharField(CardEditions, max_length=50, default=CardEditionsEnum.regular)
