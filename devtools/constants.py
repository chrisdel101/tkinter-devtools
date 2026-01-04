from enum import Enum
from typing import Any, Literal, TypedDict
import tkinter as tk


MAX_KEY_WIDTH = 30  # adjust as needed
COMBOBOX_ARROW_OFFSET = 25  # pixels to account for combobox arrow area

class GeometryType(Enum ):
    PACK = "pack"
    GRID = "grid"
    PLACE = "place"

class TreeStateKey(Enum):
    SELECTED_ITEM_WIDGET =  1
    WIDGETS_BY_TREE_INSERT_ID_DICT = 2
    MEM_WIDGET_STORE_BY_PY_MEM_ID= 3

class ListboxInsertNotifyStateKey(Enum):
    SELECTED_INDEX = "selected_index"
    CURRENT_VALUES_STATE = "current_values_state"
    LISTBOX_PAGE_INSERT = "listbox_page_insert_enum"

# name to use to display specific listbox insert within frame
class ListboxPageInsertEnum(Enum):
    ATTRIBUTES = 1
    GEOMETRY = 2

class ActionType(Enum):
    INSERT_LISTBOX_ITEM = "insert_listbox_item"
    INSERT_LISTBOX_ITEMS = "insert_listbox_items"
    HANDLE_SUBTRACT_INDEX = "handle_subtract_index"
    HANDLE_SUBTRACT_SELECTION = "handle_subtract_selection"
    CANCEL_UPDATE_LISTBOX = "cancel_update_listbox"
    UPDATE_TREE_ITEM_TO_PAGE_WIDGET_GRID_CONFIG = "update_tree_item_to_page_widget_grid_config"
    UPDATE_TREE_ITEM_TO_PAGE_WIDGET_PACK_CONFIG = "update_tree_item_to_page_widget_pack_config"
    UPDATE_TREE_ITEM_TO_PAGE_WIDGET_PLACE_CONFIG = "update_tree_item_to_page_widget_place_config"
    UPDATE_TREE_ITEM_TO_PAGE_WIDGET_ATTR_CONFIG = "update_tree_item_to_page_widget_attr_config"
    DELETE_ALL_LISTBOX_ITEMS = "delete_all_listbox_items"
    TOGGLE_GEO_BUTTON_VISIBLE = "toggle_geo_button_visible"

class ConfigValueType(Enum):
    STRING = "str"
    INTEGER = "int"
    BOOLEAN = "boolean"
    FLOAT = "float"
    TUPLE = "tuple"
    LIST = "list"

class ValidGridGeometryAttr(Enum):
    IN_ = "in"
    PADX = "padx"
    PADY = "pady"
    ROWSPAN = "rowspan"
    COLUMNSPAN = "columnspan"
    ROW = "row"
    COLUMN = "column"
    IPADX = "ipadx"
    IPADY = "ipady"
    STICKY = "sticky"

class ValidPlaceGeometryAttr(Enum):
    IN_ = "in"
    X = "x"
    Y = "y"
    RELX = "relx"
    RELY = "rely"
    WIDTH = "width"
    HEIGHT = "height"
    RELWIDTH = "relwidth"
    RELHEIGHT = "relheight"
    ANCHOR = "anchor"
    BORDERMODE = "bordermode"


class ValidPackGeometryAttr(Enum):
    IN = "in" # dupe remove  
    PADX = "padx"
    PADY = "pady"
    EXPAND = "expand"
    FILL = "fill"
    IPADX = "ipadx"
    IPADY = "ipady"
    SIDE = "side"

class AllValidGeometryAttr(Enum):
    GEOMETRY_TYPE = "geometry_type"
    IN = "in"

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

class AliasRename(Enum):
    PARENT_WIDGET = "parent widget" 
    GEOMETRY_TYPE = "geometry type"

class GeometryAttrAddition(Enum):
    ROW_CONFIGURE = "rowconfigure" 
    COLUMN_CONFIGURE = "columnconfigure"

class ComboBoxState(Enum):
    NORMAL = "normal"
    READONLY = "readonly"

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
    listbox_page_insert_enum: ListboxPageInsertEnum

class ListboxInsertManagerState(TypedDict):
    selected_index: int | None
    current_values_state: list[str] | None
    listbox_page_insert_enum: ListboxPageInsertEnum | None

