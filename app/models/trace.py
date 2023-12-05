from django.db import models
from django.db.models import Model
from django.utils import timezone


class Trace(Model):
    class Meta:
        indexes = [
            models.Index(
                fields=['traceback_hash'],
                name='traceback_hash_idx',
            ),
        ]

    error = models.CharField(max_length=2000)
    traceback = models.TextField()
    traceback_hash = models.CharField(max_length=32)
    first_time_triggered = models.DateTimeField(default=timezone.now)
    last_time_triggered = models.DateTimeField(default=timezone.now)
    count_triggered = models.IntegerField(default=0)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.error
