from app.card_abilities.state import State
from app.models.battle import Tile
from app.repositories.enchantment import EnchantmentRepository
from app.repositories.tile import TileRepository
from app.utils.battle_consumer_utils import BattleServerEventsEnum, ServerEventData


class TileService:
    @classmethod
    def update_tile_buffs(cls, tile: Tile):
        if tile.element is None or tile.card is None:
            return
        if (
            tile.element != Tile.Elements.NEUTRAL
            and tile.element.lower() == tile.card.element.lower()
        ):
            EnchantmentRepository.create_tile_buffs(tile=tile)
            return
        tile_buff_enchantments = EnchantmentRepository.get_tile_buffs(tile=tile)
        EnchantmentRepository.delete_queryset(tile_buff_enchantments)

    @classmethod
    def tile_update_element(cls, state: State, tile: Tile, new_element: str) -> Tile:

        """
        Parameters
        ----------
        state
            Battle state
        tile
            Tile
        new_element
            Tile element field
        """
        TileRepository.update_element(tile=tile, new_element=new_element)
        TileRepository.save(tile)
        cls.update_tile_buffs(tile)
        event = ServerEventData(
            BattleServerEventsEnum.tile_update_element,
            params={
                'tile_id': tile.id,
                'battle_card_id': tile.battle_card_id,
                'new_element': new_element,
            },
            to_opponent_only=True,
        )
        if state.consumer:
            state.consumer.store_event(event)

        return tile
