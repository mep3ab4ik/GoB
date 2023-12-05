from django.db import models
from django.utils import timezone

from .player import Player


class PlayerSession(models.Model):
    class Meta:
        ordering = ('-session_start',)

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_sessions')
    session_start = models.DateTimeField(default=timezone.now)
    session_end = models.DateTimeField(blank=True, null=True)

    @property
    def is_active_session(self):
        return not self.session_end


class ActivePlayersOverTime(models.Model):
    class Meta:
        ordering = ('-created_at',)

    created_at = models.DateTimeField(default=timezone.now)
    players_online = models.IntegerField(default=0)
    players_in_battle = models.IntegerField(default=0)
