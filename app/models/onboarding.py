from django.db import models


class Onboarding(models.Model):
    data = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)
