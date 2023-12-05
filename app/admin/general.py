# pylint: disable=line-too-long
import json
import logging

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db import models
from django.utils.html import format_html
from django_json_widget.widgets import JSONEditorWidget
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import TokenProxy

from app.models.analytics_info import AnalyticsInfo
from app.models.cache import CachingTime
from app.models.client_version import ClientVersion
from app.models.keyword import Keyword
from app.models.onboarding import Onboarding
from app.models.trace import Trace
from app.redis_client import redis_client
from app.tasks import update_global_statistics
from django_app.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    BATTLE_CONSUMER_REDIS_GROUP_PREFIX,
    CLIENT_VERSION_CONFIG_BUCKET_NAME,
    CLIENT_VERSION_CONFIG_FILE_NAME,
)
from storage.s3 import S3Storage

logger = logging.getLogger()


class MyAdminSite(AdminSite):
    site_header = 'GOB Game'

    def index(self, request, extra_contex=None):  # pylint: disable=arguments-renamed
        statistics = cache.get('global_statistics')

        if not statistics:
            update_global_statistics()
            statistics = cache.get('global_statistics')

        custom_extra_context = {
            'total_players': statistics['players']['all_time'],
            'total_players_online': statistics['players']['online'],
            'total_players_in_battle': len(
                redis_client.keys(f'asgi:group:{BATTLE_CONSUMER_REDIS_GROUP_PREFIX}*')
            ),  # avoids 1 player online and 2 players in battle situation
        }
        if extra_contex:
            extra_contex.update(custom_extra_context)
        else:
            extra_contex = custom_extra_context
        return super().index(request, extra_contex)


admin_site = MyAdminSite(name='myadmin')
admin_site.register(Keyword)


class TraceAdmin(admin.ModelAdmin):
    list_display = [
        'error',
        'traceback_br',
        'traceback_hash',
        'count_triggered',
        'resolved',
    ]
    search_fields = ['traceback_hash']
    list_filter = ['resolved']
    list_editable = ['resolved']
    ordering = ['-last_time_triggered']
    readonly_fields = [
        'count_triggered',
        'first_time_triggered',
        'last_time_triggered',
        'traceback_hash',
        'traceback',
        'error',
    ]

    @staticmethod
    def traceback_br(obj):
        margin_left = '<span style="margin-left: 2em"></span>'
        font_weight = f'<span style="font-weight: bold">{obj.error}</span>'
        color = '<p style="color: #4c000f">' + obj.traceback.replace('\n', '<br>') + '</p>'
        color.replace('  ', margin_left).replace(obj.error, font_weight)

        try:
            return format_html(color)
        except Exception:  # pylint: disable=broad-except
            return None

    traceback_br.short_description = 'Traceback'


admin_site.register(Trace, TraceAdmin)
admin_site.register(TokenProxy, TokenAdmin)
admin_site.register(Group, GroupAdmin)


class TimeCachingAdmin(admin.ModelAdmin):
    model = CachingTime
    list_display = ['player_statistics', 'global_statistics']
    fields = ['player_statistics', 'global_statistics']


admin_site.register(CachingTime, TimeCachingAdmin)


class ClientVersionAdmin(admin.ModelAdmin):
    model = ClientVersion
    list_display = ['created_at', 'version', 'is_currently_selected']
    fields = ['created_at', 'version', 'is_currently_selected']
    readonly_fields = ['is_currently_selected']

    actions = ('choose_version',)

    def choose_version(self, request, queryset):  # pylint: disable=unused-argument
        version: ClientVersion
        if queryset.count() != 1:
            logger.info('Must select only one instance')
            return

        version = queryset.first()
        ClientVersion.objects.filter(is_currently_selected=True).update(is_currently_selected=False)
        version.is_currently_selected = True
        version.save()
        storage = S3Storage(
            aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        storage.upload_file_to_bucket(
            file=version.as_file,
            bucket=CLIENT_VERSION_CONFIG_BUCKET_NAME,
            file_path=CLIENT_VERSION_CONFIG_FILE_NAME,
        )

    choose_version.short_description = 'Select this version'


admin_site.register(ClientVersion, ClientVersionAdmin)


class OnboardingAdmin(admin.ModelAdmin):
    model = Onboarding
    list_display = ['get_row_str', 'updated_at']
    readonly_fields = ['updated_at']
    fields = ['data', 'updated_at']
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_row_str(self, request):  # pylint: disable=unused-argument
        return 'Onboarding record'

    get_row_str.short_description = get_row_str.description = 'Row'


admin_site.register(Onboarding, OnboardingAdmin)


class AnalyticsInfoAdmin(admin.ModelAdmin):
    model = AnalyticsInfo
    fields = ['user_id', 'created_at', 'event_name', 'get_event_json']
    list_display = ['id', 'event_name', 'user_id']

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_event_json(self, obj):
        return json.dumps(obj.event_json)

    get_event_json.description = get_event_json.short_description = 'event_json'


admin_site.register(AnalyticsInfo, AnalyticsInfoAdmin)
