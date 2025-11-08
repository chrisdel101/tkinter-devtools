from constants import ComboBoxState


OPTIONS = {
    "relief": {
        'values': ["flat","raised","sunken","groove","ridge","solid"],
        'state': ComboBoxState.READONLY.value
    },
    "anchor": {
        'values': ["n","ne","e","se","s","sw","w","nw","center"],
        'state': ComboBoxState.READONLY.value
    },
    "justify": {
        'values': ["left","center","right"],
        'state': ComboBoxState.READONLY.value
    },
    "font": {
        'values': ["Arial","Helvetica","Times New Roman","Courier New","Verdana","Georgia","Comic Sans MS"],
        'state': ComboBoxState.NORMAL.value
    },
    "cursor": {
        'values': ["arrow","circle","clock","cross","dotbox","exchange","fleur","heart,pirate","plus","shuttle","sizing","spider","spraycan","star","target","tcross","trek","watch"],
        'state': ComboBoxState.READONLY.value
    },
    "borderwidth": {
        'values': ["0","1","2","3","4","5","6","7","8","9","10"],
        'state': ComboBoxState.READONLY.value
    },
    "bg":{
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'state': ComboBoxState.NORMAL.value
    },
    "fg": {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'state': ComboBoxState.NORMAL.value
    },
    "highlightthickness": {
        'values': ["0","1","2","3","4","5"],
        'state': ComboBoxState.NORMAL.value
    },
    "highlightbackground": {
        'values': ["white","lightgrey","grey","darkgrey","black","red","green","blue","yellow","cyan","magenta","orange","purple","pink"],
        'state': ComboBoxState.NORMAL.value
    },
    'state': {
        'values': ['active', 'disabled', 'normal'],
        'state': ComboBoxState.READONLY.value
    },
    "text": {
        'values': "",
        'state': ComboBoxState.NORMAL.value
    },
    "padx": {
        'values': "",
        'state': ComboBoxState.NORMAL.value
    },
    "pady": {
        'values': "",
        'state': ComboBoxState.NORMAL.value
    },
}
# set any aliases
OPTIONS['foreground'] = OPTIONS['fg']
OPTIONS['background'] = OPTIONS['bg']