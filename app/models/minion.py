import uuid

from django.db import models

from app.utils.paths import get_minion_image_path
from bootstrap.utils import BootstrapMixin


class Minion(models.Model, BootstrapMixin):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=128, unique=True)
    attack = models.IntegerField()
    health = models.IntegerField()
    minion_image = models.FileField(upload_to=get_minion_image_path)

    def __str__(self):
        return self.name
