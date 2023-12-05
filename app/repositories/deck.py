import random
from typing import Optional

from app.models.battle import BattlePlayer, CardDeck
from app.models.card import Card
from app.models.deck import CustomDeck
from app.models.player import Player
from app.schemas import battle as schemas
from django_app.settings import ALLOW_ANY_DECK

from .base import BaseRepository
from .battle import BattleRepository


class DeckRepository(BaseRepository):  # pylint: disable=too-many-public-methods

    DB_MODEL = CardDeck

    @staticmethod
    def get_first_card(player: BattlePlayer) -> Optional[CardDeck]:
        return CardDeck.objects.filter(player=player).first()

    @staticmethod
    def get_player_selected_deck(player: Player) -> Optional[CustomDeck]:
        return player.custom_decks.filter(is_selected=True).first()

    @staticmethod
    def is_playable(count_cards: int, custom_deck: CustomDeck) -> bool:
        if ALLOW_ANY_DECK:
            return True
        return custom_deck.cards.all().count() == count_cards and custom_deck.all_cards_coded

    @staticmethod
    def remove_from_deck(deck_card: CardDeck) -> None:
        deck_card.delete()

    @classmethod
    def create_from_custom_deck(cls, battle_player: BattlePlayer, deck: CustomDeck) -> None:
        cards = list(Card.objects.filter(card_to_custom_deck__deck=deck).all())
        random.shuffle(cards)
        cls._create(battle_player, cards)

    @classmethod
    def create_from_cards_list(cls, battle_player: BattlePlayer, cards: list[Card]):
        cls._create(battle_player, cards)

    @classmethod
    def last_card_id(cls, battle) -> int:
        state = BattleRepository.get_state_from_redis(battle=battle)
        return state.last_battle_card_id

    @classmethod
    def set_last_card_id(cls, battle, new_id: int):
        state = BattleRepository.get_state_from_redis(battle=battle)
        state.last_battle_card_id = new_id
        BattleRepository.update_state_in_redis(battle=battle, new_state=state)

    @classmethod
    def _create(cls, battle_player: BattlePlayer, cards: list[Card]):
        deck_cards_to_create = []
        last_card_id = cls.last_card_id(battle=battle_player.battle)
        for idx, card in enumerate(cards):
            last_card_id += 1
            deck_cards_to_create.append(
                CardDeck(
                    card=card,
                    player=battle_player,
                    order=idx,
                    battle_card_id=last_card_id,
                    hp=card.hp,
                    attack=card.attack,
                )
            )
        cls.set_last_card_id(battle=battle_player.battle, new_id=last_card_id)

        CardDeck.objects.bulk_create(deck_cards_to_create)

    @staticmethod
    def create_card(
        *,
        deck_player: BattlePlayer,
        card: Card,
        last_card_in_deck_order: int,
        battle_card_id: Optional[int] = None,
    ) -> CardDeck:
        return CardDeck.objects.create(
            card=card,
            hp=card.hp,
            attack=card.attack,
            player=deck_player,
            order=last_card_in_deck_order + 1,
            battle_card_id=battle_card_id,
        )

    @staticmethod
    def delete_from_payers(players: list[BattlePlayer]):
        CardDeck.objects.filter(player__in=players).delete()

    @classmethod
    def set_next_card_in_deck(
        cls,
        player: Player,
        card: Optional[Card],
        state_in_redis: schemas.Battle,
    ):
        new_next_card = None
        if card:
            new_next_card = schemas.Card.from_orm(card)
        state_in_redis.players[player.id].deck.next_card = new_next_card
