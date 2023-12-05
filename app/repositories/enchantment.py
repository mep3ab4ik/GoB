# pylint: disable=too-many-public-methods
from typing import List, Optional

from app.models.battle import Enchantment, EnchantmentKeywordsEnum, EnchantmentTypeEnum, Tile
from app.repositories.base import BaseRepository
from app.schemas import battle as schemas_battle


class EnchantmentRepository(BaseRepository):

    DB_MODEL = Enchantment

    @staticmethod
    def update_enchantments(tile: Tile, enchantments: List[Enchantment]):
        for enchantment in enchantments:
            enchantment.id = None
            enchantment.card_hand = None
            enchantment.tile = tile
            enchantment.save()

    @staticmethod
    def create_tile_buffs(tile: Tile):
        Enchantment.objects.get_or_create(
            keyword=EnchantmentKeywordsEnum.tile_buff,
            tile=tile,
            affects_attack=True,
            type=EnchantmentTypeEnum.buff,
            attack_change_value=1,
        )

    @staticmethod
    def get_tile_buffs(tile: Tile):
        return Enchantment.objects.filter(
            keyword=EnchantmentKeywordsEnum.tile_buff,
            tile=tile,
            affects_attack=True,
            type=EnchantmentTypeEnum.buff,
            attack_change_value=1,
        )

    @staticmethod
    def create_cache(
        tile: Tile,
        enchantment: Enchantment,
        state: schemas_battle.Battle,
        active: bool = True,
    ):
        state.players[tile.player.player.id].tiles[tile.id].enchantments[
            enchantment.id
        ] = schemas_battle.Enchantment(
            id=enchantment.id,
            keyword=enchantment.keyword,
            type=enchantment.type,
            active=active,
        )

    @staticmethod
    def get_enchantment_in_cache(
        tile: Tile, keyword: EnchantmentKeywordsEnum, state: schemas_battle.Battle
    ) -> Optional[schemas_battle.Enchantment]:
        for _, enchantment in (
            state.players[tile.player.player.id].tiles[tile.id].enchantments.items()
        ):
            if enchantment.keyword == keyword:
                return enchantment
        return None

    @classmethod
    def update_enchantment_in_cache(
        cls,
        tile: Tile,
        state: schemas_battle.Battle,
        keyword: EnchantmentKeywordsEnum,
        active: bool,
    ):
        enchantment_insult = cls.get_enchantment_in_cache(tile=tile, keyword=keyword, state=state)
        if enchantment_insult:
            state.players[tile.player.player.id].tiles[tile.id].enchantments[
                enchantment_insult.id
            ].active = active

    @staticmethod
    def update_enchantment_in_cache_by_id(
        tile: Tile, state: schemas_battle.Battle, id_enchantment: int, active: bool
    ):
        state.players[tile.player.player.id].tiles[tile.id].enchantments[
            id_enchantment
        ].active = active

    @staticmethod
    def drop_enchantments_by_tile_in_cache(tile: Tile, state: schemas_battle.Battle):
        state.players[tile.player.player.id].tiles[tile.id].enchantments = {}

    @staticmethod
    def filter_by_tile_and_keyword(tile: Tile, keyword: EnchantmentKeywordsEnum):
        return Enchantment.objects.filter(tile=tile, keyword=keyword)

    @classmethod
    def delete_by_tile_and_keyword(
        cls,
        tile: Tile,
        keyword: EnchantmentKeywordsEnum,
        state: Optional[schemas_battle.Battle] = None,
    ):
        enchantments = cls.filter_by_tile_and_keyword(tile=tile, keyword=keyword)
        if enchantments.exists():
            enchantments.first().delete()
        if not state:
            return
        enchantment = cls.get_enchantment_in_cache(tile=tile, keyword=keyword, state=state)
        if enchantment:
            state.players[tile.player.player.id].tiles[tile.id].enchantments.pop(enchantment.id)

    @classmethod
    def delete_queryset(cls, enchantments):
        enchantments.delete()
