from django.conf import settings
from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.authentication import BasicAuthentication

from app.generators import BothHttpAndHttpsSchemaGenerator


class Yasg:
    def __init__(self, version=None):
        schema_view = get_schema_view(
            openapi.Info(**getattr(settings, 'API_INFO', {}), default_version=version),
            public=True,
            authentication_classes=(BasicAuthentication,),
            generator_class=BothHttpAndHttpsSchemaGenerator,
        )
        self.scheme = url(
            r'^(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema',
        )
        self.swagger = url(
            r'^$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui',
        )
        self.redoc = url(
            r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc',
        )
