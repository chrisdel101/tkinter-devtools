from devtools.constants import ActionType, AliasRename, ConfigOptionName, ConfigOptionValueTypeEnum, CommonGeometryOption, GeometryType, GridGeometryOption, ListboxItemState, PackGeometryOptionName, PlaceGeometryOption
from devtools.constants import ConfigOptionMapSetting

PACK_GEOMETRY_CONFIG_SETTING_VALUES: dict[str, ConfigOptionMapSetting] = {
    PackGeometryOptionName.GEOMETRY_TYPE: {
        'values': GeometryType.PACK.value,
        'type': ConfigOptionValueTypeEnum.STRING.value,
        'state': ListboxItemState.READ_ONLY,
    },
    PackGeometryOptionName.PADX: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    PackGeometryOptionName.PADX: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    PackGeometryOptionName.PADY: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    PackGeometryOptionName.IPADX: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    PackGeometryOptionName.IPADY: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    PackGeometryOptionName.FILL: {
        'values': ['none', 'x', 'y', 'both'],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    PackGeometryOptionName.EXPAND: {
        'values': [True, False],
        'type': ConfigOptionValueTypeEnum.BOOLEAN.value,
    },
    PackGeometryOptionName.ANCHOR: {
        'values': ["n","ne","e","se","s","sw","w","nw","center"],
        'type': ConfigOptionValueTypeEnum.BOOLEAN.value,
    },
    PackGeometryOptionName.SIDE: {
        'values': ['top', 'bottom', 'left', 'right'],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    # readonly options
    # PackGeometryOptionName.IN: {
    #     'values': None,
    #     'type': ConfigOptionValueTypeEnum.STRING.value,
    # }
}
GRID_GEOMETRY_CONFIG_SETTING_VALUES: dict[str, ConfigOptionMapSetting] = {
    GridGeometryOption.GEOMETRY_TYPE: {
        'values': GeometryType.GRID.value,
        'type': ConfigOptionValueTypeEnum.STRING.value,
        'state': ListboxItemState.READ_ONLY,

    },
    GridGeometryOption.IPADX: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    GridGeometryOption.IPADY: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
     GridGeometryOption.PADX: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    GridGeometryOption.PADY: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    GridGeometryOption.COLUMNSPAN: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    GridGeometryOption.ROWSPAN: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    GridGeometryOption.COLUMN: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    GridGeometryOption.ROW: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    GridGeometryOption.STICKY: {
        'values': ["","N","S","E","W","NS","EW","NE","NW","SE","SW","NSE","NSW","NEW","SEW","NSEW"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    # # readonly options
    # PackGeometryOptionName.IN: {
    #     'values': None,
    #     'type': ConfigOptionValueTypeEnum.STRING.value,
    # }
}
PLACE_GEOMETRY_CONFIG_SETTING_VALUES: dict[str, ConfigOptionMapSetting] = {
    PlaceGeometryOption.GEOMETRY_TYPE: {
        'values': GeometryType.PLACE.value,
        'type': ConfigOptionValueTypeEnum.STRING.value,
        'state': ListboxItemState.READ_ONLY,
    },
    PlaceGeometryOption.X: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    PlaceGeometryOption.Y: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    PlaceGeometryOption.RELX: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.FLOAT.value,
    },
    PlaceGeometryOption.RELY: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.FLOAT.value,
    },
    PlaceGeometryOption.WIDTH: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    PlaceGeometryOption.HEIGHT: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.INTEGER.value,
    },
    PlaceGeometryOption.RELWIDTH: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.FLOAT.value,
    },
    PlaceGeometryOption.RELHEIGHT: {
        'values': None,
        'type': ConfigOptionValueTypeEnum.FLOAT.value,
    },
    PlaceGeometryOption.ANCHOR: {
        'values': ["n","ne","e","se","s","sw","w","nw","center"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    PlaceGeometryOption.BORDERMODE: {
        'values': ["inside","outside"],
        'type': ConfigOptionValueTypeEnum.STRING.value,
    },
    # # readonly options
    # CommonGeometryOption.IN: {
    #     'values': None,
    #     'type': ConfigOptionValueTypeEnum.STRING.value,
    # }
}

CONFIG_OPTION_SETTINGS: dict[str, ConfigOptionMapSetting] = {
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
    CommonGeometryOption.GEOMETRY_TYPE: AliasRename.GEOMETRY_TYPE.value,
    ConfigOptionName.BD.value: ConfigOptionName.BORDERWIDTH.value,
    ConfigOptionName.BD.value: ConfigOptionName.BORDERWIDTH.value,
    ConfigOptionName.BG.value: ConfigOptionName.BACKGROUND.value,
    ConfigOptionName.FG.value: ConfigOptionName.FOREGROUND.value,
}

# uses action type enums to make to func with same name
ACTION_REGISTRY = {a.name: a.value for a in ActionType}
GEOMETRY_TYPES = [e.value for e in GeometryType]