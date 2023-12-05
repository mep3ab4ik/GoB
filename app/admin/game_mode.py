from django.contrib import admin

from app.admin.general import admin_site
from app.models import game_mode


class GameModeSeasonInline(admin.TabularInline):
    model = game_mode.GameModeSeason
    fields = ['starts_at', 'ends_at', 'season_reset_multiplier']
    extra = 1


class BlockedCardsInGameModeInline(admin.TabularInline):
    model = game_mode.BlockedCardsInGameMode
    autocomplete_fields = ['card']
    extra = 1


class SkillPointsLadderInline(admin.TabularInline):
    model = game_mode.SkillPointsLadder
    fields = ['level', 'skill_points_required', 'xp_reward']
    extra = 1


class GameModeAdmin(admin.ModelAdmin):
    model = game_mode.GameMode
    list_display = [
        'title',
        'custom_id',
        'description',
        'battlefield_timer_duration',
        'default_game_mode',
        'earn_skill_points_in_this_mode',
    ]
    list_editable = [
        'custom_id',
    ]
    fields = [
        'title',
        'custom_id',
        'description',
        'battlefield_timer_duration',
        'start_battle_player_hp',
        'default_game_mode',
        'max_cards_in_hand',
        'start_cards_on_hand_count',
        'max_tiles_per_player',
        'max_cards_in_deck',
        'earn_skill_points_in_this_mode',
        'is_graveyard_enabled',
        'show_next_card_from_deck',
        'is_random_generated_deck',
        'deal_damage_to_avatar_on_empty_deck',
        'battle_duration',
    ]
    inlines = [GameModeSeasonInline, SkillPointsLadderInline, BlockedCardsInGameModeInline]


admin_site.register(game_mode.GameMode, GameModeAdmin)
