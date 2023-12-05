# pylint: disable=line-too-long
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AdminUser
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from app.admin import admin_site
from app.models.battle import Battle, BattlePlayer
from app.models.deck import CustomDeck
from app.models.player import Friendship, Player, PlayerStatus, WhitelistWallet
from app.models.stats import ActivePlayersOverTime, PlayerSession
from app.models.user import User
from app.utils.nft import get_nft_all


class UserAdmin(AdminUser):
    list_display = ['id', 'username', 'email', 'metamask_token', 'email_verified']

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'username',
                    'email',
                    'password',
                    'metamask_token',
                    'is_registered_with_email',
                    'email_verified',
                    'last_username_changed',
                )
            },
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin_site.register(User, UserAdmin)


class FriendshipInline(admin.TabularInline):
    model = Friendship
    extra = 0
    fk_name = 'player'


class CustomDeckInline(admin.TabularInline):
    model = CustomDeck
    ordering = ('order',)
    fields = [
        'name',
        'order',
        'is_selected',
    ]
    readonly_fields = [
        'order',
    ]
    extra = 1
    max_num = 5


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['user', 'player_id', 'add_all_nft_cards', 'is_gitex_bull', 'is_gitex_bear']
    list_editable = ['add_all_nft_cards', 'is_gitex_bull', 'is_gitex_bear']
    list_filter = ['is_gitex_bull', 'is_gitex_bear', 'add_all_nft_cards']
    search_fields = ['user__username', 'player_id']
    fields = ['user', 'avatar', 'add_all_nft_cards', 'is_gitex_bull', 'is_gitex_bear', 'Analytics']
    readonly_fields = [
        'Analytics',
    ]
    inlines = [FriendshipInline, CustomDeckInline]

    def get_table_line(self, name, data):
        return f"""
            <tr>
                <th scope="row">{name}</th>
                <td>{data}</td>
            </tr>
        """

    def Analytics(self, obj):  # pylint: disable=invalid-name
        all_data = get_nft_all(obj)
        if all_data:
            count_cards = len(all_data.get('cards')) if all_data.get('cards') else 0
            count_bodies = len(all_data.get('bodies')) if all_data.get('bodies') else 0
            count_avatars = len(all_data.get('avatars')) if all_data.get('avatars') else 0
        else:
            count_cards, count_bodies, count_avatars = 0, 0, 0

        all_player_battles_id_list = list(
            BattlePlayer.objects.filter(player_id=obj.id).values_list('battle_id', flat=True)
        )
        total_battle = Battle.objects.filter(id__in=all_player_battles_id_list, state='COMPLETED')
        total_win_battle = total_battle.filter(winner=obj)

        return format_html(
            f"""
            <h2>Web data</h1>
            <table>
                {self.get_table_line('Avatar count', count_avatars)}
                {self.get_table_line('Body count', count_bodies)}
                {self.get_table_line('Total NFT card count', count_cards)}
            </table>
            <h2>General</h2>
            <table>
                {self.get_table_line('Account date creation',
                obj.user.date_joined.strftime('%Y/%d/%m %I:%M:%S %p'))}
                {self.get_table_line('Last login date',
                obj.user.last_login.strftime('%Y/%d/%m %I:%M:%S %p'))}
                {self.get_table_line('Days offline',
                obj.days_offline)}
                {self.get_table_line('Current trophy count',
                obj.current_trophy_count)}
                {self.get_table_line('Previous season trophy count',
                obj.previous_season_trophy_count)}
                {self.get_table_line('Highest trophy count',
                obj.highest_trophy_count)}
                {self.get_table_line('Current arena name',
                obj.current_arena_name)}
                {self.get_table_line('Total battle count',
                total_battle.count())}
                {self.get_table_line('Total win count',
                total_win_battle.count())}
                {self.get_table_line('Genesis NFT cards count',
                obj.count_all_player_nft_cards)}
                {self.get_table_line('Genesis non-NFT cards count',
                obj.count_all_player_non_nft_cards)}
                {self.get_table_line('Current experience',
                obj.current_experience)}
                {self.get_table_line('Current level',
                obj.current_level)}
                {self.get_table_line('Total duration user spent in game',
                obj.humanized_total_duration_user_spent_in_game)}
                {self.get_table_line('Total average duration',
                obj.get_median_total_duration_user_spent_in_game)}
            </table>
        """
        )


admin_site.register(Player, PlayerAdmin)


class WhitelistWalletAdmin(admin.ModelAdmin):
    model = WhitelistWallet
    fields = ['wallet']
    list_display = ['wallet']


admin_site.register(WhitelistWallet, WhitelistWalletAdmin)


class PlayerSessionAdmin(admin.ModelAdmin):
    model = PlayerSession
    list_display = ['player', 'session_start', 'session_end']
    fields = ['player', 'session_start', 'session_end']


admin_site.register(PlayerSession, PlayerSessionAdmin)


class ActivePlayersOverTimeAdmin(admin.ModelAdmin):
    model = ActivePlayersOverTime
    list_display = ['created_at', 'players_online', 'players_in_battle']
    fields = ['created_at', 'players_online', 'players_in_battle']


admin_site.register(ActivePlayersOverTime, ActivePlayersOverTimeAdmin)


class PlayerStatusAdmin(admin.ModelAdmin):
    model = PlayerStatus
    fields = ['name', 'title']
    list_display = ['name', 'title']


admin_site.register(PlayerStatus, PlayerStatusAdmin)
