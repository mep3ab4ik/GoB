# pylint: disable=too-many-lines
import datetime
import logging
from datetime import timedelta
from typing import List, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from app.repositories.base import BaseRepository
from app.repositories.deck import DeckRepository
from app.repositories.player import PlayerRepository
from app.repositories.tile import TileRepository
from django_app.celery import app
from utils.download_full_bodies import download_full_bodies
from utils.resize_full_bodies import resize_full_bodies
from utils.upload_full_bodies import upload_full_bodies

from .models.battle import Battle, BattleLogMongo
from .models.cache import CachingTime
from .models.card import Card
from .models.player import Player, PlayerActivity, PlayerCard
from .models.stats import ActivePlayersOverTime
from .redis_client import redis_client
from .repositories.battle import BattleRepository
from .repositories.battle_player import BattlePlayerRepository
from .repositories.card import CardRepository
from .repositories.game_mode import GameModeRepository
from .utils.nft import NFTCard, get_nft_cards

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.task
def grace_time_disconnect(battle_id, player_id, channel_name, disconnect_uuid: Optional[str]):
    battle = Battle.objects.get(id=battle_id)
    if battle.state in (
        Battle.States.DISCARDED,
        Battle.States.COMPLETED,
        Battle.States.ACTIVE,
    ):
        # player reconnected or the second player left as well
        return
    if BattleRepository.get_reconnect_cache(battle_id, player_id) != disconnect_uuid:
        # different grace time disconnect task should be running
        return

    if battle.state != Battle.States.AWAITING_RECONNECT:
        # this code should never run
        # don't want to call assert but want to see if I missed something in logs
        logger.error('Review grace_time_disconnect logic!')

    winner = Player.objects.get(id=player_id)
    battle.complete(winner)

    layer = get_channel_layer()
    async_to_sync(layer.send)(
        channel_name,
        {'type': 'battle_complete', 'message': {'result_type': 'victory'}},
    )


@app.task
def sync_nft_cards(player_id) -> None:  # pylint: disable=too-many-statements
    # used by rest api to get sync cards status, discuss if client is using it, if not - delete
    cache.set(f'player_{player_id}_sync_in_progress', 'in_progress', 300)
    player = Player.objects.get(id=player_id)

    if player.add_all_nft_cards:
        cards: List[NFTCard] = [
            NFTCard(custom_id=custom_id, edition_shiny=0, edition_regular=1)
            for custom_id in Card.objects.exclude(custom_id__icontains='DD').values_list(
                'custom_id', flat=True
            )
        ]
    else:
        # additionally should consider using serializer or pydantic model to validate format
        cards: List[NFTCard] = get_nft_cards(player)

        # add non-nft cards
        cards += [
            NFTCard(custom_id=custom_id, edition_shiny=0, edition_regular=1)
            for custom_id in Card.objects.filter(custom_id__icontains='B').values_list(
                'custom_id', flat=True
            )
        ]

    # reformat cards list so it's more convenient to process
    cards_with_count = {}
    for card in cards:
        if card.edition_shiny:
            cards_with_count[f'{card.custom_id}:shiny'] = card.edition_shiny
        if card.edition_regular:
            cards_with_count[f'{card.custom_id}:regular'] = card.edition_regular

    # sync db with received cards. max 5 sql calls
    all_cards_as_dict = {card.custom_id: card for card in Card.objects.all()}
    player_cards: List[PlayerCard] = PlayerCard.objects.filter(player=player).select_related('card')

    cards_to_update = []
    card_ids_to_remove = []

    for player_card in player_cards:
        player_card_label = f'{player_card.card.custom_id}:{player_card.edition}'
        if player_card_label not in cards_with_count:
            # db record exists, but not returned from the nft endpoint
            card_ids_to_remove.append(player_card.id)
        elif cards_with_count[player_card_label] != player_card.quantity:
            # quantity updated
            player_card.quantity = cards_with_count[player_card_label]
            cards_to_update.append(player_card)
            cards_with_count.pop(player_card_label)
        else:
            # nothing changed, just pop the cards_with_count dict,
            # whatever is left in cards_with_count
            # are new cards, need to create them
            cards_with_count.pop(player_card_label)

    PlayerCard.objects.bulk_update(cards_to_update, ['quantity'])
    PlayerCard.objects.filter(id__in=card_ids_to_remove).delete()
    logger.info('Updated %s card quantities for player %s', len(cards_to_update), player_id)
    logger.info('Removed %s cards for player %s', len(card_ids_to_remove), player_id)

    cards_to_create = []
    for card_label, quantity in cards_with_count.items():
        custom_id, edition = card_label.split(':')
        card = all_cards_as_dict[custom_id]
        cards_to_create.append(
            PlayerCard(card=card, edition=edition, quantity=quantity, player=player)
        )

    PlayerCard.objects.bulk_create(cards_to_create)
    logger.info('Created %s cards for player %s', len(cards_to_create), player_id)
    cache.delete(f'player_{player_id}_sync_in_progress')


