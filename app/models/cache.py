from django.db import models


class CachingTime(models.Model):
    player_statistics = models.IntegerField(default=0)
    global_statistics = models.IntegerField(default=0)
