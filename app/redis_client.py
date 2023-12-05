from django.conf import settings
from redis import Redis

redis_client = Redis(settings.REDIS_HOST, db=1, decode_responses=True)