@app.task
def end_turn_timer(
    battle_id: int, turn_number: int, turn_idx: int, player_id: int, opponent_id: int
):
    battle = Battle.objects.get(id=battle_id)
    battle_state = battle.state not in (Battle.States.ACTIVE, Battle.States.AWAITING_RECONNECT)
    if battle.turn != turn_idx or battle.turn_number != turn_number or battle_state:
        return
    player = Player.objects.get(id=player_id)
    player_channel_name = PlayerRepository.get_player_channel_name(player)
    opponent = Player.objects.get(id=opponent_id)
    opponent_channel_name = PlayerRepository.get_player_channel_name(opponent)

    layer = get_channel_layer()
    if player_channel_name:
        async_to_sync(layer.group_send)(
            player_channel_name, {'type': 'battle_next_round', 'message': {}}
        )  # this is a client event but called from this function
    else:
        # player is disconnected call next round from opponent consumer
        async_to_sync(layer.group_send)(
            opponent_channel_name,
            {'type': 'battle_next_round_internal', 'message': {'player_id': player_id}},
        )  # this is a client event but called from this function


@app.task
def sync_bods():
    logger.info('Sync bods started')
    download_full_bodies()
    resize_full_bodies()
    upload_full_bodies()


@app.task
def start_battle_countdown(
    battle_id, my_channel_name, opponent_channel_name, player_id, opponent_id
):  # pylint: disable=import-outside-toplevel
    battle = Battle.objects.get(id=battle_id)
    logger.info('Battle started')
    battle_start(battle)
    layer = get_channel_layer()
    async_to_sync(layer.send)(
        my_channel_name,
        {
            'type': 'start_battle',
            'message': {'round_duration': battle.game_mode.battlefield_timer_duration},
        },
    )
    async_to_sync(layer.send)(
        opponent_channel_name,
        {
            'type': 'start_battle',
            'message': {'round_duration': battle.game_mode.battlefield_timer_duration},
        },
    )

    if battle.game_mode.show_next_card_from_deck:
        from app.battle_service import next_card_in_deck

        logger.debug('Creating battle_state_%s in redis...', battle.room_id)
        battle_player = BattlePlayerRepository.get(player_id, battle)
        opponent_battle_player = BattlePlayerRepository.get(opponent_id, battle)

        next_card_in_deck(
            battle=battle,
            player=battle_player,
        )
        next_card_in_deck(
            battle=battle,
            player=opponent_battle_player,
        )
        battle_state_in_redis = BattleRepository.get_state_from_redis(battle)
        player_next_card = battle_state_in_redis.players[player_id].deck.next_card
        enemy_next_card = battle_state_in_redis.players[opponent_id].deck.next_card

        async_to_sync(layer.send)(
            my_channel_name,
            {
                'type': 'next_card_in_deck',
                'message': {'next_card': player_next_card.dict() if player_next_card else None},
            },
        )
        async_to_sync(layer.send)(
            opponent_channel_name,
            {
                'type': 'next_card_in_deck',
                'message': {'next_card': enemy_next_card.dict() if enemy_next_card else None},
            },
        )


@app.task
def update_last_activity():
    all_keys_in_cache = cache.keys('*')
    for iter_keys in all_keys_in_cache:
        if iter_keys.startswith('last_activity-'):
            last_activity_data = cache.get(iter_keys)
            player_id = iter_keys.split('-')[-1]
            player = Player.objects.get(player_id=player_id)
            player.last_activity = last_activity_data
            player.save()
            PlayerActivity.objects.update_or_create(
                player=player,
                start_activity=player.user.last_login,
                defaults={'end_activity': timezone.now()},
            )


@app.task
def update_global_statistics():
    logger.debug('Updating global statistics...')
    player_queryset = Player.objects
    battle_queryset = Battle.objects
    caching_time_row = CachingTime.objects.first()
    caching_time = (
        caching_time_row.global_statistics
        if caching_time_row
        else settings.GLOBAL_STATISTICS_DEFAULT_CACHE_TIME
    )

    online_players_count = 0
    cursor = 0

    while True:
        cursor, results = redis_client.scan(
            cursor, f'asgi:group:{settings.LOBBY_CONSUMER_REDIS_GROUP_PREFIX}-*', 1000
        )
        online_players_count += len(results)
        if not cursor:
            break

    statistic = {
        'battles': {
            'all_time': battle_queryset.count(),
            'last_30_days': battle_queryset.filter(
                battle_end__gte=datetime.datetime.now() - timedelta(days=30)
            ).count(),
            'last_7_days': battle_queryset.filter(
                battle_end__gte=datetime.datetime.now() - timedelta(days=7)
            ).count(),
            'today': battle_queryset.filter(
                battle_end__gte=datetime.datetime.now() - timedelta(days=1)
            ).count(),
            'active': battle_queryset.filter(state__in=Battle.States.active_states()).count(),
        },
        'players': {
            'all_time': player_queryset.count(),
            'last_30_days': player_queryset.filter(
                last_activity__gte=datetime.datetime.now() - timedelta(days=30)
            ).count(),
            'last_7_days': player_queryset.filter(
                last_activity__gte=datetime.datetime.now() - timedelta(days=7)
            ).count(),
            'today': player_queryset.filter(
                last_activity__gte=datetime.datetime.now() - timedelta(days=1)
            ).count(),
            'online': online_players_count,
        },
    }

    cache.set('global_statistics', statistic, caching_time)
    logger.info('Global statistics updated')


