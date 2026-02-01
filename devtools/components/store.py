from __future__ import annotations
import logging
import tkinter as tk
from typing import Any

from devtools.components.observable import Action
from devtools.constants import ActionType, ListBoxEntryInputAction, ListboxManagerState, ListboxInsertNotifyStateKey, ListboxPageInsertEnum, TreeState, TreeStateKey
from typing import TYPE_CHECKING

from devtools.decorators import try_except_catcher
from devtools.style import Style

if TYPE_CHECKING:
    # ONLY for type checkers
    from devtools.components.widgets.config_listbox.ConfigListboxManager import ConfigListboxManager


class Store:
    @try_except_catcher
    def __init__(self, root, observable, config):
        self._observable = observable
        # config values
        self.show_unmapped_widgets: bool = config.get("show_unmapped_widgets")
        
        self.block_active_adding: bool = False
        self.existing_combobox_wrappers: list[tk.Widget] | list = []
        self.style = Style(root=root)
        self.selected_combobox: tk.Widget | None = None
        self.devtools_window_in_focus: bool = True
        self.key_combobox_popdown_open: bool = False
        self.value_combobox_popdown_open: bool = False
        self.listbox_entry_input_action:   ListBoxEntryInputAction | None = None
        self.editting_item_index: int | None = None
        self.allow_input_focus_out_logic: bool = True
        self.tree_state: TreeState = {
            TreeStateKey.SELECTED_ITEM_WIDGET.value: None,
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT.value: {},
            TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID.value: {}
        }
        # store the listbox manager inserts
        self.listbox_inserts: dict[ListboxPageInsertEnum, ConfigListboxManager] = {} 
        # listbox being shown in frame 
        self.current_listbox_insert: ConfigListboxManager | None = None
        self.current_listbox_insert_internal_state: ListboxManagerState = {
            ListboxPageInsertEnum.OPTIONS: {
                ListboxInsertNotifyStateKey.SELECTED_INDEX.value: None,
                ListboxInsertNotifyStateKey.CURRENT_VALUES_STATE.value: None,
                ListboxInsertNotifyStateKey.LISTBOX_PAGE_INSERT.value: ListboxPageInsertEnum.OPTIONS
            },
            ListboxPageInsertEnum.GEOMETRY: {
                ListboxInsertNotifyStateKey.SELECTED_INDEX.value: None,
                ListboxInsertNotifyStateKey.CURRENT_VALUES_STATE.value: None,
                ListboxInsertNotifyStateKey.LISTBOX_PAGE_INSERT.value: ListboxPageInsertEnum.GEOMETRY
            }
        }
        self.hidden_widgets = None
        self.show_geometry_button = tk.BooleanVar()
        self.show_geometry_button.trace_add('write', self.on_geometry_var_change)
        self.show_geometry_button.set(False)
        
    def on_geometry_var_change(self, *_):
        self._observable.notify_observers(Action(
            type=ActionType.TOGGLE_GEO_BUTTON_VISIBLE,
        data=self.show_geometry_button.get()
        ))

    @try_except_catcher
    def tree_state_get(self, enum_key:  TreeStateKey):
        return self.tree_state.get(enum_key.value)

    # handles tracking store state or tree - i.e. selected item
    @try_except_catcher
    def tree_state_set(self, enum_key: TreeStateKey, state_to_set: Any):
        self.tree_state[enum_key.value] = state_to_set

    # get single value from listbox manager state
    @try_except_catcher
    def listbox_manager_state_get_value(self, enum_key: ListboxInsertNotifyStateKey, page_insert_override: ListboxPageInsertEnum | None = None):
        # get current insert key ListboxPageInsertEnum or manual param
        page_insert = page_insert_override if page_insert_override else self.current_listbox_insert._listbox_page_insert_enum
        return self.current_listbox_insert_internal_state.get(page_insert).get(enum_key.value)

    # key for name current_listbox_insert_internal_state, value is dict of values
    # - updates whole dict whenever a change occurs
    @try_except_catcher
    def listbox_manager_state_set(self, enum_key: ListboxInsertNotifyStateKey, state_to_set: Any, page_insert_override: ListboxPageInsertEnum | None = None):
        # use current page insert or override param - get listbox by enum key
        current_target_listbox = self.listbox_inserts.get(page_insert_override) if page_insert_override else self.current_listbox_insert
        current_target_listbox_enum = current_target_listbox._listbox_page_insert_enum if current_target_listbox else None
        
        match current_target_listbox_enum:
            # set one of the ListboxInsertNotifyStateKey values by ListboxPageInsertEnum
            case ListboxPageInsertEnum.OPTIONS:
                self.current_listbox_insert_internal_state[
                    ListboxPageInsertEnum.OPTIONS][enum_key.value] = state_to_set
                self._observable.notify_observers(
                    Action(type=ActionType.INSERT_LISTBOX_ITEMS,
                           data=self.current_listbox_insert_internal_state[ListboxPageInsertEnum.OPTIONS].get(enum_key.value),
                           target=current_target_listbox)
                )
            case ListboxPageInsertEnum.GEOMETRY:
                self.current_listbox_insert_internal_state[
                    ListboxPageInsertEnum.GEOMETRY][enum_key.value] = state_to_set
                self._observable.notify_observers(
                    Action(type=ActionType.INSERT_LISTBOX_ITEMS,
                        data=self.current_listbox_insert_internal_state[ListboxPageInsertEnum.GEOMETRY].get(enum_key.value),
                        target=current_target_listbox)
                    )

    @property
    def allow_input_focus_out_logic(self):
        return self._allow_input_focus_out_logic

    @allow_input_focus_out_logic.setter
    def allow_input_focus_out_logic(self, value):
        logging.trace(f'store setter - set allow_input_focus_out_logic - {value}')
        self._allow_input_focus_out_logic = value

    @property
    def hidden_widgets(self):
        return self._hidden_widgets

    @hidden_widgets.setter
    def hidden_widgets(self, value):
        self._hidden_widgets = value

    @property
    def devtools_window_in_focus(self):
        return self._devtools_window_in_focus

    @devtools_window_in_focus.setter
    def devtools_window_in_focus(self, value):
        self._devtools_window_in_focus = value

    @property
    def show_unmapped_widgets(self):
        return self._show_unmapped_widgets

    @show_unmapped_widgets.setter
    def show_unmapped_widgets(self, value):
        self._show_unmapped_widgets = value

    @property
    def current_listbox_insert(self):
        return self._current_listbox_insert

    @current_listbox_insert.setter
    def current_listbox_insert(self, value):
        self._current_listbox_insert = value

    @property
    def listbox_inserts(self):
        return self._listbox_inserts

    @listbox_inserts.setter
    def listbox_inserts(self, value):
        self._listbox_inserts = value

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
