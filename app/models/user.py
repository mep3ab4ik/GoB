from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """User model is responsible for authentication of users,
    is the same for both admin site users and player
    """

    class Meta:
        indexes = [
            models.Index(
                fields=['username'],
                name='user_username_idx',
            ),
            models.Index(
                fields=['metamask_token'],
                name='user_metamask_token_idx',
            ),
            models.Index(
                fields=['email'],
                name='user_email_idx',
            ),
        ]

    metamask_token = models.CharField(max_length=1024, blank=True, null=True)
    is_registered_with_email = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    last_username_changed = models.DateTimeField(blank=True, null=True, default=timezone.now)