@app.task
def record_player_stats():
    ActivePlayersOverTime.objects.create(
        players_online=len(
            redis_client.keys(f'asgi:group:{settings.LOBBY_CONSUMER_REDIS_GROUP_PREFIX}*')
        ),
        players_in_battle=len(
            redis_client.keys(f'asgi:group:{settings.BATTLE_CONSUMER_REDIS_GROUP_PREFIX}*')
        ),
    )


@app.task
def save_battle_log_to_mongo(battle_id, battle_player_id, event_type, content):
    BattleLogMongo.objects.create(
        battle_id=str(battle_id),
        battle_player_id=str(battle_player_id),
        event_type=event_type,
        event_json=content,
    )


@app.task
def battle_duration(battle_id):
    logger.info('The battle time is over')
    battle = BattleRepository.get_from_battle_id(battle_id)
    battle_player1, battle_player2 = battle.players.all()
    get_channel_layer()
    layer = get_channel_layer()
    event_loss = {'type': 'battle_complete', 'message': {'result_type': 'loss'}}
    event_victory = {'type': 'battle_complete', 'message': {'result_type': 'victory'}}
    if battle_player1.hp == battle_player2.hp:
        logger.info(
            'Sending the event of the end of the battle. hp are equal, battle state = discarded'
        )
        BattleRepository.set_state(battle, Battle.States.DISCARDED, ended_at=timezone.now())
        channel_name = BattleRepository.get_battle_channel_name(battle)
        async_to_sync(layer.group_send)(channel_name, event_loss)
        BattleRepository.save(battle)
        return

    winner = battle_player1 if battle_player1.hp > battle_player2.hp else battle_player2
    surrender = battle_player2 if winner == battle_player1 else battle_player1
    events = (
        (PlayerRepository.get_player_channel_name(winner.player), event_victory),
        (PlayerRepository.get_player_channel_name(surrender.player), event_loss),
    )
    logger.info('Sending the event of the end of the battle')
    for channel, event in events:
        async_to_sync(layer.group_send)(channel, event)

    BattleRepository.set_state(
        battle, Battle.States.COMPLETED, winner=winner.player, ended_at=timezone.now()
    )
    BattleRepository.save(battle)


def battle_start(  # pylint: disable=too-many-statements
    battle: Battle,
) -> None:
    from app import battle_service  # pylint: disable=import-outside-toplevel

    battle.battle_start = timezone.now()
    current_turn_player = None
    opponent_player = None
    players = battle.players.all()
    state_redis = BattleRepository.get_state_from_redis(battle)
    for battle_player in players:
        if battle.game_mode.is_random_generated_deck:
            count_cards_from_game_mode = battle.game_mode.max_cards_in_deck
            blocked_cards = GameModeRepository.get_blocked_cards(battle.game_mode)
            all_cards = CardRepository.get_published_cards()
            all_cards -= blocked_cards
            all_cards = BaseRepository.random_objects(all_cards, count_cards_from_game_mode)
            DeckRepository.create_from_cards_list(battle_player, all_cards)
        else:
            deck = DeckRepository.get_player_selected_deck(battle_player.player)
            DeckRepository.create_from_custom_deck(battle_player, deck)

        for _ in range(battle.game_mode.start_cards_on_hand_count):
            deck_card = DeckRepository.get_first_card(battle_player)
            if not deck_card:
                # can be triggered if user has less than 5 cards in deck
                break
            battle_service.create_last_card_in_hand(
                hand_player=deck_card.player,
                card=deck_card.card,
                battle_card_id=deck_card.battle_card_id,
            )
            deck_card.delete()
        TileRepository.create_from_battle_player(battle_player=battle_player, state=state_redis)
        if battle_player.idx != battle.turn:
            TileRepository.create_from_battle_player(battle_player=battle_player, state=state_redis)
            opponent_player = battle_player.player
        else:
            current_turn_player = battle_player.player
            battle.current_turn_player = battle_player
    BattleRepository.set_round_started_at(state_redis)
    BattleRepository.update_state_in_redis(battle=battle, new_state=state_redis)
    end_turn_timer.apply_async(
        args=(
            battle.id,
            battle.turn_number,
            battle.turn,
            current_turn_player.id if current_turn_player else None,
            opponent_player.id if opponent_player else None,
        ),
        serializer='json',
        countdown=battle.game_mode.battlefield_timer_duration,
    )
    battle_duration.apply_async(
        args=(battle.id,),
        serializer='json',
        countdown=battle.game_mode.battle_duration,
        task_id=battle.room_id,
    )
    battle.save()
