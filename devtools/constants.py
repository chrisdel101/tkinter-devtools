from enum import Enum, auto
import tkinter as tk
from typing import Any, NotRequired, TypedDict

DEVTOOLS_TOP_LEVEL_NAME = "tk_devtools_window"
IS_DEVTOOLS_SENTINEL = "IS_DEVTOOLS_SENTINEL"  # attach to identify if parent widget is devtools window
COMBOBOX_ARROW_OFFSET = 25  # pixels to account for combobox arrow area

# define log levels by value
class CustomLogLevel(Enum):
    TRACE = 8
    BASE_TRACE = 3
    LOW_TRACE = 5
# namespaces are logged when enabled
class LogNameSpace(Enum):
    # namespaces
    COMBOBOX_KEY = auto()

class GeometryType(Enum):
    PACK = "pack"
    GRID = "grid"
    PLACE = "place"
    # is for the tk widget
    WM = "wm"
    # items inside a canvas not canvas itself
    CANVAS = "canvas"
    # means exists but is not displayed
    UNMAPPED = "" 
    # for inside a text widget
    TEXT = "text"
    PANED_WINDOW = "paned_window"

class TreeStateKey(Enum):
    SELECTED_ITEM_WIDGET =  1
    WIDGETS_BY_TREE_INSERT_ID_DICT = 2
    MEM_WIDGET_STORE_BY_PY_MEM_ID= 3

class ListboxTemplateNotifyStateKey(Enum):
    SELECTED_INDEX = "selected_index"
    ALL_WIDGET_POSSIBLE_KEYS = "all_widget_possible_keys"
    CURRENT_VALUES_STATE = "current_values_state"
    LISTBOX_PAGE_TEMPLATE = "listbox_page_template_enum"

# name to use to display specific listbox template within frame
class ListboxPageTemplateEnum(Enum):
    OPTIONS = 1 # for widget resource options
    GEOMETRY = 2 # for widget geometry settings

class ActionType(Enum):
    LOAD_TEMPLATE_VALUE_STATE = "load_template_value_state"
    INSERT_LISTBOX_ITEM = "insert_listbox_item"
    INSERT_LISTBOX_ITEMS = "insert_listbox_items"
    HANDLE_SUBTRACT_INDEX = "handle_subtract_index"
    HANDLE_SUBTRACT_SELECTION = "handle_subtract_selection"
    CANCEL_UPDATE_LISTBOX = "cancel_update_listbox"
    UPDATE_TREE_ITEM_TO_PAGE_WIDGET_GRID_CONFIG = "update_tree_item_to_page_widget_grid_config"
    UPDATE_TREE_ITEM_TO_PAGE_WIDGET_PACK_CONFIG = "update_tree_item_to_page_widget_pack_config"
    UPDATE_TREE_ITEM_TO_PAGE_WIDGET_PLACE_CONFIG = "update_tree_item_to_page_widget_place_config"
    UPDATE_TREE_ITEM_TO_PAGE_WIDGET_OPTION_CONFIG = "update_tree_item_to_page_widget_option_config"
    DELETE_ALL_LISTBOX_ITEMS = "delete_all_listbox_items"
    TOGGLE_GEO_BUTTON_VISIBLE = "toggle_geo_button_visible"
    TOGGLE_ROW_SHIFT = "toggle_row_shift"
    SHOW_RIGHT_WINDOW_ERROR = "show_right_window_error"

class ConfigOptionValueTypeEnum(Enum):
    STRING = str
    INTEGER = int
    BOOLEAN = bool
    FLOAT = float
    TUPLE = tuple
    LIST = list

class CommonGeometryOption:
    GEOMETRY_TYPE = "geometry_type"
    VISIBILITY = "visibility"
    
# Add any new geometry options to these clases
class GridGeometryOption(CommonGeometryOption):
    PADX = "padx"
    PADY = "pady"
    ROWSPAN = "rowspan"
    COLUMNSPAN = "columnspan"
    ROW = "row"
    COLUMN = "column"
    IPADX = "ipadx"
    IPADY = "ipady"
    STICKY = "sticky"

class PlaceGeometryOption(CommonGeometryOption):
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

class PackGeometryOptionName(CommonGeometryOption):
    AFTER = "after"
    BEFORE = "before"
    PADX = "padx"
    PADY = "pady"
    EXPAND = "expand"
    FILL = "fill"
    IPADX = "ipadx"
    IPADY = "ipady"
    SIDE = "side"
    ANCHOR = "anchor"
    
class ConfigOptionKeyName(Enum):
    ACTIVEBACKGROUND = "activebackground"
    ACTIVEFOREGROUND = "activeforeground"
    ANCHOR = "anchor"
    BACKGROUND = "background"
    BITMAP = "bitmap"
    BORDERWIDTH = "borderwidth"
    CURSOR = "cursor"
    DISABLEDFOREGROUND = "disabledforeground"
    FONT = "font"
    FOREGROUND = "foreground"
    HEIGHT = "height"
    HIGHLIGHTBACKGROUND = "highlightbackground"
    HIGHLIGHTCOLOR = "highlightcolor"  
    HIGHLIGHTTHICKNESS = "highlightthickness"
    IMAGE= "image"
    JUSTIFY = "justify"
    PADX = "padx"
    PADY = "pady"
    RELIEF = "relief"
    STATE = "state"
    TEXT = "text"
    WIDTH = "width"

    BD = "bd"
    BG = "bg"
    FG = "fg"
    

class AliasRename(Enum):
    PARENT_WIDGET = "parent widget" 
    GEOMETRY_TYPE = "geometry type"

class GeometryOptionAddition(Enum):
    ROW_CONFIGURE = "rowconfigure" 
    COLUMN_CONFIGURE = "columnconfigure"

class ListboxItemState(Enum):
    DEFAULT = auto()
    READ_ONLY = auto()

# create used when adding and no val is being input
class ListBoxEntryInputAction(Enum):
    CREATE = 1
    UPDATE = 2

class ListboxItemPair(TypedDict):
    key: str
    value: str

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
    listbox_page_template_enum: ListboxPageTemplateEnum

class ListboxInsertManagerState(TypedDict):
    selected_index: int | None
    current_values_state: list[str] | None
    listbox_page_template_enum: ListboxPageTemplateEnum | None

# entry inside CONFIG_OPTION_SETTINGS
class ConfigOptionMapSetting(TypedDict):
    values: str
    type: str | int | bool | tuple | list
    state: NotRequired[ListboxItemState]