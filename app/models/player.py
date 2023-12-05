# pylint: disable=import-outside-toplevel
import datetime
import logging
import time
from typing import Union

from django.core.cache import cache
from django.db import models
from django.utils import timezone

from app.enums.card import CardEditions
from app.utils.user import generate_random_player_id

from .card import Card
from .game_mode import GameMode, GameModeSeason, PlayerSeasonStats
from .user import User

logger = logging.getLogger()


class WhitelistWallet(models.Model):
    wallet = models.CharField(max_length=1024)


class PlayerStatus(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=64)


class Player(models.Model):  # pylint: disable=too-many-public-methods
    """Player is a base model for all players and has a one to one relationship with User model."""

    class Meta:
        indexes = [
            models.Index(
                fields=['user'],
                name='player_user_idx',
            ),
            models.Index(
                fields=['is_gitex_bull'],
                name='player_is_gitex_bull_idx',
            ),
            models.Index(
                fields=['is_gitex_bear'],
                name='player_is_gitex_bear_idx',
            ),
        ]

    player_id = models.CharField(default=generate_random_player_id, max_length=16, unique=True)
    avatar = models.PositiveIntegerField(blank=True, null=True, default=0)  #: Player avatar id
    body = models.PositiveIntegerField(blank=True, null=True, default=0)  #: Player body id
    status = models.ForeignKey(PlayerStatus, on_delete=models.SET_NULL, null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)  #: Player last activity date
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='player'
    )  #: Player user object
    # player_friends
    # main api fields
    num_avatars_owned = models.IntegerField(default=0)
    num_bods_owned = models.IntegerField(default=0)
    num_cards_owned = models.IntegerField(default=0)
    pfp_avatar_image_url = models.CharField(max_length=512, blank=True, null=True)

    current_trophy_count = models.PositiveIntegerField(default=0)
    previous_season_trophy_count = models.PositiveIntegerField(default=0)
    highest_trophy_count = models.PositiveIntegerField(default=0)
    current_arena_name = models.CharField(max_length=512, default='', blank=True, null=True)
    current_experience = models.PositiveIntegerField(default=100)
    current_level = models.PositiveIntegerField(default=1)
    add_all_nft_cards = models.BooleanField(default=False)

    # GITEX event fields
    is_gitex_bull = models.BooleanField(default=False)
    is_gitex_bear = models.BooleanField(default=False)

    @property
    def username(self) -> str:
        return self.user.username

    @property
    def is_whitelist_user(self):
        return WhitelistWallet.objects.filter(wallet__iexact=self.user.metamask_token).exists()

    def update_last_activity(self):
        cache.set(f'last_activity-{self.player_id}', timezone.now(), 62)

    @property
    def days_offline(self):
        days_offline = timezone.now() - self.user.last_login
        return days_offline.days

    @property
    def count_all_player_nft_cards(self):
        return self.player_cards.filter(card__nft_card_type='nft').count()

    @property
    def count_all_player_non_nft_cards(self):
        return self.player_cards.filter(card__nft_card_type='non_nft').count()

    @property
    def total_duration_user_spent_in_game(self):
        all_time = None
        for player_activity in self.player_activity_duration.all():
            if isinstance(all_time, datetime.timedelta):
                all_time += player_activity.end_activity - player_activity.start_activity
            else:
                all_time = player_activity.end_activity - player_activity.start_activity
        return all_time

    @property
    def humanized_total_duration_user_spent_in_game(self):
        all_time = self.total_duration_user_spent_in_game
        formatted_time = time.strftime('%H:%M', time.gmtime(all_time.total_seconds()))

        if not all_time or not all_time.days:
            return f'{formatted_time}' if all_time else '00:00'

        days_in_month = all_time.days % 30
        months = all_time.days // 30
        return f'{months}:{days_in_month} {formatted_time}'

    @property
    def get_median_total_duration_user_spent_in_game(self):
        time_list = [
            player.end_activity - player.start_activity
            for player in self.player_activity_duration.all()
        ]
        average_timedelta = (
            sum(time_list, datetime.timedelta(0)) / len(time_list) if time_list else None
        )
        return (
            f"{time.strftime('%H:%M', time.gmtime(average_timedelta.total_seconds()))}"
            if average_timedelta
            else '00:00'
        )

    def season_stats(self, season: Union[GameModeSeason, None]):
        out = {
            'skill_points': 0,
            'skill_level': 1,
            'season_highest': 0,
            'time_until_season_end_seconds': 0,
        }
        if not season:
            return out
        out['time_until_season_end_seconds'] = season.total_time_until_season_end_seconds
        player_season = self.player_to_season.filter(season=season).first()
        if not player_season:
            return out
        out['skill_points'] = player_season.skill_points
        out['skill_level'] = player_season.skill_level
        out['season_highest'] = player_season.season_highest
        return out

    @property
    def current_ladder_season_stats(self):
        game_mode: GameMode = GameMode.objects.filter(
            default_game_mode=True, earn_skill_points_in_this_mode=True
        ).first()
        if not game_mode:
            return self.season_stats(None)
        return self.season_stats(game_mode.current_season)

    @property
    def previous_ladder_season_stats(self):
        game_mode: GameMode = GameMode.objects.filter(
            default_game_mode=True, earn_skill_points_in_this_mode=True
        ).first()
        if not game_mode:
            return self.season_stats(None)
        return self.season_stats(game_mode.previous_season)

    @property
    def best_ladder_season_stats(self):
        game_mode: GameMode = GameMode.objects.filter(
            default_game_mode=True, earn_skill_points_in_this_mode=True
        ).first()
        if not game_mode:
            return self.season_stats(None)
        best_season = (
            PlayerSeasonStats.objects.filter(season__game_mode=game_mode, player=self)
            .order_by('-skill_points')
            .first()
        )
        return self.season_stats(best_season.season)

    @property
    def total_player_cards(self):
        return self.player_cards.exclude(card__custom_id__startswith='DD').count()

    @property
    def battle_statistics(self):
        from app.utils.statistics import update_player_statistics  # noqa: I252

        user_id = self.user.id
        statistics_data = cache.get(f'user_statistics_{user_id}')

        if statistics_data:
            return statistics_data

        return update_player_statistics(user_id=user_id)

    def battle_stats_for_season(self, season_id: int):
        from app.utils.statistics import update_player_statistics

        user_id = self.user.id
        statistics_data = cache.get(f'user_statistics_{user_id}_season_{season_id}')

        if statistics_data:
            return statistics_data

        season = GameModeSeason.objects.get(id=season_id)
        return update_player_statistics(user_id=user_id, season=season)


