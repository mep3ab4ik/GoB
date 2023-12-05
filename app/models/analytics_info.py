from uuid import uuid4

from djongo import models as mongo_models


def generate_uuid():
    return str(uuid4())


class AnalyticsInfo(mongo_models.Model):
    class Meta:
        in_db = 'nonrel'
        ordering = ('-created_at',)
        managed = False

    id = mongo_models.CharField(
        max_length=36,
        primary_key=True,
        editable=False,
        verbose_name='ID',
        default=generate_uuid,
    )
    user_id = mongo_models.IntegerField()
    created_at = mongo_models.DateTimeField(auto_now_add=True)
    event_name = mongo_models.CharField(
        max_length=120,
    )
    event_json = mongo_models.JSONField()
