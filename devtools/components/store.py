import logging
import tkinter as tk
from typing import Any, OrderedDict, TypedDict

from devtools.components.observable import Action
from devtools.constants import ActionType, ListboxManagerStateKey, TreeStateKey

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
    current_values_state: OrderedDict[str, str] | None

class Store:
    """A simple store to hold key-value pairs."""
    def __init__(self, observable):
        self._observable = observable
        self.block_active_adding: bool = False 
        self.existing_combobox_wrappers: list[tk.Widget] | list = []
        self.selected_combobox: tk.Widget | None = None
        self.devtools_window_in_focus: bool = True
        self.key_combobox_popdown_open: bool = False
        self.value_combobox_popdown_open: bool = False
        self.editting_item_index:int | None = None 
        self.tree_state: TreeState = {
            TreeStateKey.SELECTED_ITEM.value: None,
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT.value: {},
            TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID.value: {}
        }  
        self.listbox_manager_state: ListboxManagerState = {
            ListboxManagerStateKey.SELECTED_INDEX.value: None,
            ListboxManagerStateKey.CURRENT_VALUES_STATE.value: None
        }  

    def tree_state_get(self, enum_key:  TreeStateKey):
        return self.tree_state.get(enum_key.value)
    
    # handles tracking store state or tree - i.e. selected item
    def tree_state_set(self, enum_key: TreeStateKey, state_to_set: Any):
        self.tree_state[enum_key.value] = state_to_set
        
    # get single value from listbox manager state
    def listbox_manager_state_get_value(self, enum_key: ListboxManagerStateKey):
        return self.listbox_manager_state.get(enum_key.value)
    
    # key for name listbox_manager_state, value is dict of values
    # - updates whole dict whenever a change occurs
    def listbox_manager_state_set(self, enum_key: ListboxManagerStateKey, state_to_set: Any):
        self.listbox_manager_state[enum_key.value] = state_to_set 
        self._observable.notify_observers(
            Action(type=ActionType.INSERT_ALL_LISTBOX.name,
            data=self.listbox_manager_state.get(enum_key.value))
        )

    @property
    def editting_item_index(self):
        return self._editting_item_index
    
    @editting_item_index.setter
    def editting_item_index(self, value):
        self._editting_item_index = value 

    @property
    def value_combobox_popdown_open(self):
        return self._value_combobox_popdown_open
    
    @value_combobox_popdown_open.setter
    def value_combobox_popdown_open(self, value):
        self._value_combobox_popdown_open = value 

    @property
    def key_combobox_popdown_open(self):
        return self._key_combobox_popdown_open
    
    @key_combobox_popdown_open.setter
    def key_combobox_popdown_open(self, value):
        self._key_combobox_popdown_open = value 

    @property
    def block_active_adding(self):
        return self._block_active_adding
    
    @block_active_adding.setter
    def block_active_adding(self, value):
        # logging.debug(f'SETTING block_active_adding TO {value}')
        self._block_active_adding = value 

    # remove any selected comboboxs or wrappers in state
    def focus_out_untrack_combobox_wrappers(self):
        if self.existing_combobox_wrappers:
            logging.debug(f"Combobox removed from state.")
            self.existing_combobox_wrappers = []

    # track frame and inner combobox - when window focus out - cancel all comboboxes - called in build_key_option_box
    def track_combobox_wrappers(self, widget):
    # - combobox widget cannot focusout itself
        try:
            if widget.winfo_name() == "!combobox":
                # store combobox i
                logging.debug(f"Combobox selected1 NO LOGIC: {widget.get()}")
            else:    
                for child in widget.winfo_children():
                    if child.winfo_name() == "!combobox":
                        # store wrapper if child is combobox
                        self.existing_combobox_wrappers.append(widget)
                        self.selected_combobox = child
                        logging.debug(f"Combobox added to state.")
                        # logging.debug(f"Combobox state added: {widget}")
                        break
              
        except Exception as e:
            logging.error(f"Error tracking combobox selection: {e}", exc_info=True)

