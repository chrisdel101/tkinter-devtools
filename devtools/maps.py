from devtools.constants import ActionType, AliasRename, ConfigOptionName, ConfigOptionValueTypeEnum, CommonGeometryOption
from devtools.schemas import ConfigOptionMapSetting

ATTR_CONFIG_SETTING_VALUES = {


CONFIG_OPTION_SETTINGS: dict[dict[str,ConfigOptionMapSetting]] = {
    # relief
    ConfigOptionName.RELIEF.value: {
        'values': ["flat","raised","sunken","groove","ridge","solid"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ConfigOptionName.ANCHOR.value: {
        'values': ["n","ne","e","se","s","sw","w","nw","center"],
         'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ConfigOptionName.JUSTIFY.value: {
        'values': ["left","center","right"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ConfigOptionName.FONT.value: {
        'values': ["Arial","Helvetica","Times New Roman","Courier New","Verdana","Georgia","Comic Sans MS"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ConfigOptionName.CURSOR.value: {
        'values': ["arrow","circle","clock","cross","dotbox","exchange","fleur","heart,pirate","plus","shuttle","sizing","spider","spraycan","star","target","tcross","trek","watch"],
         'type': ConfigOptionValueTypeEnum.STRING.value,  
    },
    ConfigOptionName.BACKGROUND.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ConfigOptionName.FOREGROUND.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigOptionValueTypeEnum.STRING.value,   
    },
    ConfigOptionName.HIGHLIGHTBACKGROUND.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ConfigOptionName.STATE.value: {
        'values': ['active', 'disabled', 'normal'],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ConfigOptionName.TEXT.value: {
        'values': "",
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    ConfigOptionName.BORDERWIDTH.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    ConfigOptionName.HIGHLIGHTTHICKNESS.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    ConfigOptionName.PADX.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    ConfigOptionName.PADY.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    ConfigOptionName.WIDTH.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    ConfigOptionName.HEIGHT.value: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    }
}

CONFIG_ALIASES = {
    CommonGeometryOption.GEOMETRY_TYPE.value: AliasRename.GEOMETRY_TYPE.value,
    CommonGeometryOption.IN.value: AliasRename.PARENT_WIDGET.value,
    ConfigOptionName.BD.value: ConfigOptionName.BORDERWIDTH.value,
    ConfigOptionName.BD.value: ConfigOptionName.BORDERWIDTH.value,
    ConfigOptionName.BG.value: ConfigOptionName.BACKGROUND.value,
    ConfigOptionName.FG.value: ConfigOptionName.FOREGROUND.value,
}

# uses action type enums to make to func with same name
ACTION_REGISTRY = {a.name: a.value for a in ActionType}