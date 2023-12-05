import io
import json

from django.db import models
from django.utils import timezone


class ClientVersion(models.Model):
    class Meta:
        verbose_name = 'Client Version'
        verbose_name_plural = 'Client Versions'
        ordering = ('-created_at',)
        indexes = [
            models.Index(
                fields=['is_currently_selected'],
                name='is_currently_selected_idx',
            ),
        ]

    created_at = models.DateTimeField(default=timezone.now)
    version = models.CharField(max_length=16, unique=True)
    is_currently_selected = models.BooleanField(
        verbose_name='Is this version selected', default=False
    )

    @property
    def as_file(self):
        json_data = {'current': self.version, 'previous': []}
        return io.BytesIO(bytes(json.dumps(json_data).encode('UTF-8')))
