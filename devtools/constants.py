from enum import Enum
from typing import Any, TypedDict
import tkinter as tk


MAX_KEY_WIDTH = 30  # adjust as needed
COMBOBOX_ARROW_OFFSET = 25  # pixels to account for combobox arrow area

class TreeStateKey(Enum):
    SELECTED_ITEM =  "selected_item"
    WIDGETS_BY_TREE_INSERT_ID_DICT = "widgets_by_tree_insert_id"
    MEM_WIDGET_STORE_BY_PY_MEM_ID= "mem_widget_store_by_py_mem_id"

class ListboxManagerStateKey(Enum):
    SELECTED_INDEX = "selected_index"
    CURRENT_VALUES_STATE = "current_values_state"
    LISTBOX_PAGE_INSERT_TYPE = "listbox_page_insert_type"

# use to display specific listbox in frame
class ListboxPageInsertType(Enum):
    ATTRIBUTES = 1
    GEOMETRY = 2

class ActionType(Enum):
    INSERT_LISTBOX_ITEM = "insert_listbox_item"
    INSERT_LISTBOX_ITEMS = "insert_listbox_items"
    HANDLE_SUBTRACT_INDEX = "handle_subtract_index"
    HANDLE_SUBTRACT_SELECTION = "handle_subtract_selection"
    CANCEL_UPDATE_LISTBOX = "cancel_update_listbox"
    UPDATE_TREE_ITEM_TO_PAGE_WIDGET = "update_tree_item_to_page_widget"
    DELETE_ALL_LISTBOX_ITEMS = "delete_all_listbox_items"

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
    CREATE = 1
    UPDATE = 2

class MemIdWidgetStore(TypedDict):
    tree_id: str
    # is the active widget
    widget: tk.Widget
    widget_config_init_frozen: dict[str, Any]

class TreeState(TypedDict):
    # widgets tracked using tree ids 'I001'
    selected_widget_item: tk.Widget | None
    # use Treeview.insert id like 'I001'
    widgets_by_tree_insert_id: dict[str, tk.Widget] = {}
    # store mem id() like {4579038880: {tree_id:'I002', widget:tk.Widget}}
    mem_widget_store_by_py_mem_id: dict[int, MemIdWidgetStore] = {}

class ListboxManagerState(TypedDict):
    # widgets tracked using tree ids 'I001'
    selected_index: int| None
    current_values_state: dict[str, str] | None
    listbox_page_insert_type: ListboxPageInsertType | None
    