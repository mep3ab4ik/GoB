from django.db import models


class Arena(models.Model):
    class Meta:
        verbose_name = 'Arena'
        verbose_name_plural = 'Arenas'
        ordering = ('required_trophies', 'name')

    name = models.CharField(max_length=64, unique=True)
    required_trophies = models.IntegerField()

    def __str__(self):
        return self.name
