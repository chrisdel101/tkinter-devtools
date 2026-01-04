from devtools.constants import ActionType, AliasRename, ValidConfigAttr, ConfigValueType, AllValidGeometryAttr

CONFIG_SETTING_VALUES = {
    # relief
    ValidConfigAttr.RELIEF.value: {
        'values': ["flat","raised","sunken","groove","ridge","solid"],
        'type': ConfigValueType.STRING.value,
    },
    ValidConfigAttr.ANCHOR.value: {
        'values': ["n","ne","e","se","s","sw","w","nw","center"],
         'type': ConfigValueType.STRING.value,
    },
    ValidConfigAttr.JUSTIFY.value: {
        'values': ["left","center","right"],
        'type': ConfigValueType.STRING.value,
    },
    ValidConfigAttr.FONT.value: {
        'values': ["Arial","Helvetica","Times New Roman","Courier New","Verdana","Georgia","Comic Sans MS"],
        'type': ConfigValueType.STRING.value,
    },
    ValidConfigAttr.CURSOR.value: {
        'values': ["arrow","circle","clock","cross","dotbox","exchange","fleur","heart,pirate","plus","shuttle","sizing","spider","spraycan","star","target","tcross","trek","watch"],
         'type': ConfigValueType.STRING.value,  
    },
    ValidConfigAttr.BORDERWIDTH.value: {
        'values': ["0","1","2","3","4","5","6","7","8","9","10"],
        'type': ConfigValueType.INTEGER.value,
    },
    ValidConfigAttr.BACKGROUND.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigValueType.STRING.value,
    },
    ValidConfigAttr.FOREGROUND.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigValueType.STRING.value,   
    },
    ValidConfigAttr.HIGHLIGHTTHICKNESS.value: {
        'values': ["0","1","2","3","4","5"],
        'type': ConfigValueType.INTEGER.value,
    },
    ValidConfigAttr.HIGHLIGHTBACKGROUND.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigValueType.STRING.value,
    },
    ValidConfigAttr.STATE.value: {
        'values': ['active', 'disabled', 'normal'],
        'type': ConfigValueType.STRING.value,
    },
    ValidConfigAttr.TEXT.value: {
        'values': "",
        'type': ConfigValueType.STRING.value,
    },
    ValidConfigAttr.PADX.value: {
        'values': "",
        'type': ConfigValueType.INTEGER.value,
    },
    ValidConfigAttr.PADY.value: {
        'values': "",
        'type': ConfigValueType.INTEGER.value,
    },
    ValidConfigAttr.WIDTH.value: {
        'values': "",
        'type': ConfigValueType.INTEGER.value,
    },
    ValidConfigAttr.HEIGHT.value: {
        'values': "",
        'type': ConfigValueType.INTEGER.value,
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