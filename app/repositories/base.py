import random
from typing import Optional, Union

from django.db import models


class BaseRepository:
    DB_MODEL: models.Model

    @classmethod
    def create(cls, **kwargs):
        return cls.DB_MODEL.objects.create(**kwargs)

    @classmethod
    def update(cls, db_instance, **kwargs):
        for key, value in kwargs.items():
            setattr(db_instance, key, value)

    @classmethod
    def save(cls, db_instance):
        db_instance.save()

    @classmethod
    def get_last_order(cls, battle_player):
        last_card = cls.DB_MODEL.objects.filter(player=battle_player).last()
        return last_card.order if last_card else 0

    @staticmethod
    def random_objects(subsequence: Union[list, set], count_objects: int = 1) -> Optional[list]:
        len_subsequence = len(subsequence)
        if len_subsequence > 0:
            return random.sample(subsequence, min(count_objects, len_subsequence))
        return None
