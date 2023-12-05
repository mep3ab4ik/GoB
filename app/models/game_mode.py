from typing import Optional

from django.db import models
from django.db.models import Q
from django.utils import timezone

from app.models.card import Card
from django_app.settings import SKILL_POINTS_ON_LOSS, SKILL_POINTS_ON_VICTORY


class GameMode(models.Model):
    class Meta:
        verbose_name = 'Game Mode'
        verbose_name_plural = 'Game Modes'
        indexes = [
            models.Index(
                fields=['default_game_mode'],
                name='default_game_mode_idx',
            ),
            models.Index(
                fields=['earn_skill_points_in_this_mode'],
                name='earn_skill_points_idx',
            ),
        ]

    custom_id = models.CharField(max_length=16, unique=True)
    title = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=512, unique=True)
    default_game_mode = models.BooleanField(default=True)
    battlefield_timer_duration = models.IntegerField()
    start_battle_player_hp = models.IntegerField(default=30)
    max_cards_in_hand = models.IntegerField(default=10)
    start_cards_on_hand_count = models.IntegerField(default=5)
    max_tiles_per_player = models.IntegerField(default=7)
    max_cards_in_deck = models.IntegerField(default=30)
    earn_skill_points_in_this_mode = models.BooleanField(default=False)
    is_graveyard_enabled = models.BooleanField(default=True)
    show_next_card_from_deck = models.BooleanField(default=False)
    is_random_generated_deck = models.BooleanField(default=False)
    deal_damage_to_avatar_on_empty_deck = models.BooleanField(default=True)
    battle_duration = models.IntegerField(default=3600)

    def __str__(self):
        return self.title

    @property
    def current_season(self):
        return self.seasons.filter(
            Q(starts_at__lte=timezone.now(), ends_at__isnull=True)
            | Q(starts_at__lte=timezone.now(), ends_at__gt=timezone.now())
        ).first()

    @property
    def previous_season(self):
        return self.seasons.filter(ends_at__lt=timezone.now()).order_by('-starts_at').first()


class BlockedCardsInGameMode(models.Model):
    class Meta:
        verbose_name = 'Blocked cards'
        verbose_name_plural = 'Blocked cards'
        unique_together = (('game_mode', 'card'),)

    game_mode = models.ForeignKey(GameMode, on_delete=models.CASCADE, related_name='blocked_cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='blocked_cards')


class GameModeSeason(models.Model):
    class Meta:
        verbose_name = 'Game Mode Season'
        verbose_name_plural = 'Game Mode Season'
        ordering = ('starts_at',)

    game_mode = models.ForeignKey(GameMode, on_delete=models.CASCADE, related_name='seasons')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(blank=True, null=True)
    season_reset_multiplier = models.FloatField(
        verbose_name='season reset multiplier: how much skill points are kept '
        'after season reset (0-1)',
        default=0,
    )

    @property
    def total_time_until_season_end_seconds(self):
        return round((self.ends_at - timezone.now()).total_seconds()) if self.ends_at else 0

    def __str__(self):
        return f'{self.game_mode} season from {self.starts_at} to {self.ends_at}'


class SkillPointsForBattlePlayer(models.Model):
    player = models.ForeignKey(
        'Player', on_delete=models.CASCADE, related_name='skill_points_for_player'
    )
    battle = models.ForeignKey(
        'Battle', on_delete=models.CASCADE, related_name='skill_points_for_battle'
    )
    skill_points = models.FloatField(default=0)


class SkillPointsLadder(models.Model):
    class Meta:
        ordering = ('level',)

    game_mode = models.ForeignKey(
        GameMode, on_delete=models.CASCADE, related_name='game_mode_ladder'
    )
    level = models.IntegerField(default=1)
    skill_points_required = models.IntegerField(default=0)
    xp_reward = models.IntegerField(default=0)


class PlayerSeasonStats(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=['player'],
                name='player_season_stats_player_idx',
            ),
            models.Index(
                fields=['season'],
                name='player_season_stats_season_idx',
            ),
        ]

    season = models.ForeignKey(
        GameModeSeason, on_delete=models.CASCADE, related_name='season_to_player'
    )
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='player_to_season')
    skill_points = models.IntegerField(default=0)
    skill_level = models.IntegerField(default=1)
    xp_earned = models.IntegerField(
        default=0
    )  # this field will be removed once we connect the web api for receiving
    # earned xp from the game
    season_highest = models.IntegerField(default=0)

    @property
    def current_skill_level_object(self) -> Optional[SkillPointsLadder]:
        try:
            return self.season.game_mode.game_mode_ladder.get(level=self.skill_level)
        except (SkillPointsLadder.DoesNotExist, SkillPointsLadder.MultipleObjectsReturned):
            return None

    @property
    def next_skill_level_object(self) -> Optional[SkillPointsLadder]:
        try:
            return self.season.game_mode.game_mode_ladder.get(level=self.skill_level + 1)
        except (SkillPointsLadder.DoesNotExist, SkillPointsLadder.MultipleObjectsReturned):
            return None

    def add_skill_points_on_battle_complete(self, battle, is_winner: bool):
        if SkillPointsForBattlePlayer.objects.filter(battle=battle, player=self.player).exists():
            return
        skill_points_for_player: int
        if is_winner:
            skill_points_for_player = SKILL_POINTS_ON_VICTORY
            self.skill_points += skill_points_for_player
            next_skill_level = self.next_skill_level_object
            if next_skill_level and self.skill_points >= next_skill_level.skill_points_required:
                self.skill_level += 1
                self.xp_earned += (
                    next_skill_level.xp_reward
                )  # change this logic once we receive api from the web team
        else:
            min_skill_points = 0
            current_skill_level = self.current_skill_level_object
            if current_skill_level:
                min_skill_points = current_skill_level.skill_points_required
            skill_points_for_player = (
                SKILL_POINTS_ON_LOSS if self.skill_points > min_skill_points else 0
            )
            self.skill_points += skill_points_for_player
        self.save()

        SkillPointsForBattlePlayer.objects.create(
            battle=battle, player=self.player, skill_points=skill_points_for_player
        )
