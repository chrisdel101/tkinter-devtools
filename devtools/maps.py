from devtools.constants import CommonConfigAttr, ConfigValueType

OPTIONS = {
    # relief
    CommonConfigAttr.RELIEF.value: {
        'values': ["flat","raised","sunken","groove","ridge","solid"],
        'type': ConfigValueType.STRING.value,
    },
    CommonConfigAttr.ANCHOR.value: {
        'values': ["n","ne","e","se","s","sw","w","nw","center"],
         'type': ConfigValueType.STRING.value,
    },
    CommonConfigAttr.JUSTIFY.value: {
        'values': ["left","center","right"],
        'type': ConfigValueType.STRING.value,
    },
    CommonConfigAttr.FONT.value: {
        'values': ["Arial","Helvetica","Times New Roman","Courier New","Verdana","Georgia","Comic Sans MS"],
        'type': ConfigValueType.STRING.value,
    },
    CommonConfigAttr.CURSOR.value: {
        'values': ["arrow","circle","clock","cross","dotbox","exchange","fleur","heart,pirate","plus","shuttle","sizing","spider","spraycan","star","target","tcross","trek","watch"],
         'type': ConfigValueType.STRING.value,  
    },
    CommonConfigAttr.BORDERWIDTH.value: {
        'values': ["0","1","2","3","4","5","6","7","8","9","10"],
        'type': ConfigValueType.INTEGER.value,
    },
    CommonConfigAttr.BD.value: {
        'values': ["0","1","2","3","4","5","6","7","8","9","10"],
        'type': ConfigValueType.INTEGER.value,
    },
    CommonConfigAttr.BG.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigValueType.STRING.value,
    },
    CommonConfigAttr.FG.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigValueType.STRING.value,   
    },
    CommonConfigAttr.HIGHLIGHTTHICKNESS.value: {
        'values': ["0","1","2","3","4","5"],
        'type': ConfigValueType.INTEGER.value,
    },
    CommonConfigAttr.HIGHLIGHTBACKGROUND.value: {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'type': ConfigValueType.STRING.value,
    },
    CommonConfigAttr.STATE.value: {
        'values': ['active', 'disabled', 'normal'],
        'type': ConfigValueType.STRING.value,
    },
    CommonConfigAttr.TEXT.value: {
        'values': "",
        'type': ConfigValueType.STRING.value,
    },
    CommonConfigAttr.PADX.value: {
        'values': "",
        'type': ConfigValueType.INTEGER.value,
    },
    CommonConfigAttr.PADY.value: {
        'values': "",
        'type': ConfigValueType.INTEGER.value,
    }
}
# set any aliases
OPTIONS['foreground'] = OPTIONS['fg']
OPTIONS['background'] = OPTIONS['bg']
OPTIONS['borderwidth'] = OPTIONS['bd']