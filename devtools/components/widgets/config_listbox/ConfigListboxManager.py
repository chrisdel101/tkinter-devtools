from __future__ import annotations
import logging
import tkinter as tk
from tkinter import ttk
from typing import OrderedDict

from devtools.components.observable import Action, Observable
from devtools.components.store import ListboxManagerStateKey, Store
from devtools.constants import ActionType, ListBoxEntryInputAction, OptionBoxState, TreeStateKey
from devtools.decorators import toggle_block_focus_out_key_logic
from devtools.utils import Utils
from devtools.components.widgets.config_listbox.ConfigListboxUtils import ConfigListboxUtils
from devtools.style import Style

"""

Inside Left window of the devtools with config settings.
Allows editing of the selected item in the listbox.
https://stackoverflow.com/a/64611569/5972531

"""
class ConfigListboxManager(tk.Listbox, ConfigListboxUtils):

    def __init__(self, 
            master, 
            observable: Observable,
            store: Store,
            **styles
        ): 
        tk.Listbox.__init__(self, master=master, **Style.config_listbox_manager.get('listbox'))
        self._observable = observable
        self._store = store
        self._observable.register_observer(self)

        # self.scroll_bar = tk.Scrollbar(master, orient="vertical", command=self.yview)
        # self.config(yscrollcommand=self.scroll_bar.set)
        self.styles = styles

        self.bind("<Double-1>", self.start_update)
        # self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.option_box_state = OptionBoxState.CLOSED.value
        self.key_var = tk.StringVar()
        self.val_var = tk.StringVar()
        self.list_var = tk.Variable(value=[])
        self.value_box_wrapper = None
        self.key_box_wrapper = None
        # focus guard - blocks
        self.allow_focus_out_key_logic = True
        self.allow_focus_out_value_logic = True

    # use event x and y w tk index - get listbox item index
    def _get_index_from_event_coords(self, event):
        selected_index: int = self.index(f"@{event.x},{event.y}")
        return selected_index
    
    def start_update(self, event):
        # index of clicked item on list
        updating_item_index: int = self._get_index_from_event_coords(event)
        # extract starting values from list item
        full_txt_str = self.get(updating_item_index)
    
        changes_dict  = Utils.build_split_str_pairs_dict(full_txt_str, ":")
        self.handle_entry_input_update(
            index=updating_item_index, 
            changes_dict=changes_dict
        )
    # handle entry within an entry inside listbox
    # - pass in callback - used in multiple places w diff callbacks
    def insert_value_output_and_apply_to_page(
            self, 
            current_widget: tk.Entry | tk.OptionMenu, 
            key_entry_value: str,
            value_entry_value: str,
        ):
        # store the current y position in listbox  
        y0, _ = self.yview()
        # check for .get method  - use .get for new entry else val correct option box  
        value_entry_value = current_widget.get() if getattr(current_widget, 'get', None) else value_entry_value
         # delete data at current index and insert new data there
        self.delete_all_listbox_items()
        current_value_state_dict  = self._store.listbox_manager_state_get_value(ListboxManagerStateKey.CURRENT_VALUES_STATE)
        # overwrite current vals - doesn't allow dupes
        updated_value_state_dict = OrderedDict(sorted({**current_value_state_dict, key_entry_value: value_entry_value}.items()))
        self._store.listbox_manager_state_set(enum_key=ListboxManagerStateKey.CURRENT_VALUES_STATE, state_to_set=updated_value_state_dict)
        
        self.after_idle(lambda: self.yview_moveto(y0))
        # UPDATE THE PAGE WIDGET HERE
        self._observable.notify_observers(Action(type=ActionType.UPDATE_TREE_ITEM_TO_PAGE_WIDGET.name, data={
            'key': key_entry_value,
            'value': value_entry_value
        }))
        self.cancel_update_listbox(*self._store.existing_combobox_wrappers)
        self._store.block_active_adding = False
        self.allow_focus_out_key_logic = True
        # print("insert_value_output_and_apply_to_page block_active_adding FALSE")
        # return value_entry_value
    
    # @toggle_block_focus_out_key_logic
     # return and place value_option_box from key_option_box
    def handle_build_value_option_box_from_key_option_box(
        self,
        index: int, 
        key_option_box: ttk.Combobox, 
        value_inside: tk.StringVar, 
        item_option_vals_list: list[str]):
        value_option_box = self.build_value_option_box(
            index, 
            key_entry_widget=key_option_box, 
            key_entry_value=value_inside.get(),
            item_option_vals_list=item_option_vals_list)
            
        value_option_box.pack(fill='x')
        self.value_box_wrapper.place(relx=0.3, y=self._translate_y_coord(0), relwidth=0.5, width=-1)
        self.allow_focus_out_key_logic = True
        value_option_box.focus_set()
        self.allow_focus_out_key_logic = False

        self._set_selected_by_index(index)

    @toggle_block_focus_out_key_logic
    def handle_build_value_entry_from_key_entry(
            self,
            index: int, 
            key_entry_widget: tk.OptionMenu | tk.Entry, 
            key_entry_value: str, 
            value_entry_value: str,
            y_coord: int,
            **kwargs):
        self.value_box_wrapper = tk.Frame(self)
        value_entry = tk.Entry(self.value_box_wrapper, **self.styles['entry'])
        value_entry.insert(0, value_entry_value)
        value_entry.selection_from(0)
        value_entry.selection_to("end")
        value_entry.pack(fill='x')
        self.value_box_wrapper.place(relx=0.3, y=y_coord, relwidth=0.58, width=-1)
        self._store.add_existing_wrapper(self.value_box_wrapper)
        # set focus to value entry
        value_entry.focus_set()
        # set manually so curselect can access it on subract
        self._set_selected_by_index(index)
        value_entry.bind("<Return>", lambda e: 
            self.insert_value_output_and_apply_to_page(
            current_widget=e.widget, 
            index=index, 
            value_widget_to_destroy=e.widget, 
            key_widget_to_destroy=key_entry_widget,
            key_entry_value=key_entry_value,
            value_entry_value=value_entry_value
            )
        )
        
        if kwargs.get('entry_input_action') == ListBoxEntryInputAction.CREATE.value:
            value_entry.bind("<Escape>", lambda e: (
                self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT_INDEX.name, data=index)),
                self.cancel_update_listbox(e.widget, key_entry_widget, self.key_box_wrapper,), 
                print("escape entry create"),
                setattr(self._store, 'active_adding', False)))
        else:
            value_entry.bind("<Escape>", lambda e: (
                self.cancel_update_listbox(e.widget, key_entry_widget, self.key_box_wrapper,), 
                print("escape entry update"),
                setattr(self._store, 'active_adding', False)))
            value_entry.bind("<FocusOut>", lambda e: (
                self.cancel_update_listbox(e.widget, key_entry_widget, self.key_box_wrapper,), 
                print("focusout entry update"),
                setattr(self._store, 'active_adding', False)))
    # run funcs for entering row update - called from double click on row
    @toggle_block_focus_out_key_logic
    def handle_entry_input_update(
        self, 
        index: int, 
        changes_dict: dict = {}, 
    ):
        self._store.editting_item_index = index
        y_coord = self.bbox(index)[1]
        self.key_box_wrapper = tk.Frame(self)
        key_entry = tk.Entry(self.key_box_wrapper, **self.styles['entry'], **self.styles['key_entry'])
        # add the text from the item into the key_entry - just place it but dont allow focus
        key_entry.insert(0, changes_dict.get('key'))
        key_entry.selection_from(0)
        key_entry.selection_to("end")
        key_entry.pack(fill='x')
        self.key_box_wrapper.place(relx=0, y=y_coord, relwidth=0.5 or 1, width=-1)
        self._store.add_existing_wrapper(self.key_box_wrapper)

        item_option_vals_list: list[str] | None = self._get_config_value_options(changes_dict.get('key'))
        if item_option_vals_list:
            value_option_box = self.build_value_option_box(
            index=index,
            key_entry_widget=key_entry,
            key_entry_value=changes_dict.get('key'),
            item_option_vals_list=item_option_vals_list
            )
            value_option_box.pack(fill='x')
            self.value_box_wrapper.place(relx=0.3, y=self._translate_y_coord(index), relwidth=0.5, width=-1)
            self.allow_focus_out_key_logic = True
            value_option_box.focus_set()
            self.allow_focus_out_key_logic = False
        else:
            self.handle_build_value_entry_from_key_entry(
                index=index,
                key_entry_widget=key_entry,
                key_entry_value=changes_dict.get('key'),
                value_entry_value=changes_dict.get('value'),
                y_coord=y_coord
            )
    # run funcs for entering row add - called from parent on add button clicked parent when add button clicked
    # @toggle_block_focus_out_key_logic
    def handle_entry_input_create(
        self, 
        index: int):
        item_option_vals_list = None
        # store current editting index
        self._store.editting_item_index = index
        current_treeview_item = self._store.tree_state_get(TreeStateKey.SELECTED_ITEM)
        # use same stored state as listbox - already filtered extracted
        current_item_options_list = list(self._store.listbox_manager_state.get(ListboxManagerStateKey.CURRENT_VALUES_STATE.value).keys())
        key_option_box = self.build_key_option_box(
            index=index,
            item_option_vals_list=current_item_options_list
        )
        key_option_box.pack(fill='x')
        self.key_box_wrapper.place(relx=0, y=self._translate_y_coord(0), relwidth=0.5, width=-1)
        # move focus to key combo
        key_option_box.focus_set()
        # set manually so curselect can access it on subract
        self._set_selected_by_index(index)
        
    def notify(self, action: Action):
        Utils.dispatch_action(self, action)
