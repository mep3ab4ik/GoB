class CardTypesEnum:
    serf = 'serf'
    spell = 'spell'
    mystery = 'mystery'


CardTypes = (
    (CardTypesEnum.serf, 'Serf'),
    (CardTypesEnum.spell, 'Spell'),
    (CardTypesEnum.mystery, 'Mystery'),
)


class SpellTypesEnum:
    regular = 'regular'
    target = 'target'


SpellTypes = (
    (SpellTypesEnum.regular, 'Regular'),
    (SpellTypesEnum.target, 'Target'),
)


class SpellTargetingTypesEnum:
    only_opponent_tiles = 'only_opponent_tiles'
    only_opponent_creatures = 'only_opponent_creatures'
    only_opponent_avatar = 'only_opponent_avatar'
    only_opponent_everything = 'only_opponent_everything'  # creatures + avatar

    only_player_tiles = 'only_player_tiles'
    only_player_creatures = 'only_player_creatures'
    only_player_avatar = 'only_player_avatar'
    only_player_everything = 'only_player_everything'  # creatures + avatar

    both_player_tiles = 'both_player_tiles'
    both_player_creatures = 'both_player_creatures'
    both_player_avatars = 'both_player_avatars'
    both_player_everything = 'both_player_everything'  # creatures + avatar


SpellTargetingTypes = (
    (SpellTargetingTypesEnum.only_opponent_tiles, 'Only Opponent Tiles'),
    (SpellTargetingTypesEnum.only_opponent_creatures, 'Only Opponent Creatures'),
    (SpellTargetingTypesEnum.only_opponent_avatar, 'Only Opponent Avatar'),
    (SpellTargetingTypesEnum.only_opponent_everything, 'Only Opponent Everything'),
    (SpellTargetingTypesEnum.only_player_tiles, 'Only Player Tiles'),
    (SpellTargetingTypesEnum.only_player_creatures, 'Only Player Creatures'),
    (SpellTargetingTypesEnum.only_player_avatar, 'Only Player Avatar'),
    (SpellTargetingTypesEnum.only_player_everything, 'Only Player Everything'),
    (SpellTargetingTypesEnum.both_player_tiles, 'Both Player Tiles'),
    (SpellTargetingTypesEnum.both_player_creatures, 'Both Player Creatures'),
    (SpellTargetingTypesEnum.both_player_avatars, 'Both Player Avatars'),
    (SpellTargetingTypesEnum.both_player_everything, 'Both Player Everything'),
)


class CreatureTargetingTypesEnum:
    non_target = 'non_target'
    target = 'target'


CreatureTargetingTypes = (
    (CreatureTargetingTypesEnum.non_target, 'Non-target'),
    (CreatureTargetingTypesEnum.target, 'Target'),
)


class CardElementsEnum:
    neutral = 'neutral'
    water = 'water'
    fire = 'fire'
    earth = 'earth'
    electric = 'electric'


CardElements = (
    (CardElementsEnum.neutral, 'Neutral'),
    (CardElementsEnum.water, 'Water'),
    (CardElementsEnum.fire, 'Fire'),
    (CardElementsEnum.earth, 'Earth'),
    (CardElementsEnum.electric, 'Electric'),
)


class CardRaritiesEnum:
    common = 'common'
    rare = 'rare'
    epic = 'epic'
    legendary = 'legendary'


CardRarities = (
    (CardRaritiesEnum.common, 'Common'),
    (CardRaritiesEnum.rare, 'Rare'),
    (CardRaritiesEnum.epic, 'Epic'),
    (CardRaritiesEnum.legendary, 'Legendary'),
)


class CardEditionsEnum:
    regular = 'regular'
    shiny = 'shiny'


CardEditions = (
    (CardEditionsEnum.regular, 'Regular'),
    (CardEditionsEnum.shiny, 'Shiny'),
)
