import os

from app.ws_consumers.lobby_consumer import LobbyConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from django.urls import re_path

# TODO Token params is temporary solution
websocket_urlpatterns = [
    re_path(r'^ws/lobby/(?P<token>[a-zA-Z0-9_,-]+)/$', LobbyConsumer.as_asgi()),
]
