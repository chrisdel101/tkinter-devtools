from enum import Enum


MAX_KEY_WIDTH = 30  # adjust as needed

class ConfigValueType(Enum):
    STRING = "str"
    INTEGER = "int"
    BOOLEAN = "boolean"
    FLOAT = "float"
    TUPLE = "tuple"
    LIST = "list"

class ValidConfigAttr(Enum):
    RELIEF = "relief"
    ANCHOR = "anchor"
    JUSTIFY = "justify"
    FONT = "font"
    CURSOR = "cursor"
    BORDERWIDTH = "borderwidth"
    BD = "bd"
    HIGHLIGHTTHICKNESS = "highlightthickness"
    HIGHLIGHTBACKGROUND = "highlightbackground"
    HIGHLIGHTCOLOR = "highlightcolor"  
    STATE = "state"
    TEXT = "text"
    PADX = "padx"
    PADY = "pady"

    BG = "bg"
    FG = "fg"
    BACKGROUND = "background"
    FOREGROUND = "foreground"
    
    WIDTH = "width"
    HEIGHT = "height"

KEYS_TO_REMOVE = ['class']

class ComboBoxState(Enum):
    NORMAL = "normal"
    READONLY = "readonly"

class OptionBoxState(Enum):
    OPEN = "open"
    CLOSED = "closed"
# create used when adding and no val is being input
class ListBoxEntryInputAction(Enum):
    CREATE = "create"
    UPDATE = "update"