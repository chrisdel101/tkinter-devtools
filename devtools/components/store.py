from __future__ import annotations
import logging
import tkinter as tk
from typing import Any

from devtools.components.observable import Action
from devtools.constants import ActionType, ListBoxEntryInputAction, ListboxManagerState, ListboxTemplateNotifyStateKey, ListboxPageTemplateEnum, TreeState, TreeStateKey
from typing import TYPE_CHECKING

from devtools.decorators import try_except_catcher

if TYPE_CHECKING:
    # ONLY for type checkers
    from devtools.components.widgets.config_listbox.ConfigListboxManager import ConfigListboxManager


class Store:
    @try_except_catcher
    def __init__(self, observable, **kwargs):
        self._observable = observable
        self.block_active_adding: bool = False # block add button during adding prevent multiple
        self.existing_combobox_wrappers: list[tk.Widget] | list = [] # store wrappers around all comboboxes to allow remove all
        self.devtools_window_in_focus: bool = True # tracking to trigger destroy state on devtools window focus out 
        self.tree_refresh_job = None # blocks tree rebuild while one is active
        self.tree_rebuild_in_progress: bool = False # guard to block re-entrant tree rebuild
        self.tree_rebuild_requested: bool = False # queue one extra rebuild when requested mid-rebuild
        self.key_combobox_popdown_open: bool = False # track when open to apply focus out destroy logic
        self.value_combobox_popdown_open: bool = False # track when open to apply focus out destroy logic
        self.show_unmapped_widgets = kwargs.get("show_unmapped_widgets", True) # toggle to omit unmappeed default shows anything in the code
        self.listbox_entry_input_action:   ListBoxEntryInputAction | None = None # sets type of input as create or update
        self.allow_input_focus_out_logic: bool = True # guard to allow subract/cancel focus out
        self.tree_state: TreeState = {
            TreeStateKey.SELECTED_ITEM_WIDGET.value: None,
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT.value: {},
            TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID.value: {}
        }
        self.listbox_templates: dict[ListboxPageTemplateEnum, ConfigListboxManager] = {} # store the listbox manager option or geometry
        self.current_listbox_template: ConfigListboxManager | None = None  # currrent template inserted as shown in the listbox
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
        } # store the state of the active template in the listbox 
        self.hidden_widgets = {} # store hidden state in case restored
        self.show_geometry_button = False # hides geometry button when widget has none
        self.row_shift = True # guard to toggle when row shift is applied
        self.tree_highlighted_widget: tk.Widget | None = None # track highlighted to remove highlight on next highlight or deselect
        self.tree_highlight_saved_config: dict | None = None # store original config to restore after highlight
        self.tree_highlight_overlay_edges: list[tk.Frame] = [] # overlay on top of widget to show highlight - stored to remove after
        self.tree_highlight_overlay_parent: tk.Misc | None = None # parent of overlay to lift after highlight
        self.tree_applying_highlight: bool = False # guard to block multiple highlight at once
        self.tree_store_widget_by_obj_mem_id: dict[int, dict[str, tk.Widget]] = {} # widget by mem id to find widgets

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
    def row_shift(self):
        return self._row_shift

    @row_shift.setter
    def row_shift(self, value):
        self._row_shift = value
        self._observable.notify_observers(Action(
            type=ActionType.TOGGLE_ROW_SHIFT,
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
    def tree_refresh_job(self):
        return self._tree_refresh_job

    @tree_refresh_job.setter
    def tree_refresh_job(self, value):
        self._tree_refresh_job = value

    @property
    def tree_rebuild_in_progress(self):
        return self._tree_rebuild_in_progress

    @tree_rebuild_in_progress.setter
    def tree_rebuild_in_progress(self, value):
        self._tree_rebuild_in_progress = value

    @property
    def tree_rebuild_requested(self):
        return self._tree_rebuild_requested

    @tree_rebuild_requested.setter
    def tree_rebuild_requested(self, value):
        self._tree_rebuild_requested = value


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

    @property
    def tree_highlighted_widget(self):
        return self._tree_highlighted_widget

    @tree_highlighted_widget.setter
    def tree_highlighted_widget(self, value):
        self._tree_highlighted_widget = value

    @property
    def tree_highlight_saved_config(self):
        return self._tree_highlight_saved_config

    @tree_highlight_saved_config.setter
    def tree_highlight_saved_config(self, value):
        self._tree_highlight_saved_config = value

    @property
    def tree_highlight_overlay_edges(self):
        return self._tree_highlight_overlay_edges

    @tree_highlight_overlay_edges.setter
    def tree_highlight_overlay_edges(self, value):
        self._tree_highlight_overlay_edges = value

    @property
    def tree_highlight_overlay_parent(self):
        return self._tree_highlight_overlay_parent

    @tree_highlight_overlay_parent.setter
    def tree_highlight_overlay_parent(self, value):
        self._tree_highlight_overlay_parent = value

    @property
    def tree_applying_highlight(self):
        return self._tree_applying_highlight

    @tree_applying_highlight.setter
    def tree_applying_highlight(self, value):
        self._tree_applying_highlight = value

    @property
    def tree_store_widget_by_obj_mem_id(self):
        return self._tree_store_widget_by_obj_mem_id

    @tree_store_widget_by_obj_mem_id.setter
    def tree_store_widget_by_obj_mem_id(self, value):
        self._tree_store_widget_by_obj_mem_id = value
