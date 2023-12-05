# pylint: disable=line-too-long
import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from nested_inline.admin import NestedModelAdmin, NestedTabularInline
from nonrelated_inlines.admin import NonrelatedStackedInline

from app.admin.general import admin_site
from app.card_abilities.card_utils import get_class_card
from app.enums.card import CardEditions
from app.exceptions import CardAbilityNotFound
from app.models.arena import Arena
from app.models.battle import Battle, BattleLogMongo, EventHistory
from app.models.card import Card, CardAction, CardRelationShip, CardSeries, CardSubtype
from app.models.deck import PreAssembledDeck, PreAssembledDeckToCard


class EventHistoryInline(NestedTabularInline):
    model = EventHistory
    fields = [
        'created_at',
        'event_source',
        'event_destination',
        'event_type',
        'event_raw_message',
    ]
    extra = 1


class BattleLogInline(NonrelatedStackedInline):  # pylint: disable=abstract-method
    template = NestedTabularInline.template
    model = BattleLogMongo
    fields = ['timestamp', 'battle_player_id', 'event_type', 'get_event_json']
    readonly_fields = ['timestamp', 'battle_player_id', 'event_type', 'get_event_json']
    search_fields = ['room_id']
    extra = 1

    def get_form_queryset(self, obj):
        return self.model.objects.filter(battle_id=str(obj.id)).all()

    def get_event_json(self, obj):
        return json.dumps(obj.event_json)

    get_event_json.description = get_event_json.short_description = 'event_json'


class BattleAdmin(NestedModelAdmin):
    change_form_template = 'admin/battle_logs/change_form_button_json.html'
    list_display = ['room_id', 'created_at', 'game_mode', 'game_mode_season']
    fields = [
        'room_id',
        'player_1_ticket',
        'player_2_ticket',
        'created_at',
        'battle_start',
        'battle_end',
        'state',
        'winner',
        'game_mode',
        'game_mode_season',
    ]
    list_filter = ['game_mode', 'game_mode_season']
    inlines = [EventHistoryInline, BattleLogInline]


admin_site.register(Battle, BattleAdmin)


class CardActionInline(NestedTabularInline):
    model = CardAction
    fields = ['order', 'action_type', 'minion', 'spell_name']
    extra = 1


class CardRelationshipInline(admin.StackedInline):
    model = CardRelationShip
    extra = 0
    min_num = 1


class CardFilter(admin.SimpleListFilter):
    title = 'Coded'
    parameter_name = 'is_coded'

    def lookups(self, request, model_admin):
        return (('coded_but_disabled', _('Coded but disabled')),)

    def queryset(self, request, queryset):
        if self.value() != 'coded_but_disabled':
            return None

        cards_not_is_enabled = queryset.filter(is_enabled=False)
        list_is_coded_cards = []
        for card in cards_not_is_enabled:
            try:
                get_class_card(card.custom_id)
                list_is_coded_cards.append(card.custom_id)
            except CardAbilityNotFound:
                continue
        return queryset.filter(custom_id__in=list_is_coded_cards)


class CardAdmin(NestedModelAdmin):
    change_form_template = 'admin/admin_from_card_model/error_from_card_is_enabled.html'
    list_display = [
        'name',
        'custom_id',
        'by_artist',
        'description',
        'approval',
        'rarity',
        'element',
        'nft_card_type',
        'bake_image',
        'card_image_tag',
    ]
    fields = [
        'custom_id',
        'name',
        'is_enabled',
        'by_artist',
        'description',
        'rarity',
        'approval',
        'hp',
        'type',
        'targeting',
        'targeting_type',
        'attack',
        'element',
        'nft_card_type',
        'original_illustration',
        'regular_edition_illustration',
        'shiny_edition_illustration',
        'card_series',
        'subtypes',
        'card_image_preview',
    ]
    readonly_fields = ['card_image_preview']
    list_filter = [
        'element',
        'by_artist',
        'approval',
        'rarity',
        'nft_card_type',
        'type',
        'is_enabled',
        CardFilter,
    ]
    search_fields = ['name', 'custom_id']
    list_editable = ['approval']
    inlines = [CardActionInline]
    actions = ['set_enabled']

    def card_image_tag(self, obj):
        return (
            format_html(f'<img src="{obj.original_illustration.url}" height="140px"/>')
            if obj.original_illustration
            else format_html('')
        )

    def card_image_preview(self, obj):
        return (
            format_html(f'<img src="{obj.original_illustration.url}" height="512px"/>')
            if obj.original_illustration
            else format_html('')
        )

    def card_image_regular_preview(self, obj):
        return (
            format_html(
                f'<div style="display: flex; justify-content: center;">'
                f'<img src="{obj.card_regular_image.url}" height="140px"/>'
                f'</div>'
            )
            if obj.card_regular_image
            else format_html('')
        )

    def card_image_shiny_preview(self, obj):
        return (
            format_html(
                f'<div style="display: flex; justify-content: center;">'
                f'<img src="{obj.card_shiny_image.url}" height="140px"/>'
                f'</div>'
            )
            if obj.card_shiny_image
            else format_html('')
        )

    def bake_image(self, obj):
        return format_html(
            '<br>'.join(
                [
                    f'<a href="/api/v1/card/bake/{obj.id}/{edition[0]}/" '
                    f'target="_blank">Bake card ({edition[0].capitalize()})</a>'
                    for edition in CardEditions
                ]
            )
        )

    @admin.action(description='Set enable')
    def set_enabled(self, request, queryset):  # pylint: disable=unused-argument
        for qs in queryset:
            qs.is_enabled = True
            qs.save()

    class Media:
        js = ('card/js/card.js',)


admin_site.register(Card, CardAdmin)


class CardSeriesAdmin(admin.ModelAdmin):
    list_display = ['name']
    fields = ['name']


admin_site.register(CardSeries, CardSeriesAdmin)


class CardSubtypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    fields = ['name']


admin_site.register(CardSubtype, CardSubtypeAdmin)


class PreAssembledDeckCardInline(admin.TabularInline):
    model = PreAssembledDeckToCard
    fields = ['card', 'order']
    extra = 1


class PreAssembledDeckAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']
    fields = ['name', 'order']
    inlines = [PreAssembledDeckCardInline]


admin_site.register(PreAssembledDeck, PreAssembledDeckAdmin)


class ArenaAdmin(admin.ModelAdmin):
    model = Arena
    fields = ['name', 'required_trophies']
    list_display = ['name', 'required_trophies']


admin_site.register(Arena, ArenaAdmin)
