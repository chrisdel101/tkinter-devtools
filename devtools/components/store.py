from __future__ import annotations
import logging
import tkinter as tk
from typing import Any

from devtools.components.observable import Action
# from devtools.components.widgets.config_listbox.ConfigListboxManager import ConfigListboxManager
from devtools.constants import ActionType, ListBoxEntryInputAction, ListboxManagerState, ListboxManagerStateKey, ListboxPageInsertType, TreeState, TreeStateKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # ONLY for type checkers
    from devtools.components.widgets.config_listbox.ConfigListboxManager import ConfigListboxManager  

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
        self.listbox_entry_input_action:   ListBoxEntryInputAction | None  = None
        self.editting_item_index:int | None = None 
        self.allow_input_focus_out_logic: bool = True
        self.tree_state: TreeState = {
            TreeStateKey.SELECTED_ITEM.value: None,
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT.value: {},
            TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID.value: {}
        }  
        self.listbox_page_insert_type: ListboxPageInsertType = ListboxPageInsertType.ATTRIBUTES
        self.current_listbox_insert: ConfigListboxManager | None = None
        self.current_listbox_insert_internal_state: ListboxManagerState = {
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
        return self.current_listbox_insert_internal_state.get(enum_key.value)
    
    # key for name current_listbox_insert_internal_state, value is dict of values
    # - updates whole dict whenever a change occurs
    def listbox_manager_state_set(self, enum_key: ListboxManagerStateKey, state_to_set: Any):
        self.current_listbox_insert_internal_state[enum_key.value] = state_to_set 
        self._observable.notify_observers(
            Action(type=ActionType.INSERT_LISTBOX_ITEMS.name,
            data=self.current_listbox_insert_internal_state.get(enum_key.value))
        )

    @property
    def allow_input_focus_out_logic(self):
        return self._allow_input_focus_out_logic
    
    @allow_input_focus_out_logic.setter
    def allow_input_focus_out_logic(self, value):
        logging.debug(f'SETTING allow_input_focus_out_logic TO {value}')
        self._allow_input_focus_out_logic = value

    @property
    def devtools_window_in_focus(self):
        return self._devtools_window_in_focus
    
    @devtools_window_in_focus.setter
    def devtools_window_in_focus(self, value):
        self._devtools_window_in_focus = value
        
    @property
    def listbox_page_insert_type(self):
        return self._listbox_page_insert_type
    
    @listbox_page_insert_type.setter
    def listbox_page_insert_type(self, value):
        self._listbox_page_insert_type = value

    @property
    def editting_item_index(self):
        return self._editting_item_index
    
    @editting_item_index.setter
    def editting_item_index(self, value):
        self._editting_item_index = value 

    @property
    def listbox_entry_input_action(self):
        return self._listbox_entry_input_action
    
    @listbox_entry_input_action.setter
    def listbox_entry_input_action(self, value):
        self._listbox_entry_input_action = value 
    
    def add_existing_store_wrapper(self, wrapper: tk.Widget):
        self.existing_combobox_wrappers.append(wrapper)
    
    def remove_existing_store_wrappers(self):
        self.existing_combobox_wrappers = []

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