class Friendship(models.Model):
    """Friendship signature"""

    class Meta:
        unique_together = (('friend', 'player'),)
        indexes = [
            models.Index(
                fields=['friend'],
                name='friendship_friend_idx',
            ),
            models.Index(
                fields=['player'],
                name='friendship_player_idx',
            ),
            models.Index(
                fields=['is_accepted'],
                name='friendship_is_accepted_idx',
            ),
            models.Index(
                fields=['sender'],
                name='friendship_sender_idx',
            ),
        ]

    friend = models.ForeignKey(Player, models.CASCADE, related_name='friends')
    player = models.ForeignKey(Player, models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    sender = models.ForeignKey(Player, models.CASCADE, related_name='sender_friends')

    def __str__(self):
        return f'{self.player.id}-{self.is_accepted}'


class PlayerCard(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=['player'],
                name='player_card_player_idx',
            ),
            models.Index(
                fields=['card'],
                name='player_card_card_idx',
            ),
            models.Index(
                fields=['edition'],
                name='friendship_edition_idx',
            ),
        ]

    card = models.ForeignKey(Card, models.CASCADE)
    quantity = models.IntegerField(default=1)
    edition = models.CharField(CardEditions, max_length=50)
    player = models.ForeignKey(Player, models.CASCADE, related_name='player_cards')


class PlayerActivity(models.Model):
    player = models.ForeignKey(Player, models.CASCADE, related_name='player_activity_duration')
    start_activity = models.DateTimeField()
    end_activity = models.DateTimeField()
