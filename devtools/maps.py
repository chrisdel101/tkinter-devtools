from devtools.constants import ActionType, AliasRename, ValidConfigAttr, ConfigOptionValueTypeEnum, AllValidGeometryAttr
from devtools.schemas import AttributeMapSetting

ATTR_CONFIG_SETTING_VALUES = {

ATTR_CONFIG_SETTING_VALUES: dict[dict[str,AttributeMapSetting]] = {
    # relief
    ValidConfigAttr.RELIEF.value: {
        'values': ["flat","raised","sunken","groove","ridge","solid"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ValidConfigAttr.ANCHOR.value: {
        'values': ["n","ne","e","se","s","sw","w","nw","center"],
         'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ValidConfigAttr.JUSTIFY.value: {
        'values': ["left","center","right"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ValidConfigAttr.FONT.value: {
        'values': ["Arial","Helvetica","Times New Roman","Courier New","Verdana","Georgia","Comic Sans MS"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ValidConfigAttr.CURSOR.value: {
        'values': ["arrow","circle","clock","cross","dotbox","exchange","fleur","heart,pirate","plus","shuttle","sizing","spider","spraycan","star","target","tcross","trek","watch"],
         'type': ConfigOptionValueTypeEnum.STRING.value,  
    },
    ValidConfigAttr.BACKGROUND.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ValidConfigAttr.FOREGROUND.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigOptionValueTypeEnum.STRING.value,   
    },
    ValidConfigAttr.HIGHLIGHTBACKGROUND.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ValidConfigAttr.STATE.value: {
        'values': ['active', 'disabled', 'normal'],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ValidConfigAttr.TEXT.value: {
        'values': "",
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ValidConfigAttr.BORDERWIDTH.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    ValidConfigAttr.HIGHLIGHTTHICKNESS.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    ValidConfigAttr.PADX.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    ValidConfigAttr.PADY.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    ValidConfigAttr.WIDTH.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    ValidConfigAttr.HEIGHT.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    }
}

CONFIG_ALIASES = {
    AllValidGeometryAttr.GEOMETRY_TYPE.value: AliasRename.GEOMETRY_TYPE.value,
    AllValidGeometryAttr.IN.value: AliasRename.PARENT_WIDGET.value,
    ValidConfigAttr.BD.value: ValidConfigAttr.BORDERWIDTH.value,
    ValidConfigAttr.BD.value: ValidConfigAttr.BORDERWIDTH.value,
    ValidConfigAttr.BG.value: ValidConfigAttr.BACKGROUND.value,
    ValidConfigAttr.FG.value: ValidConfigAttr.FOREGROUND.value,
}

# uses action type enums to make to func with same name
ACTION_REGISTRY = {a.name: a.value for a in ActionType}