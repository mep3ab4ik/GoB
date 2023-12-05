from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from app.repositories.deck import DeckRepository
from app.utils.statistics import update_player_statistics

from .battle import Battle, CardHand
from .deck import CustomDeck
from .game_mode import PlayerSeasonStats


@receiver(pre_save, sender=CardHand)
def set_battle_card_id_if_empty(
    sender, instance: CardHand, **kwargs
):  # pylint: disable=unused-argument
    if not instance.id and not instance.battle_card_id and instance.card:
        last_card_id = DeckRepository.last_card_id(instance.player.battle)
        instance.battle_card_id = last_card_id + 1
        DeckRepository.set_last_card_id(instance.player.battle, instance.battle_card_id)


@receiver(post_save, sender=Battle)
def update_payers_stats_on_battle_end(
    sender, instance: Battle, created, **kwargs
):  # pylint: disable=unused-argument
    if created or not instance.winner:
        return

    season = instance.game_mode_season
    player_one, player_two = instance.players.all()
    update_player_statistics(user=player_one.player)
    update_player_statistics(user=player_one.player, season=instance.game_mode_season)
    update_player_statistics(user=player_two.player)
    update_player_statistics(user=player_two.player, season=instance.game_mode_season)
    if not season:
        return
    # add 2SP to winner
    winner = instance.winner
    loser = player_one.player if player_one.player.id != winner.id else player_two.player
    player_season, created = PlayerSeasonStats.objects.get_or_create(player=winner, season=season)
    player_season.add_skill_points_on_battle_complete(battle=instance, is_winner=True)

    # subtract 1SP from loser
    loser_player_season, created = PlayerSeasonStats.objects.get_or_create(
        player=loser, season=season
    )
    loser_player_season.add_skill_points_on_battle_complete(battle=instance, is_winner=False)


@receiver(post_delete, sender=CustomDeck, dispatch_uid='CustomDeck_delete')
def delete_custom_deck_object(sender, instance, using, **kwargs):  # pylint: disable=unused-argument
    for num, player_deck in enumerate(instance.player.custom_decks.order_by('id')):
        player_deck.order = num + 1
        player_deck.save()
