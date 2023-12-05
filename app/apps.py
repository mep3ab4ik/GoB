from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    verbose_name = 'App GOB Game'

    def ready(self):
        import app.models.signals  # noqa:F401  pylint:disable=import-outside-toplevel,unused-import
