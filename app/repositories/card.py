from app.models.card import Card
from app.repositories.base import BaseRepository


class CardRepository(BaseRepository):

    DB_MODEL = Card

    @staticmethod
    def get_published_cards() -> set[Card]:
        return set(Card.objects.filter(is_enabled=True))
