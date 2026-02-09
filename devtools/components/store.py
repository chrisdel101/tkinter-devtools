from __future__ import annotations
import logging
import tkinter as tk
from typing import Any

from devtools.components.observable import Action
from devtools.constants import ActionType, ListBoxEntryInputAction, ListboxManagerState, ListboxTemplateNotifyStateKey, ListboxPageTemplateEnum, TreeState, TreeStateKey
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
        # map all config values to store
        [setattr(self, k, v) for k, v in config.items()]
        # state state values
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
        # store the listbox manager templates
        self.listbox_templates: dict[ListboxPageTemplateEnum,
                                   ConfigListboxManager] = {}
        # which template is inserted as shown in the listbox
        self.current_listbox_template: ConfigListboxManager | None = None
        # store the state of the active template in the listbox 
        self.current_listbox_template_internal_state: ListboxManagerState = {
            ListboxPageTemplateEnum.OPTIONS: {
                ListboxTemplateNotifyStateKey.SELECTED_INDEX.value: None,
                ListboxTemplateNotifyStateKey.CURRENT_VALUES_STATE.value: None,
                ListboxTemplateNotifyStateKey.LISTBOX_PAGE_TEMPLATE.value: ListboxPageTemplateEnum.OPTIONS
            },
            ListboxPageTemplateEnum.GEOMETRY: {
                ListboxTemplateNotifyStateKey.SELECTED_INDEX.value: None,
                ListboxTemplateNotifyStateKey.CURRENT_VALUES_STATE.value: None,
                ListboxTemplateNotifyStateKey.LISTBOX_PAGE_TEMPLATE.value: ListboxPageTemplateEnum.GEOMETRY
            }
        }
        self.hidden_widgets = {}
        self.show_geometry_button = False

    @try_except_catcher
    def tree_state_get(self, enum_key:  TreeStateKey):
        return self.tree_state.get(enum_key.value)

    # handles tracking store state or tree - i.e. selected item
    @try_except_catcher
    def tree_state_set(self, enum_key: TreeStateKey, state_to_set: Any):
        self.tree_state[enum_key.value] = state_to_set

    # get single value from listbox manager state
    @try_except_catcher
    def listbox_manager_state_get_value(self, enum_key: ListboxTemplateNotifyStateKey, page_insert_override: ListboxPageTemplateEnum | None = None):
        # get current insert key ListboxPageTemplateEnum or manual param
        page_insert = page_insert_override if page_insert_override else self.current_listbox_template._listbox_page_insert_enum
        return self.current_listbox_template_internal_state.get(page_insert).get(enum_key.value)

    # key for name current_listbox_template_internal_state, value is dict of values
    # - updates whole dict whenever a change occurs
    @try_except_catcher
    def listbox_manager_state_set(self, enum_key: ListboxTemplateNotifyStateKey, state_to_set: Any, page_insert_override: ListboxPageTemplateEnum | None = None):
        # use current page insert or override param - get listbox by enum key
        current_target_listbox = self.listbox_templates.get(page_insert_override) if page_insert_override else self.current_listbox_template
        current_target_listbox_enum = current_target_listbox._listbox_page_insert_enum if current_target_listbox else None
        
        match current_target_listbox_enum:
            # set one of the ListboxTemplateNotifyStateKey values by ListboxPageTemplateEnum
            case ListboxPageTemplateEnum.OPTIONS:
                self.current_listbox_template_internal_state[
                    ListboxPageTemplateEnum.OPTIONS][enum_key.value] = state_to_set
                self._observable.notify_observers(
                    Action(type=ActionType.INSERT_LISTBOX_ITEMS,
                           data=self.current_listbox_template_internal_state[ListboxPageTemplateEnum.OPTIONS].get(enum_key.value),
                           target=current_target_listbox)
                )
            case ListboxPageTemplateEnum.GEOMETRY:
                self.current_listbox_template_internal_state[
                    ListboxPageTemplateEnum.GEOMETRY][enum_key.value] = state_to_set
                self._observable.notify_observers(
                    Action(type=ActionType.INSERT_LISTBOX_ITEMS,
                        data=self.current_listbox_template_internal_state[ListboxPageTemplateEnum.GEOMETRY].get(enum_key.value),
                        target=current_target_listbox)
                    )

    @property
    def show_geometry_button(self):
        return self._show_geometry_button
    
    @show_geometry_button.setter
    def show_geometry_button(self, value):
        self._show_geometry_button = value
        self._observable.notify_observers(Action(
            type=ActionType.TOGGLE_GEO_BUTTON_VISIBLE,
        data=value
        ))

    @property
    def allow_input_focus_out_logic(self):
        return self._allow_input_focus_out_logic

    @allow_input_focus_out_logic.setter
    def allow_input_focus_out_logic(self, value):
        logging.trace(f'store setter - set allow_input_focus_out_logic - {value}')
        self._allow_input_focus_out_logic = value

    # hidden widgets are tracked with their state to allow for re-showing 
    @property
    def hidden_widgets(self):
        return self._hidden_widgets

    @hidden_widgets.setter
    # dict of widgets by py id
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
    def current_listbox_template(self):
        return self._current_listbox_insert

    @current_listbox_template.setter
    def current_listbox_template(self, value):
        self._current_listbox_insert = value

    @property
    def listbox_templates(self):
        return self._listbox_templates

    @listbox_templates.setter
    def listbox_templates(self, value):
        self._listbox_templates = value
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
