"""
ASGI config for django_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')

import django

django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import app.routing
from app.custom_authentication_middleware import TokenAuthMiddlewareFromPath

websocket_router = URLRouter(app.routing.websocket_urlpatterns)

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': TokenAuthMiddlewareFromPath(websocket_router),
    }
)
