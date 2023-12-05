class BattlePlayerScriptTypesEnum:
    on_end_turn = 'on_end_turn'
    on_appear = 'before_appear'
    on_disappear = 'before_disappear'


BattlePlayerScriptTypes = (
    (BattlePlayerScriptTypesEnum.on_end_turn, 'on_end_turn'),
    (BattlePlayerScriptTypesEnum.on_appear, 'before_appear'),
    (BattlePlayerScriptTypesEnum.on_disappear, 'before_disappear'),
)
