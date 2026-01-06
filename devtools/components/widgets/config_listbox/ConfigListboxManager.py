from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Any

from devtools.components.observable import Action, Observable
from devtools.components.store import ListboxInsertNotifyStateKey, Store
from devtools.constants import ActionType, ConfigOptionMapSetting, ConfigOptionValueTypeEnum, GeometryType, ListBoxEntryInputAction, ListboxPageInsertEnum, TreeStateKey
from devtools.decorators import block_allow_input_focus_out_logic, try_except_catcher
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
            listbox_page_insert_enum: ListboxPageInsertEnum,
            observable: Observable,
            store: Store,
            **styles
        ): 
        tk.Listbox.__init__(self, master=master, **Style.config_listbox_manager.get('listbox'))
        self.name = f"{listbox_page_insert_enum.name} listbox"
        self._observable: Observable = observable
        self._store: Store = store
        self._observable.register_observer(self)
        self._listbox_page_insert_enum: ListboxPageInsertEnum = listbox_page_insert_enum
        # self.scroll_bar = tk.Scrollbar(master, orient="vertical", command=self.yview)
        # self.config(yscrollcommand=self.scroll_bar.set)
        self.styles: dict = styles

        self.bind("<Double-1>", self.start_update)
        # self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_var: tk.Variable = tk.Variable(value=[])
        self.spinbox_var: tk.Variable = tk.IntVar(value=[])
        self.value_box_wrapper: tk.Frame | None = None
        self.spin_box_wrapper: tk.Frame | None = None
        self.key_box_wrapper: tk.Frame | None = None
            # focus guard - blocks

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
        config_setting_map = self.map_config_option_to_setting(changes_dict.get('key'))
        self.handle_entry_input_update(
            index=updating_item_index, 
            changes_dict=changes_dict,
            config_setting_map=config_setting_map
        )
    # handle entry within an entry inside listbox
    # - pass in callback - used in multiple places w diff callbacks
    @try_except_catcher
    def insert_value_output_and_apply_to_page(
            self, 
            value_entry_widget: tk.Entry | tk.OptionMenu, 
            key_entry_value: str,
            updated_option_value: str | int | float,
        ):
        # store the current y position in listbox  
        y0, _ = self.yview()
        # check for .get method  - use .get for new entry else val correct option box  
        value_entry_value = value_entry_widget.get() if getattr(value_entry_widget, 'get', None) else updated_option_value
         # delete data at current index and insert new data there
        self.delete_all_listbox_items()
        current_listbox_insert_widget = self._store.current_listbox_insert
        current_listbox_value_state_dict  = self._store.listbox_manager_state_get_value(ListboxInsertNotifyStateKey.CURRENT_VALUES_STATE)
        # overwrite current vals - stops duplicates from adding to listbox
        updated_value_state_sorted_dict = Utils.sorted_dict(Utils.merge_dicts(current_listbox_value_state_dict, {key_entry_value: value_entry_value}))
        self._store.listbox_manager_state_set(enum_key=ListboxInsertNotifyStateKey.CURRENT_VALUES_STATE, state_to_set=updated_value_state_sorted_dict)
        
        self.after_idle(lambda: self.yview_moveto(y0))
        # UPDATE THE PAGE WIDGETS HERE - calls tree 
        if self._listbox_page_insert_enum == ListboxPageInsertEnum.ATTRIBUTES:
            # run update_tree_item_to_page_widget_attr_config on widget.config
            self._observable.notify_observers(Action(type=ActionType.UPDATE_TREE_ITEM_TO_PAGE_WIDGET_ATTR_CONFIG, data={
                'key': key_entry_value,
                'value': value_entry_value
            }))
        else:
            # GEOMETRY UPDATE HANDLING
            geo_manager = self._store.tree_state.get(TreeStateKey.SELECTED_ITEM_WIDGET.value).winfo_manager()
            match geo_manager:
                case GeometryType.PACK.value:
                    self._observable.notify_observers(Action(type=ActionType.UPDATE_TREE_ITEM_TO_PAGE_WIDGET_PACK_CONFIG, data={
                        'key': key_entry_value,
                        'value': value_entry_value
                    }))
                case GeometryType.GRID.value:
                    self._observable.notify_observers(Action(type=ActionType.UPDATE_TREE_ITEM_TO_PAGE_WIDGET_GRID_CONFIG, data={
                        'key': key_entry_value,
                        'value': value_entry_value
                    }))
                case GeometryType.PLACE.value:       
                    self._observable.notify_observers(Action(type=ActionType.UPDATE_TREE_ITEM_TO_PAGE_WIDGET_PLACE_CONFIG, data={
                        'key': key_entry_value,
                        'value': value_entry_value
                    }))
        self.cancel_update_listbox(*self._store.existing_combobox_wrappers)
        self._store.block_active_adding = False
        self._store.allow_input_focus_out_logic = True
        
    @block_allow_input_focus_out_logic
    @try_except_catcher
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
            item_option_vals_list=item_option_vals_list
            )
            
        value_option_box.pack(fill='x')
        self.value_box_wrapper.place(relx=0.5, y=self.listbox_in_parent_y_coord(), relwidth=0.5, width=-1)
        self._store.add_existing_store_wrapper(self.value_box_wrapper)
        # self.allow_input_focus_out_logic = True
        value_option_box.focus_set()
        # self.allow_input_focus_out_logic = False

        self._set_selected_by_index(index)

    @block_allow_input_focus_out_logic
    @try_except_catcher
    # widget config options here do not have value mapping
    def handle_build_value_entry_from_key_entry(
            self,
            index: int, 
            key_entry_widget: ttk.Combobox | tk.Entry, 
            key_entry_value: str, 
            y_coord: int,
            current_option_val: Any,
            config_setting_map: ConfigOptionMapSetting | None=None,
            **kwargs):
        ''' 
        build value entry when output from key entry has no mapping options
        :param key_entry_widget: ttk.Combobox | tk.Entry
        :param key_entry_value: str
        - option value from key entry
        :param y_coord: int
        - bbox(index)[1] update; 0 on create
        :param current_option_val: str | None = None
        - value of current widget config option
        :param config_setting_map: ConfigOptionMapSetting | None=None
        - dict with type and values when options maps 
        '''
        # check  mapping for int type - spinbox
        if config_setting_map and config_setting_map.get("type") in (int, float):
            self.spin_box_wrapper = tk.Frame(self)
            spinbox = self.build_value_spin_box(
                key_entry_widget=key_entry_widget,
                key_entry_value=key_entry_value,  
                current_option_value=current_option_val,
                index=index
            )
            spinbox.pack(fill='x')
            self.spin_box_wrapper.place(relx=0.5, y=y_coord, relwidth=0.5, width=-1)
            self._store.add_existing_store_wrapper(self.spin_box_wrapper)
            # self.allow_input_focus_out_logic = True
            spinbox.focus_set()
        else:
            # no mapping or values - empty entry widget for value entry
            self.value_box_wrapper = tk.Frame(self)
            value_entry = tk.Entry(self.value_box_wrapper, **self.styles['entry'])
            # fill in entry with current val
            value_entry.insert(0, current_option_val)
            value_entry.selection_from(0)
            value_entry.selection_to("end")
            value_entry.pack(fill='x')
            self.value_box_wrapper.place(relx=0.5, y=y_coord,relwidth=0.5, width=-1)
            self._store.add_existing_store_wrapper(self.value_box_wrapper)
            # set focus to value entry
            value_entry.focus_set()
            # set manually so curselect can access it on subract
            self._set_selected_by_index(index)
            value_entry.bind("<Return>", lambda e: 
                self.insert_value_output_and_apply_to_page(
                value_entry_widget=e.widget, 
                key_entry_value=key_entry_value,
                updated_option_value=current_option_val
                )
            )
            if kwargs.get('entry_input_action') == ListBoxEntryInputAction.CREATE.value:
                value_entry.bind("<Escape>", lambda e: (
                    self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT_INDEX, data=index)),
                    self.cancel_update_listbox(*self._store.existing_combobox_wrappers), 
                    print("escape entry create"),
                    setattr(self._store, 'block_active_adding', False)))
                value_entry.bind("<FocusOut>", lambda e: (
                    self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT_INDEX, data=index)),
                    self.cancel_update_listbox(*self._store.existing_combobox_wrappers), 
                    setattr(self._store, 'block_active_adding', False)))
            else:
                value_entry.bind("<Escape>", lambda e: (
                    self.cancel_update_listbox(*self._store.existing_combobox_wrappers), 
                    print("escape entry update"),
                    setattr(self._store, 'block_active_adding', False)))
                value_entry.bind("<FocusOut>", lambda e: (
                    self.cancel_update_listbox(*self._store.existing_combobox_wrappers), 
                    print("focusout entry update"),
                    setattr(self._store, 'block_active_adding', False)))
    # run funcs for entering row update - called from double click on row
    @block_allow_input_focus_out_logic
    @try_except_catcher
    def handle_entry_input_update(
        self, 
        index: int, 
        config_setting_map: ConfigOptionMapSetting | None, 
        changes_dict: dict = {}, 
    ):
        self._store.listbox_entry_input_action = ListBoxEntryInputAction.UPDATE
        self._store.editting_item_index = index
        y_coord = self.bbox(index)[1]
        self.key_box_wrapper = tk.Frame(self)
        key_entry = tk.Entry(self.key_box_wrapper, **self.styles['entry'], **self.styles['key_entry'])
        # add the text from the item into the key_entry - just place it but dont allow focus
        key_entry.insert(0, changes_dict.get('key'))
        key_entry.selection_from(0)
        key_entry.selection_to("end")
        key_entry.pack(fill='x')
        self.key_box_wrapper.place(relx=0, y=y_coord, relwidth=0.5, width=-1)
        self._store.add_existing_store_wrapper(self.key_box_wrapper)
        item_attr_type: ConfigOptionValueTypeEnum = self.map_config_attr_to_setting_type(changes_dict.get('key'))
        # check mapping for int type - spinbox
        if config_setting_map and config_setting_map.get("type") == int or config_setting_map.get("type") == float:
            self.spin_box_wrapper = tk.Frame(self)
            spinbox = self.build_value_spin_box(
                key_entry_widget=key_entry,
                key_entry_value=changes_dict.get('key'),  
                current_option_value=changes_dict.get('value'),
                index=index
            )
            spinbox.pack(fill='x')
            self.spin_box_wrapper.place(relx=0.45, y=y_coord, relwidth=0.5, width=-1)
            self._store.add_existing_store_wrapper(self.spin_box_wrapper)
            # self.allow_input_focus_out_logic = True
            spinbox.focus_set()
        # check mapping for attribute config value options - combobox
        elif (item_attr_vals_list := config_setting_map and config_setting_map.get('values')):
            value_option_box = self.build_value_option_box(
            index=index,
            key_entry_widget=key_entry,
            key_entry_value=changes_dict.get('key'),
            item_option_vals_list=item_attr_vals_list
            )
            value_option_box.pack(fill='x')
            self.value_box_wrapper.place(relx=0.45, y=y_coord + self.listbox_in_parent_y_coord(), relwidth=0.5, width=-1)
            self._store.add_existing_store_wrapper(self.value_box_wrapper)
            # self.allow_input_focus_out_logic = True
            value_option_box.focus_set()
        else:
            # no mapping - entry
            self.handle_build_value_entry_from_key_entry(
                index=index,
                key_entry_widget=key_entry,
                key_entry_value=changes_dict.get('key'),
                y_coord=y_coord,
                current_option_val=changes_dict.get('value'),
            )
    # run funcs for entering row add - called from parent on add button clicked parent when add button clicked
    @try_except_catcher
    def handle_entry_input_create(
        self, 
        index: int):
        self._store.listbox_entry_input_action = ListBoxEntryInputAction.CREATE
        # store current editting index
        self._store.editting_item_index = index
        current_treeview_item = self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET)
        # using listbox state stored - already filtered/extracted
        page_insert = self._store.current_listbox_insert._listbox_page_insert_enum
        current_item_options_list = list(self._store.current_listbox_insert_internal_state.get(page_insert).get(ListboxInsertNotifyStateKey.CURRENT_VALUES_STATE.value).keys())
        key_option_box = self.build_key_option_box(
            index=index,
            item_option_vals_list=current_item_options_list
        )
        key_option_box.pack(fill='x')
        self.key_box_wrapper.place(relx=0, y=self.listbox_in_parent_y_coord(), relwidth=0.5, width=-1)
        self._store.add_existing_store_wrapper(self.key_box_wrapper)
        # move focus to key combo
        key_option_box.focus_set()
        # set manually so curselect can access it on subract
        self._set_selected_by_index(index)
        
    def notify(self, action: Action):
        Utils.dispatch_action(self, action)
