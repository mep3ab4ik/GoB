import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')

app = Celery('django_app')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    from app.tasks import (
        record_player_stats,
        sync_bods,
        update_global_statistics,
        update_last_activity,
    )

    # Every hour
    sender.add_periodic_task(1 * 60 * 60, sync_bods.s())

    # Every 1 minutes
    sender.add_periodic_task(1 * 60, update_global_statistics.s())
    sender.add_periodic_task(1 * 60, record_player_stats.s())

    # every 10 seconds
    sender.add_periodic_task(1 * 10, update_last_activity.s())
